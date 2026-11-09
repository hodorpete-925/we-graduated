"""
live_scores.py - this week's matchups and standings for League home, written
to scores.json (ported from I Yearn's pull_yahoo_week.py + publish_scores.py).

The live page re-fetches scores.json when it loads, so during games only this
small file is pushed; the big page is not rebuilt. Read-only against
fantasy.db (never opens it). scores.json is written only after every Yahoo
call succeeds, so a failed pull leaves the last good file in place.

    py live_scores.py                 pull, then push scores.json to GitHub if it changed
    py live_scores.py --no-publish    pull only (refresh.py uses this)
    py live_scores.py --week 9        a specific week
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from wg_common import call, dec, guard_env, load_chain, query_for, unwrap

HERE = Path(__file__).parent
SCORES = HERE / "scores.json"
FLAGS = 0x08000000 if sys.platform == "win32" else 0
STATUS = {"preevent": "upcoming", "midevent": "in_progress", "postevent": "final"}


def num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def team_id(t):
    tid = getattr(t, "team_id", None)
    if tid is None and getattr(t, "team_key", None):
        tid = str(dec(t.team_key)).split(".")[-1]
    return int(tid)


def record(ts):
    ot = getattr(ts, "outcome_totals", None)
    w, l, t = (getattr(ot, "wins", 0), getattr(ot, "losses", 0), getattr(ot, "ties", 0)) if ot else (0, 0, 0)
    return f"{int(w or 0)}-{int(l or 0)}-{int(t or 0)}"


def now_et():
    import time
    return datetime.now().strftime("%b %d %I:%M %p ").replace(" 0", " ") + ("EDT" if time.localtime().tm_isdst > 0 else "EST")


def pull(week=None):
    chain = load_chain()
    cur = max(chain, key=lambda s: s["season"])
    q = query_for(cur["game_id"], cur["league_id"])
    meta = call(q.get_league_metadata)
    week = week or int(getattr(meta, "current_week", 0) or 0)
    if not week:
        sys.exit("could not determine the current week")
    st = call(q.get_league_standings)
    standings = {}
    for t in (getattr(st, "teams", None) or []):
        t = unwrap(t, "team")
        ts = getattr(t, "team_standings", None)
        standings[team_id(t)] = {"rank": int(getattr(ts, "rank", 0) or 0) if ts else None, "rec": record(ts) if ts else None,
                                 "faab": int(num(getattr(t, "faab_balance", 0)))}
    sb = call(q.get_league_scoreboard_by_week, week)
    out, statuses = [], set()
    for m in (getattr(sb, "matchups", None) or []):
        m = unwrap(m, "matchup")
        teams = [unwrap(t, "team") for t in (getattr(m, "teams", None) or [])]
        if len(teams) != 2:
            continue
        sides = []
        for t in teams:
            tid = team_id(t)
            s = standings.get(tid, {})
            sides.append({"tid": tid, "team": dec(t.name),
                          "proj": round(num(getattr(getattr(t, "team_projected_points", None), "total", 0)), 2),
                          "pts": round(num(getattr(getattr(t, "team_points", None), "total", 0)), 2),
                          "rec": s.get("rec"), "rank": s.get("rank"),
                          "win_prob": round(num(getattr(t, "win_probability", 0)), 3) or None})
        raw = str(dec(getattr(m, "status", "") or ""))
        statuses.add(raw)
        out.append({"a": sides[0], "b": sides[1], "status": STATUS.get(raw, "unknown")})
    any_pts = any(x["a"]["pts"] or x["b"]["pts"] for x in out)
    status = ("in_progress" if "midevent" in statuses and any_pts else
              "final" if statuses and statuses <= {"postevent"} else "upcoming")
    return {"as_of": now_et(), "season": cur["season"], "week": week, "status": status,
            "source": "Yahoo Fantasy Sports API (live_scores.py)", "matchups": out}


def publish():
    def git(*a):
        r = subprocess.run(["git", *a], cwd=HERE, capture_output=True, text=True, creationflags=FLAGS)
        return r.returncode, (r.stdout + r.stderr).strip()
    git("add", "scores.json")
    rc, _ = git("diff", "--cached", "--quiet", "--", "scores.json")
    if rc == 0:
        print("scores.json unchanged; nothing to publish")
        return 0
    rc, out = git("commit", "-m", f"Scores {datetime.now():%Y-%m-%d %H:%M}", "--", "scores.json")
    if rc != 0:
        print("commit failed: " + out)
        return rc
    rc, out = git("push")
    print("pushed scores.json" if rc == 0 else "push failed: " + out)
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--week", type=int)
    ap.add_argument("--no-publish", action="store_true")
    a = ap.parse_args()
    guard_env()
    doc = pull(a.week)
    tmp = SCORES.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, SCORES)
    print(f"week {doc['week']} ({doc['status']}): {len(doc['matchups'])} matchups -> scores.json at {doc['as_of']}")
    for m in doc["matchups"]:
        print(f"  {m['a']['team'][:24]:<24} {m['a']['pts']:>7} vs {m['b']['pts']:<7} {m['b']['team'][:24]}")
    if not a.no_publish:
        sys.exit(publish())


if __name__ == "__main__":
    main()
