"""
verify_db.py - read-only health check of fantasy.db. Opens it read-only,
writes nothing. Run any time.

    venv\\Scripts\\python.exe verify_db.py
"""

import sqlite3

from wg_common import DB_PATH

PER_SEASON = ["teams", "draft_picks", "transactions", "team_standings", "matchups",
              "team_season_stats", "final_rosters", "player_weekly_stats"]


def main():
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    seasons = [r[0] for r in conn.execute("SELECT season FROM seasons ORDER BY season")]
    print("rows per season")
    print("  season " + " ".join(f"{t[:11]:>11}" for t in PER_SEASON))
    for s in seasons:
        cells = [conn.execute(f"SELECT COUNT(*) FROM {t} WHERE season=?", (s,)).fetchone()[0] for t in PER_SEASON]
        print(f"  {s}   " + " ".join(f"{c:>11}" for c in cells))

    print("\nmanagers")
    for name, n, first, last, pete in conn.execute(
            """SELECT m.canonical_name, COUNT(*), MIN(t.season), MAX(t.season), m.is_pete
               FROM managers m JOIN teams t USING(manager_id) GROUP BY m.manager_id
               ORDER BY MIN(t.season), m.canonical_name"""):
        print(f"  {name:<14} {n:>2} seasons  {first}-{last}" + ("  (you)" if pete else ""))

    print("\ntransaction types / statuses")
    for et, st, n in conn.execute("SELECT event_type, status, COUNT(*) FROM transactions "
                                  "GROUP BY 1, 2 ORDER BY 3 DESC"):
        print(f"  {et:<10} {st:<12} {n}")

    checks = {
        "players with placeholder names": "SELECT COUNT(*) FROM players WHERE player_name LIKE 'Player %'",
        "draft picks with no team": "SELECT COUNT(*) FROM draft_picks WHERE team_season_id IS NULL",
        "player moves with no team": "SELECT COUNT(*) FROM transaction_players WHERE team_season_id IS NULL",
        "matchups with no opponent": "SELECT COUNT(*) FROM matchups WHERE opponent_team_season_id IS NULL",
    }
    print("\nchecks (want 0, or close to it)")
    for label, q in checks.items():
        print(f"  {label:<34} {conn.execute(q).fetchone()[0]}")
    conn.close()


if __name__ == "__main__":
    main()
