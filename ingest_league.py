"""
ingest_league.py - season settings, teams, managers and team season counters
(moves, trades, FAAB balance) for every We Graduated season.

Managers are the hard part. They link one person's 17 seasons together, and
Yahoo may hide manager guids. Resolution order for each (season, team):
  1. manager_map.json "by_team"  {"2015:3": "Jeff"}       (explicit, wins)
  2. manager_map.json "by_guid"  {"<guid>": "Jeff"}
  3. manager_map.json "by_nickname" {"jeffrey": "Jeff"}
  4. automatic: same real guid = same person, named by his latest nickname;
     if the guid is hidden, the Yahoo nickname is used instead.
Anything still unresolved, or two teams in one season landing on the same
manager, blocks --commit.

Every run (dry or commit) writes two review files, nothing else:
  manager_review.txt          who we think is who, season by season
  manager_map.template.json   a full by_team map pre-filled with the
                              automatic answer. Fix any names, save it as
                              manager_map.json, rerun.

    venv\\Scripts\\python.exe ingest_league.py
    venv\\Scripts\\python.exe ingest_league.py --commit
"""

import json
from collections import Counter, defaultdict

from wg_common import (HERE, as_list, base_args, call, dec, finish, get, guard_env,
                       now_str, open_db, parse_seasons, print_delta, query_for,
                       seasons_from_db, table_counts, to_int, unwrap)

MAP_PATH = HERE / "manager_map.json"
TEMPLATE_PATH = HERE / "manager_map.template.json"
REVIEW_PATH = HERE / "manager_review.txt"
HIDDEN_RAW = {None, "", "--hidden--", "-- hidden --"}


class _Hidden:
    """Yahoo masks identities as '--hidden--' or '-- hidden --' (spacing varies)."""
    def __contains__(self, v):
        return v in HIDDEN_RAW or (isinstance(v, str) and v.replace(" ", "").lower() == "--hidden--")


HIDDEN = _Hidden()
TABLES = ["seasons", "managers", "teams", "team_season_stats"]


def pull_season(season, gid, lid):
    q = query_for(gid, lid)
    meta = call(q.get_league_metadata)
    settings = call(q.get_league_settings)
    teams = call(q.get_league_teams)
    srow = {
        "start_week": to_int(get(meta, "start_week")),
        "end_week": to_int(get(meta, "end_week")),
        "is_finished": to_int(get(meta, "is_finished")),
        "playoff_start_week": to_int(get(settings, "playoff_start_week")),
        "num_playoff_teams": to_int(get(settings, "num_playoff_teams")),
        "uses_faab": to_int(get(settings, "uses_faab")),
        "waiver_type": dec(get(settings, "waiver_type")),
        "trade_ratify_type": dec(get(settings, "trade_ratify_type")),
        "draft_type": dec(get(settings, "draft_type")),
    }
    rows = []
    for t in as_list(teams, "team"):
        mgrs = as_list(get(t, "managers"), "manager")
        # co-managed teams: prefer the non-comanager entry
        m = next((x for x in mgrs if not to_int(get(x, "is_comanager"))), mgrs[0] if mgrs else {})
        rows.append({
            "season": season,
            "team_id": to_int(get(t, "team_id")),
            "team_name": dec(get(t, "name")) or f"Team {get(t, 'team_id')}",
            "guid": dec(get(m, "guid")),
            "nickname": dec(get(m, "nickname")),
            "is_current_login": to_int(get(m, "is_current_login")) or 0,
            "is_commissioner": to_int(get(m, "is_commissioner")) or 0,
            "n_managers": len(mgrs),
            "draft_position": to_int(get(t, "draft_position")),
            "moves": to_int(get(t, "number_of_moves")),
            "trades": to_int(get(t, "number_of_trades")),
            "faab_balance": to_int(get(t, "faab_balance")),
        })
    return srow, rows


