"""
ingest_results.py - final standings and every weekly head-to-head score.

team_standings: one row per team per season (rank, seed, W-L-T, PF, PA).
matchups: one row per team per week (two per game), with playoff and
consolation flags. Weeks come from seasons.start_week/end_week, which
ingest_league.py fills.

About 17 calls per season. Run after ingest_league.py has committed.
    venv\\Scripts\\python.exe ingest_results.py
    venv\\Scripts\\python.exe ingest_results.py --commit
"""

from wg_common import (as_list, base_args, call, dec, finish, get, guard_env, now_str, open_db,
                       parse_seasons, print_delta, query_for, seasons_from_db, table_counts,
                       to_float, to_int, tsid)

TABLES = ["team_standings", "matchups"]


def standings(conn, q, season, now):
    st = call(q.get_league_standings)
    n = 0
    for t in as_list(get(st, "teams"), "team"):
        ts = get(t, "team_standings")
        ot = get(ts, "outcome_totals")
        team = tsid(conn, season, get(t, "team_key"))
        if team is None:
            continue
        conn.execute(
            """INSERT INTO team_standings (season, team_season_id, rank, playoff_seed, wins, losses,
                                           ties, points_for, points_against, fetched_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(season, team_season_id) DO UPDATE SET
                 rank=excluded.rank, playoff_seed=excluded.playoff_seed, wins=excluded.wins,
                 losses=excluded.losses, ties=excluded.ties, points_for=excluded.points_for,
                 points_against=excluded.points_against, fetched_at=excluded.fetched_at""",
            (season, team, to_int(get(ts, "rank")), to_int(get(ts, "playoff_seed")),
             to_int(get(ot, "wins")), to_int(get(ot, "losses")), to_int(get(ot, "ties")),
             to_float(get(ts, "points_for")), to_float(get(ts, "points_against")), now))
        n += 1
    return n


def week(conn, q, season, wk, now):
    n = 0
    for m in as_list(call(q.get_league_matchups_by_week, wk), "matchup"):
        teams = as_list(get(m, "teams"), "team")
        if len(teams) < 2:
            continue
        winner = dec(get(m, "winner_team_key"))
        info = []
        for t in teams:
            tp, tpp = get(t, "team_points"), get(t, "team_projected_points")
            info.append((dec(get(t, "team_key")), to_float(get(tp, "total")), to_float(get(tpp, "total"))))
        for i, (tk, pts, proj) in enumerate(info):
            opp_tk, opp_pts, _ = info[1 - i]
            team = tsid(conn, season, tk)
            if team is None:
                continue
            conn.execute(
                """INSERT INTO matchups (season, week, team_season_id, points, projected_points,
                                         opponent_team_season_id, opponent_points, is_playoffs,
                                         is_consolation, is_tied, is_winner, status, fetched_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(season, week, team_season_id) DO UPDATE SET
                     points=excluded.points, projected_points=excluded.projected_points,
                     opponent_team_season_id=excluded.opponent_team_season_id,
                     opponent_points=excluded.opponent_points, is_playoffs=excluded.is_playoffs,
                     is_consolation=excluded.is_consolation, is_tied=excluded.is_tied,
                     is_winner=excluded.is_winner, status=excluded.status, fetched_at=excluded.fetched_at""",
                (season, wk, team, pts, proj, tsid(conn, season, opp_tk), opp_pts,
                 to_int(get(m, "is_playoffs")) or 0, to_int(get(m, "is_consolation")) or 0,
                 to_int(get(m, "is_tied")), (1 if tk == winner else 0) if winner else None,
                 dec(get(m, "status")), now))
            n += 1
    return n


def main():
    args = base_args(__doc__).parse_args()
    guard_env()
    conn = open_db(args.commit, "ingest_results")
    all_seasons = seasons_from_db(conn)
    wanted = parse_seasons(args.seasons, [s for s, _, _ in all_seasons])
    before = table_counts(conn, TABLES)
    now = now_str()

    for season, gid, lid in all_seasons:
        if season not in wanted:
            continue
        sw, ew, cur = conn.execute("SELECT start_week, end_week, is_finished FROM seasons WHERE season=?",
                                   (season,)).fetchone()
        if not ew:
            raise SystemExit(f"{season} has no end_week. Run ingest_league.py --commit first.")
        q = query_for(gid, lid)
        try:
            ns = standings(conn, q, season, now)
        except Exception as e:
            ns = f"unavailable ({type(e).__name__})"
        rows, failed = 0, []
        for wk in range(sw or 1, ew + 1):
            try:
                rows += week(conn, q, season, wk, now)
            except Exception as e:
                failed.append(wk)
        print(f"--- {season}: standings {ns} teams; matchups {rows} team-weeks (wk {sw}-{ew})"
              + (f"; weeks failed {failed}" if failed else ""))

    print_delta(before, table_counts(conn, TABLES))
    finish(conn, args.commit)


if __name__ == "__main__":
    main()
