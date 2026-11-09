"""
ingest_transactions.py - every Yahoo transaction, every season: adds, drops,
waiver claims (with winning FAAB bid), trades (players and picks), commish
moves. All statuses are kept (vetoed trades included); filter on status.

Encoding (same as I Yearn): an add is one 'incoming' row, a drop is one
'outgoing' row, a trade is one 'incoming' row per player with the other side
in counterparty_team_season_id.

Run after ingest_league.py has committed.
    venv\\Scripts\\python.exe ingest_transactions.py
    venv\\Scripts\\python.exe ingest_transactions.py --commit
"""

from collections import Counter
from datetime import datetime

from wg_common import (as_list, base_args, call, dec, ensure_player, finish, get, guard_env,
                       open_db, parse_seasons, player_fields, print_delta, query_for,
                       seasons_from_db, table_counts, to_int, tsid)

TABLES = ["transactions", "transaction_players", "transaction_picks", "players"]


def ingest_one(conn, t, season, stats):
    ts = datetime.fromtimestamp(int(get(t, "timestamp"))).isoformat(sep=" ")
    ttype, status = dec(get(t, "type")), dec(get(t, "status"))
    bid = get(t, "faab_bid")
    bid = to_int(bid) if bid not in (None, "") else None
    conn.execute(
        """INSERT INTO transactions (yahoo_transaction_id, season, timestamp, event_type, status,
                                     faab_bid, trader_team_season_id, tradee_team_season_id)
           VALUES (?,?,?,?,?,?,?,?)
           ON CONFLICT(season, yahoo_transaction_id) DO UPDATE SET
             status=excluded.status, faab_bid=excluded.faab_bid, event_type=excluded.event_type,
             trader_team_season_id=excluded.trader_team_season_id,
             tradee_team_season_id=excluded.tradee_team_season_id""",
        (to_int(get(t, "transaction_id")), season, ts, ttype, status, bid,
         tsid(conn, season, get(t, "trader_team_key")), tsid(conn, season, get(t, "tradee_team_key"))))
    tid = conn.execute("SELECT transaction_id FROM transactions WHERE season=? AND yahoo_transaction_id=?",
                       (season, to_int(get(t, "transaction_id")))).fetchone()[0]
    stats["types"][ttype] += 1
    stats["status"][status] += 1

    for p in as_list(get(t, "players"), "player"):
        pid, name, pos, team = player_fields(p)
        ensure_player(conn, pid, name, pos, team)
        td = get(p, "transaction_data")
        if isinstance(td, list):       # some shapes wrap it in a list
            td = td[0] if td else None
        td = td.get("transaction_data", td) if isinstance(td, dict) else td
        kind = dec(get(td, "type"))
        src, dst = dec(get(td, "source_type")), dec(get(td, "destination_type"))
        if kind == "add":
            row = ("incoming", tsid(conn, season, get(td, "destination_team_key")), None)
        elif kind == "drop":
            row = ("outgoing", tsid(conn, season, get(td, "source_team_key")), None)
        elif kind == "trade":
            row = ("incoming", tsid(conn, season, get(td, "destination_team_key")),
                   tsid(conn, season, get(td, "source_team_key")))
        else:
            stats["skipped_moves"][kind] += 1
            continue
        conn.execute(
            """INSERT OR REPLACE INTO transaction_players
               (transaction_id, player_id, direction, team_season_id, source_type,
                destination_type, counterparty_team_season_id)
               VALUES (?,?,?,?,?,?,?)""",
            (tid, pid, row[0], row[1], src, dst, row[2]))
        stats["moves"] += 1

    for pk in as_list(get(t, "picks"), "pick"):
        conn.execute(
            """INSERT OR REPLACE INTO transaction_picks
               (transaction_id, draft_round, source_team_season_id,
                destination_team_season_id, original_team_season_id)
               VALUES (?,?,?,?,?)""",
            (tid, to_int(get(pk, "round")),
             tsid(conn, season, get(pk, "source_team_key")),
             tsid(conn, season, get(pk, "destination_team_key")),
             tsid(conn, season, get(pk, "original_team_key"))))
        stats["picks"] += 1


def main():
    args = base_args(__doc__).parse_args()
    guard_env()
    conn = open_db(args.commit, "ingest_transactions")
    if not conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]:
        raise SystemExit("teams table is empty. Run ingest_league.py --commit first.")
    all_seasons = seasons_from_db(conn)
    wanted = parse_seasons(args.seasons, [s for s, _, _ in all_seasons])
    before = table_counts(conn, TABLES)

    for season, gid, lid in all_seasons:
        if season not in wanted:
            continue
        try:
            txns = as_list(call(query_for(gid, lid).get_league_transactions), "transaction")
        except Exception as e:
            print(f"--- {season}: no transactions ({type(e).__name__})")
            continue
        stats = {"types": Counter(), "status": Counter(), "skipped_moves": Counter(), "moves": 0, "picks": 0}
        errors = 0
        for t in txns:
            try:
                ingest_one(conn, t, season, stats)
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"    ERROR txn {get(t, 'transaction_id', '?')}: {type(e).__name__}: {e}")
        types = ", ".join(f"{k} {v}" for k, v in stats["types"].most_common())
        non_ok = {k: v for k, v in stats["status"].items() if k != "successful"}
        print(f"--- {season}: {len(txns)} txns ({types}); {stats['moves']} player moves, "
              f"{stats['picks']} pick moves" + (f"; {errors} ERRORS" if errors else ""))
        if non_ok:
            print(f"    non-successful: {non_ok}")
        if stats["skipped_moves"]:
            print(f"    skipped player moves of unknown type: {dict(stats['skipped_moves'])}")

    print_delta(before, table_counts(conn, TABLES))
    finish(conn, args.commit)


if __name__ == "__main__":
    main()