def resolve(rows, mp):
    by_team = mp.get("by_team", {})
    by_guid = mp.get("by_guid", {})
    by_nick = {k.lower(): v for k, v in mp.get("by_nickname", {}).items()}

    # Automatic groups: real guid first, else nickname.
    def auto_key(r):
        if r["guid"] not in HIDDEN:
            return f"guid:{r['guid']}"
        if r["nickname"] not in HIDDEN:
            return f"nick:{r['nickname'].lower()}"
        return None

    latest_nick = {}
    for r in sorted(rows, key=lambda r: r["season"]):
        k = auto_key(r)
        if k and r["nickname"] not in HIDDEN:
            latest_nick[k] = r["nickname"]

    for r in rows:
        tk = f"{r['season']}:{r['team_id']}"
        if by_team.get(tk):
            r["manager"], r["how"] = by_team[tk], "map:team"
        elif r["guid"] not in HIDDEN and by_guid.get(r["guid"]):
            r["manager"], r["how"] = by_guid[r["guid"]], "map:guid"
        elif r["nickname"] not in HIDDEN and by_nick.get(r["nickname"].lower()):
            r["manager"], r["how"] = by_nick[r["nickname"].lower()], "map:nickname"
        else:
            k = auto_key(r)
            r["manager"] = latest_nick.get(k) if k else None
            r["how"] = ("auto:guid" if k and k.startswith("guid") else "auto:nickname") if r["manager"] else "UNRESOLVED"

    problems = []
    unresolved = [r for r in rows if not r["manager"]]
    if unresolved:
        problems.append(f"{len(unresolved)} team-season(s) have no manager (hidden guid and nickname).")
    for s in sorted({r["season"] for r in rows}):
        c = Counter(r["manager"] for r in rows if r["season"] == s and r["manager"])
        for name, n in c.items():
            if n > 1:
                problems.append(f"{s}: '{name}' is assigned to {n} teams.")
    # Same display name reached from two different real guids = two people, one name.
    guids_per_name = defaultdict(set)
    for r in rows:
        if r["manager"] and r["guid"] not in HIDDEN:
            guids_per_name[r["manager"]].add(r["guid"])
    for name, gs in guids_per_name.items():
        if len(gs) > 1:
            problems.append(f"'{name}' covers {len(gs)} different Yahoo accounts. Two people, or one person "
                            "with two accounts? Set by_team entries to split or confirm.")
    return problems


def write_review(rows, problems):
    hidden = sum(1 for r in rows if r["guid"] in HIDDEN)
    lines = [f"Manager review ({len(rows)} team-seasons; {hidden} with hidden guid)", ""]
    if problems:
        lines += ["PROBLEMS (block --commit):"] + [f"  - {p}" for p in problems] + [""]
    by_mgr = defaultdict(list)
    for r in rows:
        by_mgr[r["manager"] or "?? UNRESOLVED"].append(r)
    for name in sorted(by_mgr, key=lambda n: (n.startswith("??"), n.lower())):
        rs = sorted(by_mgr[name], key=lambda r: r["season"])
        pete = "  [this is you]" if any(r["is_current_login"] for r in rs) else ""
        lines.append(f"{name}  ({len(rs)} seasons){pete}")
        for r in rs:
            g = "hidden" if r["guid"] in HIDDEN else f"...{r['guid'][-6:]}"
            lines.append(f"    {r['season']}  team {r['team_id']:>2}  {r['team_name']:<32} "
                         f"nick={r['nickname']!r:<20} guid={g:<10} via {r['how']}")
        lines.append("")
    REVIEW_PATH.write_text("\n".join(lines), encoding="utf-8")
    template = {
        "_how_to_use": "Fix any wrong names below, save this file as manager_map.json, rerun ingest_league.py. "
                       "Use the short names the league uses (Pete, Credit, Joel N...).",
        "by_team": {f"{r['season']}:{r['team_id']}": r["manager"] or ""
                    for r in sorted(rows, key=lambda r: (r["season"], r["team_id"]))},
        "by_guid": {},
        "by_nickname": {},
    }
    TEMPLATE_PATH.write_text(json.dumps(template, indent=2), encoding="utf-8")


