"""
refresh.py - the whole weekly refresh in one step.

    refresh                      (double-click refresh.bat, or run it in cmd)
    refresh --no-publish         refresh and rebuild, but don't push to GitHub
    refresh --site-only          skip the Yahoo pulls; rebuild and publish only

Runs, in order, stopping at the first failure:
  1. ingest_league.py       --seasons <current> --commit   (FAAB balances, status)
  2. ingest_transactions.py --seasons <current> --commit   (adds, drops, trades, bids)
  3. ingest_results.py      --seasons <current> --commit   (scores, standings)
  4. ingest_weekly_stats.py --seasons <current> --commit   (player points; last two weeks re-pulled)
  5. live_scores.py --no-publish                           (scores.json for League home)
  6. generate_site.py                                      (index.html)
  7. git add / commit / push                               (only if something changed)

Every --commit step backs up fantasy.db to Backups/ first. Output also goes to
refresh.log. Losing FAAB bids are not in the Yahoo API; ask Claude to "refresh
FAB offers" after Wednesday waivers to update faab_offers.json.
"""

import argparse
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
PY = sys.executable
FLAGS = 0x08000000 if sys.platform == "win32" else 0     # no console pop-ups from the scheduler
LOG = HERE / "refresh.log"


def say(msg):
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(msg, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(args, label):
    say(f"--- {label}")
    r = subprocess.run([PY, *args], cwd=HERE, capture_output=True, text=True, creationflags=FLAGS)
    out = (r.stdout + r.stderr).strip().splitlines()
    for ln in out[-6:]:
        say("    " + ln)
    if r.returncode != 0:
        say(f"FAILED: {label} (exit {r.returncode}). Nothing after this step ran. Full output above / in refresh.log.")
        sys.exit(r.returncode)


def git(*a):
    r = subprocess.run(["git", *a], cwd=HERE, capture_output=True, text=True, creationflags=FLAGS)
    return r.returncode, (r.stdout + r.stderr).strip()


def current_season():
    c = sqlite3.connect(f"file:{HERE / 'fantasy.db'}?mode=ro", uri=True)
    return c.execute("SELECT MAX(season) FROM seasons").fetchone()[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-publish", action="store_true", help="don't push to GitHub")
    ap.add_argument("--site-only", action="store_true", help="skip the Yahoo pulls")
    ap.add_argument("message", nargs="?", default="", help="optional commit message")
    a = ap.parse_args()
    season = str(current_season())
    say(f"=== We Graduated refresh, season {season}")
    if not a.site_only:
        for script, label in [("ingest_league.py", "1/7 league settings and FAAB balances"),
                              ("ingest_transactions.py", "2/7 transactions"),
                              ("ingest_results.py", "3/7 scores and standings"),
                              ("ingest_weekly_stats.py", "4/7 player points (takes a few minutes)")]:
            run([script, "--seasons", season, "--commit"], label)
        run(["live_scores.py", "--no-publish"], "5/7 live matchups (scores.json)")
    run(["generate_site.py"], "6/7 build the site")
    if a.no_publish:
        say("Done. Not published (--no-publish).")
        return
    say("--- 7/7 publish to GitHub")
    git("add", "-A")
    rc, _ = git("diff", "--cached", "--quiet")
    if rc == 0:
        say("    nothing changed since the last publish")
    else:
        msg = a.message or f"Refresh {datetime.now():%Y-%m-%d %H:%M}"
        rc, out = git("commit", "-m", msg)
        if rc != 0:
            say("    commit failed: " + out); sys.exit(1)
        rc, out = git("push")
        if rc != 0:
            say("    push failed: " + out); sys.exit(1)
        say("    pushed. The live site updates in a minute or two.")
    say("Done. Reminder: losing FAAB bids need a browser read after Wednesday waivers (ask Claude to refresh FAB offers).")


if __name__ == "__main__":
    main()
