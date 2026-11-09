"""
create_database.py - build an empty We Graduated fantasy.db from schema.sql,
with one seasons row per entry in league_chain.json (written by the probe).

Dry run (default): builds the schema in memory and prints the seasons.
--commit: creates fantasy.db. Refuses if it already exists.

    venv\\Scripts\\python.exe create_database.py
    venv\\Scripts\\python.exe create_database.py --commit
"""

import argparse
import sqlite3
import sys

from wg_common import DB_PATH, HERE, guard_env, load_chain


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--commit", action="store_true")
    args = p.parse_args()
    guard_env()

    if args.commit and DB_PATH.exists():
        sys.exit("fantasy.db already exists. Nothing done. Rename or move it first if you want a fresh build.")

    chain = load_chain()
    conn = sqlite3.connect(DB_PATH if args.commit else ":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript((HERE / "schema.sql").read_text(encoding="utf-8"))
    conn.executemany(
        """INSERT INTO seasons (season, nfl_game_id, yahoo_league_id, league_key,
                                league_name, num_teams, is_finished)
           VALUES (?,?,?,?,?,?,?)""",
        [(r["season"], r["game_id"], r["league_id"], r["league_key"],
          r["name"], r["num_teams"], r.get("is_finished")) for r in chain],
    )
    conn.commit()

    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    print(f"Tables ({len(tables)}): {', '.join(t for t in tables if t != 'sqlite_sequence')}")
    print(f"\nSeasons ({len(chain)}):")
    for s, g, l, n in conn.execute("SELECT season, nfl_game_id, yahoo_league_id, league_name FROM seasons"):
        print(f"  {s}  game {g:<3}  league {l:<7}  {n}")
    conn.close()

    if args.commit:
        print(f"\nCreated {DB_PATH.name}. Next: ingest_league.py (dry run first).")
    else:
        print("\nDry run only. Rerun with --commit to create fantasy.db.")


if __name__ == "__main__":
    main()
