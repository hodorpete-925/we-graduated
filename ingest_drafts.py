"""
ingest_drafts.py - every season's draft results into draft_picks.

pick_in_round uses that season's team count. Yahoo's draft results carry no
player names, so new players land as "Player <id>" placeholders; the
transaction, roster and weekly-stat loads fill real names in later.
is_keeper is left NULL on purpose (keeper logic comes later).

Run after ingest_league.py has committed (needs the teams table).
    venv\\Scripts\\python.exe ingest_drafts.py
    venv\\Scripts\\python.exe ingest_drafts.py --commit
"""

from collections import Counter

from wg_common import (as_list, base_args, call, dec, ensure_player, finish, get, guard_env,
                       open_db, parse_seasons, print_delta, query_for, seasons_from_db,
                       table_counts, to_int, tsid)

TABLES = ["draft_picks", "players"]


def main():
    args = base_args(__doc__).parse_args()
    guard_env()
    conn = open_db(args.commit, "ingest_drafts")
    if not conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]:
        raise SystemExit("teams table is empty. Run ingest_league.py --commit first.")
    all_seasons = seasons_from_db(conn)
    wanted = parse_seasons(args.seasons, [s for s, _, _ in all_seasons])
    before = table_counts(conn, TABLES)

    for season, gid, lid in all_seasons:
        if season not in wanted:
            continue
        n_teams = conn.execute("SELECT num_teams FROM seasons WHERE season=?", (season,)).fetchone()[0] or 12
        try:
            results = as_list(call(query_for(gid, lid).get_league_draft_results), "draft_result")
        except Exception as e:
            print(f"--- {season}: no draft results ({type(e).__name__})")
            continue
        ok = skipped = unmapped = 0
        rounds = Counter()
        for d in results:
            pk = dec(get(d, "player_key"))
            if not pk:
                skipped += 1           # empty slot (pre-draft)
                continue
            overall, rnd = to_int(get(d, "pick")), to_int(get(d, "round"))
            team = tsid(conn, season, get(d, "team_key"))
            if team is None:
                unmapped += 1
            pid = int(str(pk).split(".")[-1])
            ensure_player(conn, pid)
            conn.execute(
                """INSERT INTO draft_picks (season, overall_pick, draft_round, pick_in_round,
                                            team_season_id, player_id, cost_yahoo, is_keeper)
                   VALUES (?,?,?,?,?,?,?,NULL)
                   ON CONFLICT(season, overall_pick) DO UPDATE SET
                     draft_round=excluded.draft_round, pick_in_round=excluded.pick_in_round,
                     team_season_id=excluded.team_season_id, player_id=excluded.player_id,
                     cost_yahoo=excluded.cost_yahoo""",
                (season, overall, rnd, ((overall - 1) % n_teams) + 1, team, pid,
                 to_int(get(d, "cost"))))
            rounds[rnd] += 1
            ok += 1
        extra = f", {skipped} empty slots" if skipped else ""
        warn = f", {unmapped} picks with an unknown team" if unmapped else ""
        print(f"--- {season}: {ok} picks, {len(rounds)} rounds{extra}{warn}")
        odd = {r: n for r, n in rounds.items() if n != n_teams}
        if odd:
            print(f"    rounds without exactly {n_teams} picks: {odd}")

    print_delta(before, table_counts(conn, TABLES))
    ph = conn.execute("SELECT COUNT(*) FROM players WHERE player_name LIKE 'Player %'").fetchone()[0]
    print(f"  players still named as placeholders: {ph} (later loads fill these)")
    finish(conn, args.commit)


if __name__ == "__main__":
    main()
