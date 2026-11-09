"""
ingest_weekly_stats.py - every rostered player's fantasy points, every team,
every week, under league scoring, plus where he was slotted (QB/WR/BN/IR...).
The season's last week also fills final_rosters (with Yahoo's keeper flag),
so there is no separate roster script.

This is the big one: 12 teams x ~16 weeks x 17 seasons is about 3,400 Yahoo
calls, roughly 1.5 to 2 hours. So it behaves differently from the others:
  - Dry run samples one team, first and last week, per season. Enough to see
    that points and slots parse. Add --full to dry-run everything (slow).
  - --commit saves after every team-week, so you can stop it (Ctrl+C) and
    rerun; team-weeks already in the DB are skipped. --refresh re-pulls them.
  - The in-progress season only goes up to Yahoo's current week, and its
    latest two weeks are always re-pulled (catches Monday night points).
  - After the season ends, run once with --seasons <year> --refresh so the
    final weeks and final_rosters are complete.

    venv\\Scripts\\python.exe ingest_weekly_stats.py --seasons 2025
    venv\\Scripts\\python.exe ingest_weekly_stats.py --seasons 2025 --commit
    venv\\Scripts\\python.exe ingest_weekly_stats.py --commit          (all seasons)
"""

from wg_common import (as_list, base_args, call, dec, ensure_player, finish, get, guard_env,
                       now_str, open_db, parse_seasons, player_fields, print_delta, query_for,
                       seasons_from_db, table_counts, to_float, to_int)

TABLES = ["player_weekly_stats", "final_rosters", "players"]


def team_week(conn, q, season, team, yid, wk, is_final, now):
    res = call(q.get_team_roster_player_stats_by_week, yid, wk)
    players = res if isinstance(res, list) else as_list(get(res, "players"), "player")
    n = 0
    for p in as_list(players, "player"):
        pid, name, pos, nfl = player_fields(p)
        ensure_player(conn, pid, name, pos, nfl)
        sel = get(p, "selected_position")
        slot = dec(get(sel, "position")) if sel is not None else None
        pts = to_float(get(get(p, "player_points"), "total"))
        conn.execute(
            """INSERT INTO player_weekly_stats (season, week, player_id, team_season_id,
                                                selected_position, fantasy_points, fetched_at)
               VALUES (?,?,?,?,?,?,?)
               ON CONFLICT(season, week, player_id) DO UPDATE SET
                 team_season_id=excluded.team_season_id, selected_position=excluded.selected_position,
                 fantasy_points=excluded.fantasy_points, fetched_at=excluded.fetched_at""",
            (season, wk, pid, team, slot, pts, now))
        if is_final:
            k = get(p, "is_keeper") or {}
            kept = 1 if (k.get("kept") if isinstance(k, dict) else get(k, "kept")) else 0
            conn.execute(
                """INSERT INTO final_rosters (season, team_season_id, player_id, week,
                                              selected_position, is_keeper_yahoo)
                   VALUES (?,?,?,?,?,?)
                   ON CONFLICT(season, team_season_id, player_id) DO UPDATE SET
                     week=excluded.week, selected_position=excluded.selected_position,
                     is_keeper_yahoo=excluded.is_keeper_yahoo""",
                (season, team, pid, wk, slot, kept))
        n += 1
    return n


def main():
    p = base_args(__doc__)
    p.add_argument("--refresh", action="store_true", help="re-pull team-weeks already loaded")
    p.add_argument("--full", action="store_true", help="dry run every team-week instead of a sample")
    args = p.parse_args()
    guard_env()
    conn = open_db(args.commit, "ingest_weekly_stats")
    all_seasons = seasons_from_db(conn)
    wanted = parse_seasons(args.seasons, [s for s, _, _ in all_seasons])
    before = table_counts(conn, TABLES)
    sample = not args.commit and not args.full
    if sample:
        print("Sampling: first team, first and last week of each season. --full for everything.\n")

    try:
        for season, gid, lid in all_seasons:
            if season not in wanted:
                continue
            sw, ew, done = conn.execute(
                "SELECT start_week, end_week, is_finished FROM seasons WHERE season=?", (season,)).fetchone()
            if not ew:
                raise SystemExit(f"{season} has no end_week. Run ingest_league.py --commit first.")
            q = query_for(gid, lid)
            last = ew
            if not done:
                cur = to_int(get(call(q.get_league_metadata), "current_week")) or ew
                last = min(ew, cur)
            weeks = list(range(sw or 1, last + 1))
            if not weeks:
                print(f"--- {season}: no weeks played yet")
                continue
            teams = conn.execute("SELECT team_season_id, yahoo_team_id FROM teams WHERE season=? "
                                 "ORDER BY yahoo_team_id", (season,)).fetchall()
            if sample:
                teams, weeks = teams[:1], sorted({weeks[0], weeks[-1]})
            print(f"--- {season}: {len(teams)} teams x {len(weeks)} weeks (wk {weeks[0]}-{weeks[-1]})")
            rows = skipped = 0
            for team, yid in teams:
                for wk in weeks:
                    loaded = conn.execute("SELECT 1 FROM player_weekly_stats WHERE season=? AND week=? "
                                          "AND team_season_id=? LIMIT 1", (season, wk, team)).fetchone()
                    # Re-pull the last two weeks of an in-progress season. The current week is
                    # partial, and the week before can be missing Monday night if it was
                    # loaded before the game ended.
                    always = (not done and wk >= last - 1)
                    if loaded and not args.refresh and not always:
                        skipped += 1
                        continue
                    try:
                        rows += team_week(conn, q, season, team, yid, wk, bool(done) and wk == ew, now_str())
                    except Exception as e:
                        print(f"    team {yid} wk {wk}: FAILED {type(e).__name__}: {e}")
                    if args.commit:
                        conn.commit()
                print(f"    team {yid:>2}: done ({rows} player-weeks so far)")
            print(f"    {rows} player-week rows" + (f", {skipped} team-weeks already loaded" if skipped else ""))
    except KeyboardInterrupt:
        print("\nStopped. Everything up to the last finished team-week is saved (in commit mode). Rerun to resume.")

    if sample:
        r = conn.execute("""SELECT p.player_name, s.selected_position, s.fantasy_points, s.season, s.week
                            FROM player_weekly_stats s JOIN players p USING(player_id)
                            ORDER BY s.fantasy_points DESC LIMIT 5""").fetchall()
        print("\nTop 5 sampled scores (eyeball against Yahoo):")
        for name, slot, pts, s, w in r:
            print(f"  {s} wk {w:>2}  {name:<24} {slot or '?':<4} {pts}")
    print_delta(before, table_counts(conn, TABLES))
    finish(conn, args.commit)


if __name__ == "__main__":
    main()
