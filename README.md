# We Graduated Fantasy API

Data pipeline (and, later, site) for the We Graduated league, Yahoo 4115.
Forked from the I Yearn project on 2026-11-08 and now independent of it.
No DRC engine, no synthetic trades.

Yahoo has 17 seasons: 2010 to 2026 (`league_chain.json`, written by
`probe_wegrad.py`). 2006 to 2009 exist only in the commissioner's sheets.

## Safety pattern

Every ingest script is a **dry run by default**: it opens `fantasy.db`
read-only, works on an in-memory copy, prints what would change, and writes
nothing. Add `--commit` to save. Commit runs back up `fantasy.db` to
`Backups/` first and write in one transaction. All scripts take
`--seasons 2026` or `--seasons 2019-2026` to limit scope, and refuse to run
if `.env` points at I Yearn (4416).

## Run order (Command Prompt, from this folder)

Python is I Yearn's venv until this folder gets its own:

```
set PY="..\Fantasy Football API Work\venv\Scripts\python.exe"
```

| Step | Script | What it loads | Yahoo calls |
|---|---|---|---|
| 1 | `create_database.py` | empty DB + 17 seasons | 0 |
| 2 | `ingest_league.py` | season settings, teams, managers, moves/trades/FAAB balance | ~51 |
| 3 | `ingest_drafts.py` | draft_picks | 17 |
| 4 | `ingest_transactions.py` | adds, drops, waivers + FAAB bids, trades, pick trades | 17 |
| 5 | `ingest_results.py` | final standings + every weekly matchup | ~290 |
| 6 | `ingest_weekly_stats.py` | every rostered player's points + slot, every week; final rosters | ~3,400 |
| any | `verify_db.py` | read-only health report | 0 |

Each step: run plain first, read the output, then rerun with `--commit`.

**Step 2 needs a human.** It writes `manager_review.txt` (who we think is
who across 17 seasons) and `manager_map.template.json`. If Yahoo hides
manager IDs, names are matched on Yahoo nicknames, which can be wrong.
Fix names in the template, save it as `manager_map.json`, rerun.
`--commit` refuses while any team-season is unassigned or two teams in one
season share a manager.

**Step 6 is long** (1.5 to 2 hours for everything). It saves after every
team-week, so Ctrl+C is safe and a rerun picks up where it stopped. Try one
season first: `--seasons 2025 --commit`.

## Files

- `wg_common.py` shared plumbing (dry-run/commit, backup, Yahoo retry, parsing)
- `schema.sql` tables; `v_team_seasons` view joins teams to managers
- `league_chain.json` season -> Yahoo game/league IDs
- `League Docs/` commissioner's sheets (offline copies, July 2026)
- `_old_scaffold_2026-07/` the July scaffold, superseded, kept for reference

## Not loaded yet

- Commissioner sheets: awards (2006+), all-time keepers, traded picks
  (several marked "not entered into Yahoo!")
- Keeper flags on draft picks (`is_keeper` is NULL until keeper logic lands)
- The site itself
