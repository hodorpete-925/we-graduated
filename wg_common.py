"""
wg_common.py - shared plumbing for the We Graduated ingest scripts.

Every ingest script follows the same safety pattern:

  DRY RUN (default)
    The real fantasy.db is opened READ-ONLY and copied into memory. The
    script pulls from Yahoo and writes into that in-memory copy, prints what
    changed, then throws the copy away. fantasy.db is never written.

  --commit
    fantasy.db is first copied to Backups/fantasy_<timestamp>_<script>.db,
    then the same code runs against the real file. All writes for the run go
    in one transaction, so an error mid-run rolls everything back.

Exception: ingest_weekly_stats.py commits per team-week so a 2-hour backfill
can be interrupted and resumed. It still backs up first.
"""

import argparse
import json
import shutil
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
DB_PATH = HERE / "fantasy.db"
BACKUPS = HERE / "Backups"
CHAIN_PATH = HERE / "league_chain.json"
I_YEARN_LEAGUE_ID = "4416"

RETRY_WAIT = 30
POLITE_DELAY = 1.0


# ---------------------------------------------------------------- guards ---

def guard_env():
    """Refuse to run if this folder's .env points at I Yearn."""
    from dotenv import dotenv_values
    env = dotenv_values(HERE / ".env")
    if str(env.get("YAHOO_LEAGUE_ID", "")).strip() == I_YEARN_LEAGUE_ID:
        sys.exit("Refusing to run: .env has YAHOO_LEAGUE_ID=4416 (I Yearn). Set it to 4115.")


# ------------------------------------------------------------- arguments ---

def base_args(description):
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--commit", action="store_true",
                   help="write to fantasy.db (default is a dry run that writes nothing)")
    p.add_argument("--seasons", default="",
                   help="limit to seasons, e.g. 2026 or 2019-2026 or 2012,2015 (default: all)")
    return p


def parse_seasons(spec, available):
    if not spec:
        return list(available)
    out = set()
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if "-" in chunk:
            a, b = chunk.split("-")
            out.update(range(int(a), int(b) + 1))
        elif chunk:
            out.add(int(chunk))
    return [s for s in available if s in out]


# -------------------------------------------------------------- database ---

def open_db(commit, script_name):
    """Return a connection. Dry run: in-memory copy of a read-only open.
    Commit: backup first, then the real file."""
    if not DB_PATH.exists():
        sys.exit("fantasy.db not found. Run create_database.py --commit first.")
    if commit:
        BACKUPS.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = BACKUPS / f"fantasy_{stamp}_{script_name}.db"
        shutil.copy2(DB_PATH, dest)
        print(f"Backed up fantasy.db -> Backups/{dest.name}")
        conn = sqlite3.connect(DB_PATH)
        print("MODE: COMMIT (writes go to fantasy.db)\n")
    else:
        src = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
        conn = sqlite3.connect(":memory:")
        src.backup(conn)
        src.close()
        print("MODE: DRY RUN (in-memory copy; fantasy.db is not touched)\n")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def finish(conn, commit):
    if commit:
        conn.commit()
        print("\nCommitted.")
    else:
        print("\nDry run only. Nothing was written. Rerun with --commit to save.")
    conn.close()


