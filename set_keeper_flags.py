"""
set_keeper_flags.py - mark keepers in draft_picks.

League rule: each team's (up to) 6 keepers occupy the LAST 6 rounds of the
draft. Normally rounds 10-15; in 2020 (16 rounds, extra COVID bench spot)
rounds 11-16. Verified 2026-11-09 against prior-season final rosters: keeper
rounds match 11-12 of 12 per round every season; misses are off-season
trades Yahoo did not record and John inheriting Brad's team in 2019.

Sets draft_picks.is_keeper = 1 for the last 6 rounds, 0 otherwise.
Also writes keeper_exceptions.csv: keepers who were NOT on that manager's
prior-season final roster (evidence of unrecorded off-season trades), for
the pick/trade ledger work later. 2012 has no prior season loaded, so its
keepers are flagged by rule but not cross-checked.

    venv\\Scripts\\python.exe set_keeper_flags.py
    venv\\Scripts\\python.exe set_keeper_flags.py --commit
"""

import csv

from wg_common import HERE, base_args, finish, guard_env, open_db, parse_seasons, seasons_from_db

KEEPER_ROUNDS = 6


def main():
    args = base_args(__doc__).parse_args()
    guard_env()
    conn = open_db(args.commit, "set_keeper_flags")
    all_seasons = [s for s, _, _ in seasons_from_db(conn)]
    wanted = parse_seasons(args.seasons, all_seasons)
    exceptions = []

    for s in wanted:
        last = conn.execute("SELECT MAX(draft_round) FROM draft_picks WHERE season=?", (s,)).fetchone()[0]
        if not last:
            continue
        first_keeper = last - KEEPER_ROUNDS + 1
        conn.execute("UPDATE draft_picks SET is_keeper = CASE WHEN draft_round >= ? THEN 1 ELSE 0 END "
                     "WHERE season=?", (first_keeper, s))
        per_team = conn.execute("""SELECT COUNT(*) FROM draft_picks WHERE season=? AND is_keeper=1
                                   GROUP BY team_season_id""", (s,)).fetchall()
        counts = sorted({n for (n,) in per_team})
        rows = conn.execute("""
            SELECT d.draft_round, v.manager, p.player_name,
                   (SELECT w.manager FROM final_rosters f JOIN v_team_seasons w USING(team_season_id)
                     WHERE f.season=? AND f.player_id=d.player_id) AS prior_owner
            FROM draft_picks d JOIN v_team_seasons v USING(team_season_id) JOIN players p USING(player_id)
            WHERE d.season=? AND d.is_keeper=1""", (s - 1, s)).fetchall()
        has_prior = conn.execute("SELECT COUNT(*) FROM final_rosters WHERE season=?", (s - 1,)).fetchone()[0]
        miss = [r for r in rows if has_prior and r[3] != r[1]]
        for rnd, mgr, name, prior in miss:
            exceptions.append((s, rnd, mgr, name, prior or "(not on any final roster)"))
        check = f"{len(rows) - len(miss)}/{len(rows)} on own prior roster" if has_prior else "no prior season to check"
        print(f"--- {s}: keeper rounds {first_keeper}-{last}, {len(rows)} keepers, "
              f"per team {counts}, {check}")

    out = HERE / "keeper_exceptions.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["season", "round", "kept_by", "player", "prior_season_owner"])
        w.writerows(exceptions)
    print(f"\n{len(exceptions)} keepers not on their manager's prior roster -> {out.name}")
    print("(expected: off-season trades Yahoo missed, plus team handoffs like Brad -> John in 2019)")
    finish(conn, args.commit)


if __name__ == "__main__":
    main()
