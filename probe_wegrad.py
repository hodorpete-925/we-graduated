"""
probe_wegrad.py - read-only discovery probe for We Graduated (Yahoo league 4115).

Starts at the 2026 league and walks Yahoo's "renewed from" chain backward,
one season at a time, until the chain ends or Yahoo refuses (for example, a
season before Pete joined). For each season it prints:

    season, game_id, league_id, league name, team count,
    transaction count, draft pick count, masked manager guids

It never opens or creates a database. The only files it writes are:
    league_chain.json   the season -> game_id / league_id map, for the
                        schema/ingest step to read later
    .env                yfpy refreshing its cached token block (normal)

Run host-side from the We Graduated folder:
    .\\venv\\Scripts\\python.exe probe_wegrad.py

The .env should be a copy of the I Yearn .env with YAHOO_LEAGUE_ID=4115.
Same app, same Yahoo account, so no new consent should be needed.
"""

import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
ENV = HERE / ".env"
OUT = HERE / "league_chain.json"

START_GAME_ID = 470      # NFL 2026
START_LEAGUE_ID = "4115"  # We Graduated 2026
PAUSE = 1.5               # seconds between Yahoo calls, to stay polite
MAX_SEASONS = 25          # hard stop so a bad chain can't loop forever


def dec(v):
    return v.decode("utf-8") if isinstance(v, bytes) else v


def fail(step, detail):
    print(f"\n*** FAILED at: {step}")
    print(detail)
    sys.exit(1)


def explain(e):
    msg = str(e)
    low = msg.lower()
    if "not in this league" in low or "not allowed to view" in low:
        return "Yahoo says this account is not in that league (season before you joined?)."
    if "not authorized" in low or "403" in msg:
        return "HTTP 403: credentials accepted but no Fantasy scope. Same failure as Aug."
    if "additional_authorization_required" in low or "401" in msg:
        return "HTTP 401: token is missing the Fantasy scope or is for the wrong app."
    if "404" in msg or "not found" in low:
        return "404: wrong game/league id for that season."
    return f"{type(e).__name__}: {msg}"


# ---- 1. .env sanity ---------------------------------------------------------
print("Step 1 - checking .env ...")
if not ENV.exists():
    fail(".env check", "No .env here. Copy the I Yearn one in and set YAHOO_LEAGUE_ID=4115.")
lines = ENV.read_text(encoding="utf-8").splitlines()
bad = [n for n, l in enumerate(lines, 1) if l.strip() and not l.lstrip().startswith("#") and "=" not in l]
blank = [n for n, l in enumerate(lines, 1) if not l.strip()]
if bad or blank:
    fail(".env check",
         f"yfpy crashes on lines without '='.\n  lines without '=': {bad or 'none'}\n"
         f"  blank lines: {blank or 'none'}\nDelete those lines (Notepad: check the last line) and rerun.")

from dotenv import load_dotenv  # noqa: E402
load_dotenv(ENV)
key = os.getenv("YAHOO_CONSUMER_KEY", "")
if not key or not os.getenv("YAHOO_CONSUMER_SECRET"):
    fail(".env check", "YAHOO_CONSUMER_KEY / YAHOO_CONSUMER_SECRET missing.")
lid = os.getenv("YAHOO_LEAGUE_ID", "").strip()
print(f"  key ends ...{key[-6:]}   YAHOO_LEAGUE_ID={lid or '(blank)'}")
if lid == "4416":
    fail(".env check", "YAHOO_LEAGUE_ID is 4416 (I Yearn). Set it to 4115 for this folder.")
print(f"  cached token present: {bool(os.getenv('YAHOO_ACCESS_TOKEN'))}")

import rauth.session  # noqa: E402
from yfpy.query import YahooFantasySportsQuery  # noqa: E402

rauth.session.OAUTH2_DEFAULT_TIMEOUT = 45  # fail fast instead of a 5-minute hang


def query_for(game_id, league_id):
    return YahooFantasySportsQuery(
        league_id=str(league_id),
        game_code="nfl",
        game_id=int(game_id),
        env_file_location=HERE,
        save_token_data_to_env_file=True,
    )


def count(fn, label):
    try:
        res = fn()
        time.sleep(PAUSE)
        return len(res) if res is not None else 0, None
    except Exception as e:  # count calls are informational; keep walking
        time.sleep(PAUSE)
        return None, f"{label}: {explain(e)}"


# ---- 2. walk the chain ------------------------------------------------------
print("\nStep 2 - walking the season chain back from 2026 ...\n")
chain = []
game_id, league_id = START_GAME_ID, START_LEAGUE_ID
stop_reason = "chain ended (no 'renew' link on the oldest season)"

for _ in range(MAX_SEASONS):
    try:
        q = query_for(game_id, league_id)
        meta = q.get_league_metadata()
        time.sleep(PAUSE)
    except Exception as e:
        stop_reason = f"game {game_id} / league {league_id}: {explain(e)}"
        break

    season = int(getattr(meta, "season", 0) or 0)
    row = {
        "season": season,
        "game_id": int(game_id),
        "league_id": str(league_id),
        "league_key": f"{game_id}.l.{league_id}",
        "name": dec(getattr(meta, "name", "?")),
        "num_teams": getattr(meta, "num_teams", None),
        "draft_status": dec(getattr(meta, "draft_status", None)),
        "is_finished": getattr(meta, "is_finished", None),
        "notes": [],
    }

    try:
        teams = q.get_league_teams()
        time.sleep(PAUSE)
        row["teams_returned"] = len(teams)
        masked = 0
        for t in teams:
            mgrs = getattr(t, "managers", None) or []
            if mgrs:
                m = mgrs[0]
                m = m.manager if hasattr(m, "manager") else m
                if getattr(m, "guid", None) in (None, "", "--hidden--"):
                    masked += 1
        row["masked_guids"] = masked
    except Exception as e:
        row["teams_returned"] = None
        row["notes"].append(f"teams: {explain(e)}")

    row["transactions"], err = count(q.get_league_transactions, "transactions")
    if err:
        row["notes"].append(err)
    row["draft_picks"], err = count(q.get_league_draft_results, "draft")
    if err:
        row["notes"].append(err)

    chain.append(row)
    print(f"  {season}  game {game_id:<3} league {league_id:<8} {row['name']!r:<34} "
          f"teams={row['teams_returned']}  txns={row['transactions']}  "
          f"picks={row['draft_picks']}  masked={row.get('masked_guids')}")
    for n in row["notes"]:
        print(f"        note: {n}")

    renew = dec(getattr(meta, "renew", None))
    if not renew or "_" not in str(renew):
        break
    prev_game, prev_league = str(renew).split("_", 1)
    game_id, league_id = int(prev_game), prev_league
else:
    stop_reason = f"hit the {MAX_SEASONS}-season safety cap"

# ---- 3. summary -------------------------------------------------------------
print(f"\nStopped: {stop_reason}")
if not chain:
    fail("2026 league", "Could not read even the 2026 league. Paste this output back to Claude.")

chain.sort(key=lambda r: r["season"])
OUT.write_text(json.dumps({"stop_reason": stop_reason, "seasons": chain}, indent=2), encoding="utf-8")
print(f"\nSeasons found: {chain[0]['season']} to {chain[-1]['season']} ({len(chain)} total)")
print(f"Wrote {OUT.name}. No database was touched.")
print("\nPROBE DONE. Paste the full output back to Claude.")