def table_counts(conn, tables, seasons=None):
    out = {}
    for t in tables:
        if seasons is not None and "season" in [r[1] for r in conn.execute(f"PRAGMA table_info({t})")]:
            q = f"SELECT COUNT(*) FROM {t} WHERE season IN ({','.join('?' * len(seasons))})"
            out[t] = conn.execute(q, seasons).fetchone()[0]
        else:
            out[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    return out


def print_delta(before, after):
    print("\n=== row counts (before -> after) ===")
    for t in before:
        d = after[t] - before[t]
        print(f"  {t:<24} {before[t]:>7} -> {after[t]:>7}   ({'+' if d >= 0 else ''}{d})")


def seasons_from_db(conn):
    return conn.execute(
        "SELECT season, nfl_game_id, yahoo_league_id FROM seasons ORDER BY season"
    ).fetchall()


# ----------------------------------------------------------------- yahoo ---

_query_cache = {}


def query_for(game_id, league_id):
    """One yfpy query per season, reusing the token cached in .env."""
    import rauth.session
    from yfpy.query import YahooFantasySportsQuery
    rauth.session.OAUTH2_DEFAULT_TIMEOUT = 45   # fail fast, don't hang 5 minutes
    key = (int(game_id), str(league_id))
    if key not in _query_cache:
        _query_cache[key] = YahooFantasySportsQuery(
            league_id=str(league_id),
            game_code="nfl",
            game_id=int(game_id),
            env_file_location=HERE,
            save_token_data_to_env_file=True,
        )
    return _query_cache[key]


def call(fn, *args, retries=2, delay=POLITE_DELAY):
    """Call a yfpy method with one retry on a transient failure."""
    for attempt in range(retries + 1):
        try:
            res = fn(*args)
            if delay:
                time.sleep(delay)
            return res
        except Exception as e:
            msg = str(e).lower()
            # Yahoo access tokens last one hour. yfpy refreshes on the next call,
            # but reports the expiry as DataNotFound, so check this first.
            if "token_expired" in msg and attempt < retries:
                print("    token expired; refreshing and retrying")
                time.sleep(2)
                continue
            permanent = ("not in this league" in msg or "not allowed" in msg
                         or "not authorized" in msg or "datanotfound" in type(e).__name__.lower())
            if permanent or attempt == retries:
                raise
            print(f"    transient {type(e).__name__}; retrying in {RETRY_WAIT}s")
            time.sleep(RETRY_WAIT)


# ------------------------------------------------------------- unpacking ---

def dec(v):
    return v.decode("utf-8") if isinstance(v, bytes) else v


def unwrap(obj, key):
    """yfpy sometimes returns {'player': Player} style wrappers."""
    if isinstance(obj, dict) and key in obj:
        return obj[key]
    if type(obj).__name__.lower() == key:
        return obj
    inner = getattr(obj, key, None)
    return inner if inner is not None else obj


def as_list(v, key):
    """Normalize list / dict / single-object shapes into a list of objects."""
    if v is None or v == "":
        return []
    if isinstance(v, dict):
        if key in v:
            v = v[key]
        else:
            v = list(v.values())
    if not isinstance(v, list):
        v = [v]
    return [unwrap(x, key) for x in v]


def get(obj, name, default=None):
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def yahoo_team_id(team_key):
    return int(str(dec(team_key)).split(".")[-1]) if team_key else None


def tsid(conn, season, team_key):
    """Yahoo team_key '461.l.4177.t.5' -> our team_season_id."""
    yid = yahoo_team_id(team_key)
    if yid is None:
        return None
    row = conn.execute(
        "SELECT team_season_id FROM teams WHERE season=? AND yahoo_team_id=?", (season, yid)
    ).fetchone()
    return row[0] if row else None


def ensure_player(conn, player_id, name=None, position=None, nfl_team=None):
    """Insert on first sight. Real values overwrite placeholders, never the reverse."""
    placeholder = f"Player {player_id}"
    conn.execute(
        "INSERT OR IGNORE INTO players (player_id, player_name, position, nfl_team) VALUES (?,?,?,?)",
        (player_id, name or placeholder, position, nfl_team),
    )
    if name:
        conn.execute(
            """UPDATE players SET player_name=?,
                   position=COALESCE(?, position), nfl_team=COALESCE(?, nfl_team)
               WHERE player_id=?""",
            (name, position, nfl_team, player_id),
        )


def player_fields(p):
    """(player_id, full_name, position, nfl_team) from a yfpy Player."""
    p = unwrap(p, "player")
    nm = get(p, "name")
    full = get(nm, "full", nm) if nm is not None else None
    return (
        int(get(p, "player_id")),
        dec(full) if full else None,
        dec(get(p, "display_position")),
        dec(get(p, "editorial_team_abbr")),
    )


def load_chain():
    if not CHAIN_PATH.exists():
        sys.exit("league_chain.json not found. Run probe_wegrad.py first.")
    return json.loads(CHAIN_PATH.read_text(encoding="utf-8"))["seasons"]


def now_str():
    return datetime.now().isoformat(sep=" ", timespec="seconds")
