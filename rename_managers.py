"""
rename_managers.py - one-time rename of managers to the league's first names
(Pete's call, 2026-11-09). manager_map.json was updated the same day, so any
future ingest_league.py run produces these same names.

    venv\\Scripts\\python.exe rename_managers.py
    venv\\Scripts\\python.exe rename_managers.py --commit
"""

from wg_common import base_args, finish, guard_env, open_db

RENAMES = {"Michael": "Mike", "Christopher": "Chris", "Peter": "Pete", "RyanC": "Ryan"}


def main():
    args = base_args(__doc__).parse_args()
    guard_env()
    conn = open_db(args.commit, "rename_managers")
    for old, new in RENAMES.items():
        if conn.execute("SELECT 1 FROM managers WHERE canonical_name=?", (new,)).fetchone():
            print(f"  {new} already exists, skipping {old}")
            continue
        n = conn.execute("UPDATE managers SET canonical_name=? WHERE canonical_name=?", (new, old)).rowcount
        print(f"  {old:<12} -> {new}" + ("" if n else "   (not found)"))
    print("\nManagers now:", ", ".join(r[0] for r in conn.execute(
        "SELECT canonical_name FROM managers ORDER BY canonical_name")))
    finish(conn, args.commit)


if __name__ == "__main__":
    main()