def write_db(conn, season_rows, rows):
    now = now_str()
    for season, s in season_rows.items():
        conn.execute(
            """UPDATE seasons SET start_week=?, end_week=?, is_finished=?, playoff_start_week=?,
                   num_playoff_teams=?, uses_faab=?, waiver_type=?, trade_ratify_type=?, draft_type=?
               WHERE season=?""",
            (s["start_week"], s["end_week"], s["is_finished"], s["playoff_start_week"],
             s["num_playoff_teams"], s["uses_faab"], s["waiver_type"], s["trade_ratify_type"],
             s["draft_type"], season))

    # guid stored on the manager only if exactly one real guid maps to him
    guids = defaultdict(set)
    for r in rows:
        if r["guid"] not in HIDDEN:
            guids[r["manager"]].add(r["guid"])
    latest = {}
    for r in sorted(rows, key=lambda r: r["season"]):
        latest[r["manager"]] = r
    for name, r in latest.items():
        g = next(iter(guids[name])) if len(guids[name]) == 1 else None
        is_pete = 1 if any(x["is_current_login"] for x in rows if x["manager"] == name) else 0
        conn.execute("INSERT OR IGNORE INTO managers (canonical_name) VALUES (?)", (name,))
        conn.execute("UPDATE managers SET yahoo_guid=COALESCE(?, yahoo_guid), latest_nickname=?, is_pete=? "
                     "WHERE canonical_name=?", (g, r["nickname"], is_pete, name))

    for r in rows:
        mid = conn.execute("SELECT manager_id FROM managers WHERE canonical_name=?", (r["manager"],)).fetchone()[0]
        conn.execute(
            """INSERT INTO teams (season, yahoo_team_id, team_name, manager_id, yahoo_nickname,
                                  yahoo_guid_raw, is_commissioner, draft_position)
               VALUES (?,?,?,?,?,?,?,?)
               ON CONFLICT(season, yahoo_team_id) DO UPDATE SET
                 team_name=excluded.team_name, manager_id=excluded.manager_id,
                 yahoo_nickname=excluded.yahoo_nickname, yahoo_guid_raw=excluded.yahoo_guid_raw,
                 is_commissioner=excluded.is_commissioner, draft_position=excluded.draft_position""",
            (r["season"], r["team_id"], r["team_name"], mid, r["nickname"], r["guid"],
             r["is_commissioner"], r["draft_position"]))
        ts = conn.execute("SELECT team_season_id FROM teams WHERE season=? AND yahoo_team_id=?",
                          (r["season"], r["team_id"])).fetchone()[0]
        conn.execute(
            """INSERT INTO team_season_stats (season, team_season_id, number_of_moves,
                                              number_of_trades, faab_balance, fetched_at)
               VALUES (?,?,?,?,?,?)
               ON CONFLICT(season, team_season_id) DO UPDATE SET
                 number_of_moves=excluded.number_of_moves, number_of_trades=excluded.number_of_trades,
                 faab_balance=excluded.faab_balance, fetched_at=excluded.fetched_at""",
            (r["season"], ts, r["moves"], r["trades"], r["faab_balance"], now))


def main():
    args = base_args(__doc__).parse_args()
    guard_env()
    conn = open_db(args.commit, "ingest_league")
    all_seasons = seasons_from_db(conn)
    wanted = parse_seasons(args.seasons, [s for s, _, _ in all_seasons])
    before = table_counts(conn, TABLES)

    season_rows, rows = {}, []
    for season, gid, lid in all_seasons:
        if season not in wanted:
            continue
        print(f"--- {season} (game {gid}, league {lid})")
        srow, trows = pull_season(season, gid, lid)
        season_rows[season] = srow
        rows.extend(trows)
        hidden = sum(1 for r in trows if r["guid"] in HIDDEN)
        print(f"    {len(trows)} teams, {hidden} hidden guids, weeks {srow['start_week']}-{srow['end_week']}, "
              f"playoffs from wk {srow['playoff_start_week']} ({srow['num_playoff_teams']} teams), "
              f"faab={srow['uses_faab']}")

    mp = json.loads(MAP_PATH.read_text(encoding="utf-8")) if MAP_PATH.exists() else {}
    problems = resolve(rows, mp)
    write_review(rows, problems)
    names = sorted({r["manager"] for r in rows if r["manager"]}, key=str.lower)
    print(f"\n{len(names)} distinct managers: {', '.join(names)}")
    print(f"Wrote {REVIEW_PATH.name} and {TEMPLATE_PATH.name}. Read the review before committing.")

    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print(f"  - {p}")
        if args.commit:
            conn.close()
            raise SystemExit("\nABORTED: nothing written. Fix via manager_map.json and rerun.")
        print("(dry run continues so you can see the counts; --commit will refuse until these are fixed)")
        rows = [r for r in rows if r["manager"]]

    write_db(conn, season_rows, rows)
    print_delta(before, table_counts(conn, TABLES))
    finish(conn, args.commit)


if __name__ == "__main__":
    main()
