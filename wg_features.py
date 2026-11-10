"""
wg_features.py - the I Yearn ports added 2026-11-09:

  1. Player search cards (seasons, weekly bars, rank neighbors, lineage, moves)
  2. Player comparison (up to three players side by side)
  3. Team page tabs: Overview / Roster / Drafts / Trades
  4. Draft board grid (rounds x teams) on the Drafts page
  5. "Last updated" footer
  7. Live matchups on League home (scores.json sidecar, re-fetched on load)

Item 6 (one-step refresh) is refresh.py. The heavy lists ship as JSON and are
drawn in the browser; small per-team pieces are rendered here.
"""

import html
import json
import subprocess
from collections import defaultdict
from pathlib import Path

import wg_players as P
import wg_value as W

e = lambda s: html.escape(str(s if s is not None else ""))
HERE = Path(__file__).parent
_VB = {}


def jdump(o):
    return json.dumps(o, separators=(",", ":")).replace("</", "<\\/")


def value_rows(L, season):
    """W.value_board is used by three pages; compute each season once."""
    if season not in _VB:
        _VB[season] = W.value_board(L.c, L, season)
    return _VB[season]


# ---------------------------------------------------------------- 1. search

def corpus_script(L):
    C = P.build(L)
    return C, f"<script>window.WG_PC = {jdump(list(C.values()))};</script>"


def search_body(L, C, leaderboard_html):
    return (leaderboard_html +
            '<div class="ps-wrap"><input id="wg-ps" class="ps-input" type="search" placeholder="Search any player since 2012 (two letters or more)" autocomplete="off"></div>'
            '<div id="wg-ps-out" class="ps-results"></div>'
            '<p class="note">Points, games and positional ranks count only weeks a player was on a We Graduated roster '
            '(Yahoo only reports rostered players), so "WR14" means 14th among rostered receivers that season. '
            'Games skip weeks parked on IR.</p>')


def compare_body():
    return ('<div class="cmp-top"><input id="wg-cmp" class="ps-input" type="search" placeholder="Add a player (up to three)" autocomplete="off">'
            '<div id="wg-cmp-sugg" class="pc-sugg" hidden></div></div>'
            '<div id="wg-cmp-chips" class="cmp-chips"></div><div id="wg-cmp-out"></div>')


# ---------------------------------------------------------------- 3. team tabs

def _tag(z, kind):
    if z is None:
        return '<span class="vtag vtag-nd">under 2 games</span>'
    if z >= 1:
        lab, cls = "Big win", "vtag-hi"
    elif z >= 0.3:
        lab, cls = "Above " + ("the line" if kind == "pick" else "average"), "vtag-up"
    elif z > -0.3:
        lab, cls = "About par", "vtag-mid"
    elif z > -1:
        lab, cls = "Below " + ("the line" if kind == "pick" else "average"), "vtag-dn"
    else:
        lab, cls = "Bust", "vtag-lo"
    return f'<span class="vtag {cls}">{lab}</span>'


def team_roster_tab(L, manager, cur, table):
    if not cur:
        return '<p class="note">Not in the league this season.</p>'
    wk, roster = L.current_roster(cur["team_season_id"])
    keepers = {p["player_id"] for p in L.draft(L.current) if p["team_season_id"] == cur["team_season_id"] and p["is_keeper"]}
    rows = ""
    for r in roster:
        pid = r["player_id"]
        k = ' <span class="vtag vtag-keep">Keeper</span>' if pid in keepers else ""
        rows += (f'<tr class="pexp-row" data-pexp="{pid}"><td class="meta">{e(r["selected_position"])}</td>'
                 f'<td class="player-name">{e(r["player_name"])}{k}<span class="sub-line">{e(r["position"])} &middot; {e(r["nfl_team"])}</span></td>'
                 f'<td class="num">{r["fantasy_points"]:.2f}</td><td class="num">{(r["season_pts"] or 0):.1f}</td>'
                 f'<td class="expand-col"><button class="expand-btn pexp-btn" type="button" aria-label="Show past seasons">&rsaquo;</button></td></tr>'
                 f'<tr class="pexp-detail" hidden><td colspan="5"></td></tr>')
    return (f'<p class="note">Week {wk} lineup. Tap a player for his past seasons and how he got here.</p>'
            f'<div class="table-scroll"><table class="roster wg-roster"><thead><tr><th>Slot</th><th>Player</th>'
            f'<th class="num">Wk {wk}</th><th class="num">Season</th><th></th></tr></thead><tbody>{rows}</tbody></table></div>')


def team_drafts_tab(L, manager, collapsible):
    out = ""
    for y in reversed(L.years):
        rows, meta = value_rows(L, y)
        mine = [r for r in rows if r["mgr"] == manager and r["kind"] in ("pick", "keeper")]
        if not mine:
            continue
        mine.sort(key=lambda r: r["pick"] or 999)
        trs = "".join(
            f'<tr><td class="num">{r["rnd"]}</td><td class="num">{r["pick"]}</td><td class="player-name">{e(r["name"])}'
            f'<span class="sub-line">{e(r["pos"])}</span></td><td>{"Keeper" if r["kind"] == "keeper" else "Drafted"}</td>'
            f'<td class="num">{r["pts"]:.1f}</td><td class="num">{r["fpor"]:+.1f}</td><td>{_tag(r.get("z"), r["kind"])}</td></tr>'
            for r in mine)
        tot = sum(r["fpor"] for r in mine)
        best = max(mine, key=lambda r: r.get("z") if r.get("z") is not None else -9)
        body = (f'<div class="table-scroll"><table class="roster"><thead><tr><th class="num">Rd</th><th class="num">Pick</th><th>Player</th>'
                f'<th>How</th><th class="num">Pts</th><th class="num">FPOR</th><th>Vs. slot</th></tr></thead><tbody>{trs}</tbody></table></div>')
        out += collapsible(str(y), f'{len(mine)} picks &middot; {tot:+.0f} FPOR &middot; best: {e(best["name"])}', body, open_=(y == L.current))
    return (out + '<p class="note">FPOR is points over a replacement-level player at the same position. "Vs. slot" compares a drafted '
            'player with what an average pick at that slot produced that season, and a keeper with the average keeper. '
            'Same method as the FPOR value board.</p>') if out else '<p class="note">No drafts on Yahoo.</p>'


def _since(L, pid, mgr, season, week, weekly):
    """Points scored for `mgr` from the trade week on, until he left that roster."""
    pts = g = 0
    for (s, w, m, p) in weekly.get(pid, []):
        if (s, w) < (season, week):
            continue
        if m != mgr:
            break
        pts += p; g += 1
    return pts, g


def team_trades_tab(L, manager, weekly_by_pid):
    trades = L.c.execute("""SELECT transaction_id, season, timestamp FROM transactions
                            WHERE event_type='trade' AND status='successful' ORDER BY timestamp DESC""").fetchall()
    cards = ""
    n = 0
    for tid, season, ts in trades:
        legs = L.c.execute("""SELECT tp.player_id, tp.team_season_id, p.player_name, p.position FROM transaction_players tp
                              JOIN players p USING(player_id) WHERE transaction_id=? AND tp.direction='incoming'""", (tid,)).fetchall()
        picks = L.c.execute("SELECT draft_round, destination_team_season_id, original_team_season_id FROM transaction_picks WHERE transaction_id=?", (tid,)).fetchall()
        sides = defaultdict(lambda: {"players": [], "picks": [], "pts": 0.0})
        for pid, tsid, name, pos in legs:
            m = L.mgr(tsid)
            wk = W.week_of(season, ts)
            p, g = _since(L, pid, m, season, wk, weekly_by_pid)
            sides[m]["players"].append((name, W.norm_pos(pos), p, g))
            sides[m]["pts"] += p
        for rnd, dst, orig in picks:
            sides[L.mgr(dst)]["picks"].append(f"Rd {rnd} pick ({L.mgr(orig)}'s)")
        if manager not in sides:
            continue
        n += 1
        others = [m for m in sides if m != manager]
        lead = max(sides, key=lambda m: sides[m]["pts"])
        gap = sides[lead]["pts"] - min(v["pts"] for v in sides.values())
        has_players = any(v["players"] for v in sides.values())
        has_picks = any(v["picks"] for v in sides.values())
        if not has_players:
            verdict, cls = "Pick swap", "tv-even"
        elif gap < 10:
            verdict, cls = "Even so far", "tv-even"
        else:
            verdict = f'{e(lead)} +{gap:.0f} pts since the trade' + (" (picks not counted)" if has_picks else "")
            cls = "tv-even" if has_picks else ("tv-win" if lead == manager else "tv-loss")
        cols = ""
        for m in [manager] + others:
            v = sides[m]
            items = "".join(f'<div class="tt-p"><span>{e(nm)} <span class="tl-via">{e(ps)}</span></span>'
                            f'<span class="tt-pts">{p:.1f}<span class="tl-via"> in {g} g</span></span></div>'
                            for nm, ps, p, g in v["players"])
            items += "".join(f'<div class="tt-p"><span>{e(k)}</span><span class="tl-via">pick</span></div>' for k in v["picks"])
            cols += (f'<div class="tt-side"><div class="tt-head">{e(m)} got <span class="tt-tot">{v["pts"]:.1f} pts</span></div>'
                     f'{items or "<div class=tl-via>nothing listed</div>"}</div>')
        cards += (f'<div class="tt-card"><div class="tt-meta"><span>{e(str(ts)[:10])}</span><span class="tt-verdict {cls}">{verdict}</span></div>'
                  f'<div class="tt-sides">{cols}</div></div>')
    if not n:
        return '<p class="note">No trades on Yahoo.</p>'
    return (f'<p class="note">{n} trades since {L.years[0]}. Points count what each player scored for the team that got him, '
            'from the trade week until he left that roster (keeps included). Picks show as picks; we can\'t yet trace who was taken with them.</p>' + cards)


def weekly_by_pid(L):
    out = defaultdict(list)
    for pid, s, w, tsid, pts, slot in L.c.execute(
            "SELECT player_id, season, week, team_season_id, fantasy_points, selected_position FROM player_weekly_stats ORDER BY season, week"):
        out[pid].append((s, w, L.mgr(tsid), 0.0 if slot == "IR" else (pts or 0.0)))
    return out


def tabs(slug, panels):
    """panels: [(key, label, html)]"""
    btns = "".join(f'<button class="tab-btn{" active" if i == 0 else ""}" data-tab="{slug}-{k}" type="button">{lab}</button>'
                   for i, (k, lab, _) in enumerate(panels))
    body = "".join(f'<div class="tab-panel{" active" if i == 0 else ""}" id="{slug}-{k}"{"" if i == 0 else " hidden"}>{h}</div>'
                   for i, (k, _, h) in enumerate(panels))
    return f'<div class="tabs" data-tabgroup="{slug}">{btns}</div>{body}'


# ---------------------------------------------------------------- 4. draft board

def draft_board_body(L):
    years = [y for y in L.years if value_rows(L, y)[0]]
    opts = "".join(f'<option value="{y}"{" selected" if y == L.current else ""}>{y}</option>' for y in reversed(years))
    return (f'<div class="vb-filters"><label class="vb-filter yr-pick">Season <select id="db-season">{opts}</select></label>'
            '<div class="vb-filter vb-chips" id="db-color"><button type="button" class="vb-chip is-on" data-c="z">Color: value vs. slot</button>'
            '<button type="button" class="vb-chip" data-c="f">Color: FPOR</button>'
            '<button type="button" class="vb-chip" data-c="pos">Color: position</button></div></div>'
            '<div id="db-legend"></div><div class="db-wrap"><div id="db-grid" class="db-grid"></div></div>')


# ---------------------------------------------------------------- 5. footer

def footer(L, generated):
    c = L.c
    data_at = max(filter(None, [c.execute("SELECT MAX(fetched_at) FROM player_weekly_stats").fetchone()[0],
                                c.execute("SELECT MAX(fetched_at) FROM matchups").fetchone()[0]]), default="unknown")
    wk = L.last_final_week(L.current)
    commits = []
    try:
        r = subprocess.run(["git", "log", "-6", "--date=format:%b %d %I:%M %p", "--pretty=%ad\t%s"], cwd=HERE,
                           capture_output=True, text=True, timeout=10)
        commits = [ln.split("\t", 1) for ln in r.stdout.splitlines() if "\t" in ln]
    except Exception:
        pass
    log = "".join(f"<li><span>{e(d)}</span> {e(m)}</li>" for d, m in commits) or "<li>No publish history on this machine.</li>"
    return (f'<details class="upd"><summary><span class="upd-dot"></span>Data through week {wk} final &middot; '
            f'refreshed {e(str(data_at)[:16])} &middot; built {e(generated)}</summary>'
            f'<div class="upd-body"><div>Yahoo data last pulled: <b>{e(str(data_at)[:16])}</b></div>'
            f'<div>Page built: <b>{e(generated)}</b></div><div class="upd-h">Recent publishes</div><ul>{log}</ul>'
            '<div class="tl-via">Live scores on League home refresh on their own during games (scores.json).</div></div></details>')


# ---------------------------------------------------------------- 7. live matchups

def live_block(L):
    """Home-page matchups. Seeded from the database at build time; the page then
    re-fetches scores.json (written by live_scores.py) and redraws if it is newer."""
    y = L.current
    games = [m for m in L.matchups if m["season"] == y]
    live_wk = max((m["week"] for m in games if m["status"] != "preevent"), default=1)
    seen, mus = set(), []
    stand = {r["team_season_id"]: r for r in L.season_table(y)}
    for m in games:
        if m["week"] != live_wk:
            continue
        k = tuple(sorted((m["team_season_id"], m["opponent_team_season_id"] or 0)))
        if k in seen:
            continue
        seen.add(k)
        opp = next((o for o in games if o["week"] == live_wk and o["team_season_id"] == m["opponent_team_season_id"]), {})
        def side(tsid, pts, proj):
            t = L.team(tsid); s = stand.get(tsid, {})
            return {"tid": t["yahoo_team_id"], "team": t["team_name"], "pts": pts or 0, "proj": proj or 0,
                    "rec": f'{s.get("wins", 0)}-{s.get("losses", 0)}-{s.get("ties", 0)}', "rank": s.get("rank")}
        mus.append({"a": side(m["team_season_id"], m["points"], m.get("projected_points")),
                    "b": side(m["opponent_team_season_id"], m["opponent_points"], opp.get("projected_points")),
                    "status": {"preevent": "upcoming", "midevent": "in_progress", "postevent": "final"}.get(m["status"], "unknown")})
    statuses = {x["status"] for x in mus}
    seed = {"as_of": "last site build", "week": live_wk, "status": "final" if statuses == {"final"} else
            ("in_progress" if "in_progress" in statuses else "upcoming"), "matchups": mus}
    sidecar = HERE / "scores.json"
    if sidecar.exists():
        try:
            sc = json.loads(sidecar.read_text(encoding="utf-8"))
            if sc.get("matchups") and sc.get("week", 0) >= live_wk:
                seed = sc
        except Exception:
            pass
    tid_mgr = {t["yahoo_team_id"]: t["manager"] for t in L.teams_in(y)}
    from wg_data import slug
    tid_slug = {k: slug(v) for k, v in tid_mgr.items()}
    return ('<h2 id="live-h">Matchups</h2><div id="live-meta" class="note"></div><div id="live-mu" class="mu-grid"></div>'
            f'<script>window.WG_LIVE = {jdump(seed)}; window.WG_TIDS = {jdump({"m": tid_mgr, "s": tid_slug})};</script>')


# ---------------------------------------------------------------- CSS + JS

FEAT_CSS = """
.ps-wrap { margin: 18px 0 10px; }
.ps-results { margin-top: 10px; }
.pc2 { border: 1px solid var(--gray-200); border-radius: 12px; padding: 16px 18px; background: #fff; margin-bottom: 14px; }
.pc2-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap; }
.pc2-name { font-size: 18px; font-weight: 700; color: var(--blue-800); }
.pc2-meta { font-size: 12.5px; color: var(--gray-600); margin-top: 2px; }
.pc2-label { font-size: 10.5px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--gray-500); margin: 16px 0 8px; }
.pc2-years { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 12px; }
.pc2-yr { border: 1px solid var(--gray-100); border-radius: 8px; padding: 10px; background: var(--gray-50, #fafafa); min-width: 0; }
.pc2-yrhead { font-size: 13px; display: flex; gap: 6px; align-items: baseline; flex-wrap: wrap; }
.pc2-yrhead b { font-size: 14px; color: var(--blue-800); }
.pc2-rank { font-weight: 700; color: #1d1d1f; }
.pc2-sub { font-size: 11.5px; color: var(--gray-600); margin: 2px 0 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.pc2-bars { width: 100%; height: 64px; display: block; }
.pc2-nb { width: 100%; font-size: 11.5px; border-collapse: collapse; margin-top: 6px; }
.pc2-nb td { padding: 2px 3px; color: var(--gray-600); }
.pc2-nb td:last-child { text-align: right; font-variant-numeric: tabular-nums; }
.pc2-nb tr.self td { color: var(--blue-800); font-weight: 700; background: #eef4ff; }
.pc2-two { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.3fr); gap: 18px; }
.pc2-two table.roster { font-size: 12.5px; margin-top: 0; }
.pc2-two table.roster td, .pc2-two table.roster th { padding: 6px 6px; }
.lineage-flow { margin-bottom: 4px; }
.lineage-kept { border-left-color: var(--blue-400, #3B82C4); }
.lineage-node { flex: 0 1 170px; min-width: 150px; }
@media (max-width: 860px) { .pc2-years { grid-template-columns: minmax(0, 1fr); } .pc2-two { grid-template-columns: minmax(0, 1fr); }
  .lineage-node { flex: 1 1 100%; } .lineage-arrow { transform: rotate(90deg); justify-content: center; width: 100%; }
  .lineage-break { max-width: none; flex-direction: row; width: 100%; } }
.cmp-top { position: relative; max-width: 560px; margin: 16px 0 10px; }
.cmp-chips { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
.cmp-chip { display: inline-flex; align-items: center; gap: 8px; border-radius: 999px; padding: 5px 10px 5px 12px; font-size: 13px; font-weight: 600; color: #fff; }
.cmp-chip button { border: 0; background: rgba(255,255,255,.25); color: #fff; border-radius: 50%; width: 20px; height: 20px; cursor: pointer; line-height: 1; }
.cmp-cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; align-items: start; margin-top: 14px; }
.cmp-col { border: 1px solid var(--gray-200); border-top-width: 4px; border-radius: 10px; padding: 12px 14px; background: #fff; }
.cmp-col h3 { margin: 0; font-size: 15.5px; color: var(--blue-800); }
.cmp-kv { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 10px; margin: 10px 0; }
.cmp-kv div { background: var(--gray-50, #fafafa); border-radius: 6px; padding: 6px 8px; }
.cmp-kv .k { font-size: 10px; text-transform: uppercase; letter-spacing: .08em; color: var(--gray-500); }
.cmp-kv .v { font-size: 16px; font-weight: 700; color: #1d1d1f; font-variant-numeric: tabular-nums; }
.pexp-row { cursor: pointer; }
.pexp-detail td { background: var(--gray-50, #fafafa); padding: 10px 12px !important; }
.pexp-mini { font-size: 12.5px; }
.pexp-mini table { width: 100%; border-collapse: collapse; margin-top: 6px; }
.pexp-mini td, .pexp-mini th { padding: 4px 6px; text-align: left; border-bottom: 1px solid var(--gray-100); font-size: 12px; }
.pexp-mini th { font-size: 10px; text-transform: uppercase; letter-spacing: .08em; color: var(--gray-500); }
.pexp-mini .num { text-align: right; font-variant-numeric: tabular-nums; }
.vtag { display: inline-block; font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 999px; white-space: nowrap; }
.vtag-hi { background: #1761A0; color: #fff; } .vtag-up { background: #dbe9f9; color: #0D3A66; }
.vtag-mid { background: var(--gray-100); color: var(--gray-700); } .vtag-dn { background: #fbe1e1; color: #8f1d1c; }
.vtag-lo { background: #e34948; color: #fff; } .vtag-nd { background: transparent; color: var(--gray-500); border: 1px dashed #d8d8dc; }
.vtag-keep { background: #eef4ff; color: var(--blue-800); margin-left: 6px; vertical-align: 1px; }
.tt-card { border: 1px solid var(--gray-200); border-radius: 10px; padding: 12px 14px; margin-bottom: 12px; background: #fff; }
.tt-meta { display: flex; justify-content: space-between; gap: 10px; font-size: 12px; color: var(--gray-600); margin-bottom: 8px; flex-wrap: wrap; }
.tt-verdict { font-weight: 700; border-radius: 999px; padding: 2px 10px; }
.tv-win { background: #dbe9f9; color: #0D3A66; } .tv-loss { background: #fbe1e1; color: #8f1d1c; } .tv-even { background: var(--gray-100); color: var(--gray-700); }
.tt-sides { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.tt-head { font-weight: 700; color: var(--blue-800); font-size: 13.5px; margin-bottom: 4px; display: flex; justify-content: space-between; gap: 8px; }
.tt-tot { color: #1d1d1f; font-variant-numeric: tabular-nums; }
.tt-p { display: flex; justify-content: space-between; gap: 8px; font-size: 13px; padding: 3px 0; border-bottom: 1px solid var(--gray-100); }
.tt-pts { font-variant-numeric: tabular-nums; white-space: nowrap; }
.db-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; margin-bottom: 18px; }
.db-grid { display: grid; gap: 3px; min-width: 980px; font-size: 11px; }
.db-h { font-size: 11px; font-weight: 700; color: var(--blue-800); text-align: center; padding: 4px 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.db-r { font-size: 11px; font-weight: 700; color: var(--gray-500); display: flex; align-items: center; justify-content: flex-end; padding-right: 4px; white-space: nowrap; }
.db-c { border-radius: 5px; padding: 4px 5px; min-height: 50px; background: var(--gray-100); line-height: 1.25; overflow: hidden; }
.db-c.dark { color: #fff; } .db-c.dark .db-s { color: rgba(255,255,255,.85); }
.db-c.keeper { box-shadow: inset 0 0 0 1.5px rgba(13,58,102,.45); }
.db-n { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.db-s { color: rgba(0,0,0,.6); font-size: 10px; }
.db-m { font-size: 10px; font-weight: 700; color: rgba(0,0,0,.72); display: flex; justify-content: space-between; gap: 4px; }
.db-f { font-variant-numeric: tabular-nums; font-weight: 700; }
.db-c.dark .db-m { color: #fff; }
.db-sep { grid-column: 1 / -1; font-size: 10.5px; text-transform: uppercase; letter-spacing: .08em; color: var(--gray-500); padding: 8px 0 2px; }
.upd { margin: 30px 0 10px; font-size: 12px; color: var(--gray-600); border-top: 1px solid var(--gray-200); padding-top: 10px; }
.upd summary { cursor: pointer; list-style: none; display: flex; align-items: center; gap: 8px; }
.upd summary::-webkit-details-marker { display: none; }
.upd-dot { width: 8px; height: 8px; border-radius: 50%; background: #16a34a; display: inline-block; flex: none; }
.upd-body { padding: 8px 16px; line-height: 1.7; }
.upd-h { margin-top: 6px; font-weight: 700; color: var(--gray-700); }
.upd ul { margin: 2px 0 6px 16px; padding: 0; } .upd li span { color: var(--gray-500); font-variant-numeric: tabular-nums; margin-right: 6px; }
.mu-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 10px; margin-bottom: 8px; }
.mu-card { border: 1px solid var(--gray-200); border-radius: 10px; padding: 10px 12px; background: #fff; }
.mu-side { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 2px 10px; align-items: center; padding: 3px 0; }
.mu-team { min-width: 0; }
.mu-team a { font-weight: 700; color: var(--blue-800); text-decoration: none; }
.mu-team .sub-line { display: block; font-size: 11px; color: var(--gray-500); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mu-pts { text-align: right; font-size: 18px; font-weight: 700; font-variant-numeric: tabular-nums; }
.mu-pts .proj { display: block; font-size: 10.5px; font-weight: 500; color: var(--gray-500); }
.mu-side.win .mu-pts { color: var(--blue-800); }
.mu-bar { height: 4px; border-radius: 2px; background: #f2a3a3; overflow: hidden; margin: 6px 0 2px; }
.mu-bar i { display: block; height: 100%; background: #1761A0; }
.mu-foot { display: flex; justify-content: space-between; font-size: 10.5px; color: var(--gray-500); }
"""

FEAT_JS = r"""
(function(){
  const esc = s => String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
  const PC = window.WG_PC || [], BY = {};
  PC.forEach(p => BY[p.id] = p);
  const cnt = (n, w) => n + ' ' + w + (n === 1 ? '' : 's');
  const rk = (p, l) => l.rk ? p.p + l.rk : '';
  function owner(p) { return p.own ? `<span class="ps-owner">On ${esc(p.own)}'s roster</span>` : '<span class="ps-owner ps-owner-none">Not on a roster now</span>'; }
  function bars(arr, max) {
    const W = 180, H = 64, n = 18, sw = W / n, bw = sw * .64;
    let s = '';
    for (let i = 0; i < n; i++) {
      const v = arr && arr[i], x = i * sw + (sw - bw) / 2;
      if (v == null || v <= 0) { s += `<rect x="${x.toFixed(1)}" y="${H - 3}" width="${bw.toFixed(1)}" height="1.5" fill="#e3e3e6" data-tip="Week ${i + 1}: ${v == null ? 'not rostered' : '0 pts'}"/>`; continue; }
      const h = Math.max(2, v / max * (H - 8));
      s += `<rect x="${x.toFixed(1)}" y="${(H - 2 - h).toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" rx="1.5" fill="#1761A0" data-tip="Week ${i + 1}: ${v} pts"/>`;
    }
    return `<svg class="pc2-bars" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">${s}</svg>`;
  }
  function lineage(p, maxN) {
    if (!p.lin.length) return '<div class="tl-via">No draft or transaction history on Yahoo.</div>';
    const parts = [];
    const lin = maxN && p.lin.length > maxN ? p.lin.slice(-maxN) : p.lin;
    if (lin.length < p.lin.length) parts.push(`<div class="lineage-break"><span class="lineage-break-txt" style="color:#8e8e93">${p.lin.length - lin.length} earlier stint${p.lin.length - lin.length > 1 ? 's' : ''}</span></div>`);
    lin.forEach((x, i) => {
      const [m, how, y0, y1, kept, end] = x;
      const cls = how.startsWith('Drafted') ? 'drafted' : how === 'Kept' ? 'kept' : how.startsWith('Traded') ? 'trade' : how.startsWith('Waivers') ? 'waiver' : 'free-agent';
      const yrs = y0 === y1 ? y0 : `${y0}&ndash;${y1}`;
      parts.push(`<div class="lineage-node lineage-${cls}${end == null ? ' lineage-now' : ''}"><div class="lineage-date">${yrs}</div>` +
        `<div class="lineage-manager">${esc(m)}</div><div class="lineage-method">${esc(how)}</div>` +
        (kept ? `<div class="lineage-detail">Kept ${kept} more time${kept > 1 ? 's' : ''}</div>` : '') +
        (end == null ? '<div class="lineage-tag">On this roster now</div>' : '') + '</div>');
      if (i < lin.length - 1 || end) {
        if (end === 'traded') parts.push('<div class="lineage-arrow">&rarr;</div>');
        else if (end) parts.push(`<div class="lineage-break"><span class="lineage-break-x">&#10007;</span><span class="lineage-break-txt">${end === 'dropped' ? 'dropped' : 'not kept'}</span></div>`);
      }
    });
    return `<div class="lineage-flow">${parts.join('')}</div>`;
  }
  function seasonsTable(p, n) {
    const rows = p.s.slice(0, n || 99).map(l => `<tr><td>${l.y}</td><td>${esc(l.m.join(', '))}</td><td>${esc(l.how)}</td>` +
      `<td class="num">${l.pts.toFixed(1)}</td><td class="num">${l.g}</td><td class="num">${rk(p, l)}</td></tr>`).join('');
    return `<table class="roster"><thead><tr><th>Season</th><th>Manager</th><th>How</th><th class="num">Pts</th><th class="num">G</th><th class="num">Rank</th></tr></thead><tbody>${rows}</tbody></table>`;
  }
  function card(p) {
    const yrs = Object.keys(p.wk).map(Number).sort((a, b) => b - a);
    const max = Math.max(1, ...yrs.flatMap(y => p.wk[y].filter(v => v != null)));
    const cols = yrs.map(y => {
      const l = p.s.find(x => x.y === y) || {pts: 0, g: 0, m: []};
      const nb = (p.nb[y] || []).map(([r, q, v]) => `<tr class="${q === p.id ? 'self' : ''}"><td>${p.p}${r}</td><td>${esc(BY[q] ? BY[q].n : '?')}</td><td>${v.toFixed(1)}</td></tr>`).join('');
      return `<div class="pc2-yr"><div class="pc2-yrhead"><b>${y}</b><span class="pc2-rank">${rk(p, l)}</span><span>${l.pts.toFixed(1)} pts</span><span class="tl-via">${cnt(l.g, 'game')}</span></div>` +
        `<div class="pc2-sub">${esc(l.m.join(' → '))}${l.how ? ' · ' + esc(l.how) : ''}</div>${bars(p.wk[y], max)}` +
        (nb ? `<table class="pc2-nb">${nb}</table>` : '') + '</div>';
    }).join('');
    const ev = p.ev.map(([d, t]) => `<div class="ps-event"><span class="ps-event-date">${esc(d)}</span><span class="ps-event-desc">${esc(t)}</span></div>`).join('') || '<div class="ps-event-empty">No moves recorded.</div>';
    return `<div class="pc2"><div class="pc2-head"><div><div class="pc2-name">${esc(p.n)}</div>` +
      `<div class="pc2-meta">${esc(p.p)}${p.nfl ? ' · ' + esc(p.nfl) : ''} · ${p.t.toLocaleString(undefined, {maximumFractionDigits: 0})} pts on WG rosters across ${cnt(p.s.length, 'season')}</div></div>${owner(p)}</div>` +
      (cols ? `<div class="pc2-label">Last ${yrs.length === 1 ? 'season' : yrs.length + ' seasons'} in the league, week by week</div><div class="pc2-years">${cols}</div>` : '') +
      `<div class="pc2-label">Ownership lineage</div>${lineage(p)}` +
      `<div class="pc2-two"><div><div class="pc2-label">Latest moves</div>${ev}</div><div><div class="pc2-label">Every season</div><div class="table-scroll">${seasonsTable(p)}</div></div></div></div>`;
  }
  const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9 ]/g, '');
  PC.forEach(p => p._k = norm(p.n));
  function find(q, n) { q = norm(q.trim()); if (q.length < 2) return []; return PC.filter(p => p._k.includes(q)).sort((a, b) => b.t - a.t).slice(0, n); }

  // ---------- search
  const box = document.getElementById('wg-ps'), out = document.getElementById('wg-ps-out');
  if (box) box.addEventListener('input', () => {
    const hits = find(box.value, 8);
    out.innerHTML = box.value.trim().length < 2 ? '' : (hits.map(card).join('') || '<p class="note">No player by that name has been on a WG roster since 2012.</p>');
  });

  // ---------- compare
  const COLS = ['#1761A0', '#e1b523', '#2f9e8f'];
  const cbox = document.getElementById('wg-cmp'), sugg = document.getElementById('wg-cmp-sugg'), chips = document.getElementById('wg-cmp-chips'), cout = document.getElementById('wg-cmp-out');
  let picked = [];
  function drawCompare() {
    chips.innerHTML = picked.map((id, i) => `<span class="cmp-chip" style="background:${COLS[i]}">${esc(BY[id].n)}<button type="button" data-x="${id}" aria-label="Remove">&times;</button></span>`).join('');
    chips.querySelectorAll('button').forEach(b => b.addEventListener('click', () => { picked = picked.filter(x => x != b.dataset.x); drawCompare(); }));
    if (!picked.length) { cout.innerHTML = '<p class="note">Search above and pick up to three players. Try two receivers you are deciding between.</p>'; return; }
    const ps = picked.map(id => BY[id]);
    const years = [...new Set(ps.flatMap(p => p.s.map(l => l.y)))].sort((a, b) => a - b);
    const y0 = years[0], y1 = years[years.length - 1], hi = Math.max(1, ...ps.flatMap(p => p.s.map(l => l.pts)));
    const W = 760, H = 240, L = 44, R = 16, T = 12, B = 26, px = y => L + (W - L - R) * (years.length > 1 ? (y - y0) / (y1 - y0) : .5), py = v => T + (H - T - B) * (1 - v / hi);
    let svg = [0, .25, .5, .75, 1].map(f => `<line x1="${L}" x2="${W - R}" y1="${py(hi * f)}" y2="${py(hi * f)}" stroke="#ebebed"/><text x="${L - 6}" y="${py(hi * f) + 4}" text-anchor="end" font-size="11" fill="#8e8e93">${Math.round(hi * f)}</text>`).join('');
    svg += years.map(y => `<text x="${px(y)}" y="${H - 8}" text-anchor="middle" font-size="11" fill="#8e8e93">${String(y).slice(2)}</text>`).join('');
    ps.forEach((p, i) => {
      const pts = p.s.slice().sort((a, b) => a.y - b.y);
      const segs = []; let cur = [];
      pts.forEach((l, k) => { if (k && l.y !== pts[k - 1].y + 1) { segs.push(cur); cur = []; } cur.push(l); }); segs.push(cur);
      segs.forEach(sg => { if (sg.length > 1) svg += `<path d="M${sg.map(l => px(l.y).toFixed(1) + ',' + py(l.pts).toFixed(1)).join(' L')}" fill="none" stroke="${COLS[i]}" stroke-width="2.5"/>`; });
      svg += pts.map(l => `<circle cx="${px(l.y)}" cy="${py(l.pts)}" r="4" fill="${COLS[i]}" stroke="#fff" stroke-width="1.5" data-tip="<b>${esc(p.n)}</b> ${l.y}<br>${l.pts.toFixed(1)} pts, ${p.p}${l.rk || ''}<br>${esc(l.m.join(', '))}"/>`).join('');
    });
    const chart = `<div class="viz"><div class="viz-title">Season points on WG rosters</div><div class="viz-sub">Rostered weeks only. Gaps are seasons he wasn't on a roster.</div><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Season points comparison">${svg}</svg></div>`;
    const maxw = Math.max(1, ...ps.flatMap(p => Object.values(p.wk).flat().filter(v => v != null)));
    const cols = ps.map((p, i) => {
      const last = p.s[0] || {}, best = p.s.reduce((a, b) => (b.pts > (a ? a.pts : -1) ? b : a), null) || {};
      const ly = Object.keys(p.wk).map(Number).sort((a, b) => b - a)[0];
      return `<div class="cmp-col" style="border-top-color:${COLS[i]}"><h3>${esc(p.n)}</h3><div class="pc2-meta">${esc(p.p)} · ${esc(p.nfl)}</div>${owner(p)}` +
        `<div class="cmp-kv"><div><div class="k">${last.y || ''} pts</div><div class="v">${(last.pts || 0).toFixed(1)}</div></div>` +
        `<div><div class="k">${last.y || ''} rank</div><div class="v">${rk(p, last) || '-'}</div></div>` +
        `<div><div class="k">Per game</div><div class="v">${last.g ? (last.pts / last.g).toFixed(1) : '-'}</div></div>` +
        `<div><div class="k">Best season</div><div class="v">${best.y || '-'}</div></div></div>` +
        (ly ? `<div class="pc2-label">${ly} week by week</div>${bars(p.wk[ly], maxw)}` : '') +
        `<div class="pc2-label">Lineage (latest)</div>${lineage(p, 3)}<div class="pc2-label">Seasons</div><div class="table-scroll">${seasonsTable(p, 6)}</div></div>`;
    }).join('');
    cout.innerHTML = chart + `<div class="cmp-cols">${cols}</div>`;
    if (window.wgCharts) { wgCharts.wrap(cout); setTimeout(wgCharts.cue, 30); }
  }
  if (cbox) {
    cbox.addEventListener('input', () => {
      const hits = find(cbox.value, 8).filter(p => !picked.includes(p.id));
      sugg.hidden = !hits.length;
      sugg.innerHTML = hits.map(p => `<div class="pc-sugg-item" data-id="${p.id}"><b>${esc(p.n)}</b><span class="pc-sugg-meta">${esc(p.p)} · ${p.s[0] ? p.s[0].y : ''}</span><span class="pc-sugg-owner">${esc(p.own || '')}</span></div>`).join('');
      sugg.querySelectorAll('.pc-sugg-item').forEach(it => it.addEventListener('click', () => {
        if (picked.length >= 3) picked.shift();
        picked.push(+it.dataset.id); cbox.value = ''; sugg.hidden = true; drawCompare();
      }));
    });
    drawCompare();
  }

  // ---------- team roster: tap a row for past seasons
  document.querySelectorAll('.pexp-row').forEach(row => row.addEventListener('click', ev => {
    if (ev.target.closest('a')) return;
    const det = row.nextElementSibling, btn = row.querySelector('.pexp-btn'), p = BY[row.dataset.pexp];
    if (!det) return;
    if (det.hidden) {
      const td = det.firstElementChild;
      if (!td.dataset.done) {
        td.innerHTML = p ? `<div class="pexp-mini">${lineage(p, 4)}<div class="table-scroll">${seasonsTable(p, 5)}</div></div>` : '<span class="tl-via">No history.</span>';
        td.dataset.done = '1';
      }
      det.hidden = false; btn && btn.classList.add('open');
    } else { det.hidden = true; btn && btn.classList.remove('open'); }
  }));

  // ---------- draft board grid (uses the value board's data)
  const dsel = document.getElementById('db-season'), grid = document.getElementById('db-grid');
  if (dsel && grid && window.WG_VB) {
    let mode = 'z';
    const POSC = {QB: '#e1b523', RB: '#1761A0', WR: '#86b6ef', TE: '#2f9e8f', K: '#c5c9d2', DEF: '#606C71'};
    function mix(a, b, t) { const p = c => [1,3,5].map(i => parseInt(c.slice(i, i+2), 16)); const x = p(a), y = p(b);
      return '#' + x.map((v, i) => Math.round(v + (y[i] - v) * t).toString(16).padStart(2, '0')).join(''); }
    function zf(z) { if (z == null) return '#f0efec'; const t = Math.max(-1, Math.min(1, z / 2));
      return t >= 0 ? (t < .5 ? mix('#f0efec', '#86b6ef', t * 2) : mix('#86b6ef', '#1761A0', (t - .5) * 2))
                    : (-t < .5 ? mix('#f0efec', '#f2a3a3', -t * 2) : mix('#f2a3a3', '#e34948', (-t - .5) * 2)); }
    function draw() {
      const D = window.WG_VB[dsel.value]; if (!D) { grid.innerHTML = ''; return; }
      const picks = D.r.filter(r => r[3] < 2);
      const byRd = {};
      picks.forEach(r => (byRd[r[4]] = byRd[r[4]] || []).push(r));
      Object.values(byRd).forEach(a => a.sort((x, y) => x[5] - y[5]));
      const rounds = Object.keys(byRd).map(Number).sort((a, b) => a - b);
      const r1 = byRd[rounds[0]] || [], n = r1.length;
      const order = r1.map(r => r[2]);
      // snake if the last pick of round 1 also makes the first pick of round 2
      const snake = byRd[rounds[1]] && byRd[rounds[1]][0] && r1.length && byRd[rounds[1]][0][2] === r1[n - 1][2];
      grid.style.gridTemplateColumns = `44px repeat(${n}, minmax(0, 1fr))`;
      const played = picks.filter(r => r[6] >= 2).map(r => r[8]);
      const fsd = Math.sqrt(played.reduce((a, v) => a + v * v, 0) / Math.max(played.length, 1)) || 1;   // spread of FPOR around replacement
      let h = '<div></div>' + order.map((m, i) => `<div class="db-h">Slot ${i + 1}</div>`).join('');
      rounds.forEach(rd => {
        if (rd === D.k1) h += `<div class="db-sep">Keepers (rounds ${D.k1}+), placed at the back of the draft</div>`;
        h += `<div class="db-r">Rd ${rd}</div>`;
        const row = byRd[rd].slice(0, n);
        const cells = Array(n).fill(null);
        row.forEach((r, i) => { cells[snake && (rd - rounds[0]) % 2 ? n - 1 - i : i] = r; });
        cells.forEach((r, col) => {
          if (!r) { h += '<div class="db-c"></div>'; return; }
          const fz = r[6] >= 2 ? r[8] / fsd : null;
          const bg = mode === 'z' ? zf(r[10]) : mode === 'f' ? zf(fz) : POSC[r[1]] || '#c5c9d2';
          const dark = mode === 'z' ? (r[10] != null && Math.abs(r[10]) > 1.3) : mode === 'f' ? (fz != null && Math.abs(fz) > 1.3) : ['RB', 'DEF'].includes(r[1]);
          const fp = `${r[8] >= 0 ? '+' : ''}${Math.round(r[8])}`;
          const via = '';
          const tip = `<b>${esc(r[0])}</b> ${r[1]}<br>${esc(r[2])}, ${r[3] ? 'keeper' : 'pick ' + r[5]}<br>${r[7]} pts in ${r[6]} g<br>FPOR ${r[8] >= 0 ? '+' : ''}${r[8]}` + (r[10] != null ? `<br>${r[10] >= 0 ? '+' : ''}${r[10]} sd vs ${r[3] ? 'avg keeper' : 'slot'}` : '');
          h += `<div class="db-c${dark ? ' dark' : ''}${r[3] ? ' keeper' : ''}" style="background:${bg}" data-tip="${esc(tip)}"><div class="db-n">${esc(r[0])}</div><div class="db-s">${r[1]} \u00b7 ${r[3] ? 'K' : '#' + r[5]}</div><div class="db-m">${esc(r[2])}<span class="db-f">${fp}</span></div></div>`;
        });
      });
      grid.innerHTML = h;
      document.getElementById('db-legend').innerHTML = mode === 'z'
        ? '<div class="vb-legend"><span>Below the slot</span><span class="vb-legend-bar"></span><span>Above the slot</span><span class="tl-via">Keepers are shaded against the average keeper. The number in each square is the player\'s FPOR.</span></div>'
        : mode === 'f'
        ? '<div class="vb-legend"><span>Below replacement</span><span class="vb-legend-bar"></span><span>Above replacement</span><span class="tl-via">Raw FPOR, no adjustment for draft slot. Gray = about replacement level or under 2 games.</span></div>'
        : '<div class="viz-legend">' + Object.entries(POSC).map(([k, c]) => `<span><i style="background:${c}"></i>${k}</span>`).join('') + '</div>';
    }
    dsel.addEventListener('change', draw);
    document.querySelectorAll('#db-color .vb-chip').forEach(b => b.addEventListener('click', () => {
      mode = b.dataset.c; document.querySelectorAll('#db-color .vb-chip').forEach(x => x.classList.toggle('is-on', x === b)); draw(); }));
    draw();
  }

  // ---------- live matchups
  const mu = document.getElementById('live-mu');
  if (mu && window.WG_LIVE) {
    const T = window.WG_TIDS;
    function side(s, win) {
      const m = T.m[s.tid] || s.team, sl = T.s[s.tid];
      return `<div class="mu-side${win ? ' win' : ''}"><div class="mu-team"><a href="#" data-target="team-${sl}">${esc(m)}</a>` +
        `<span class="sub-line">${esc(s.team)}${s.rec ? ' · ' + esc(s.rec) : ''}${s.rank ? ' · #' + s.rank : ''}</span></div>` +
        `<div class="mu-pts">${(+s.pts).toFixed(2)}<span class="proj">proj ${(+s.proj).toFixed(1)}</span></div></div>`;
    }
    function draw(doc) {
      const st = {final: 'final', in_progress: 'in progress', upcoming: 'upcoming'}[doc.status] || doc.status;
      document.getElementById('live-h').textContent = `Week ${doc.week} matchups`;
      document.getElementById('live-meta').textContent = `${st} · updated ${doc.as_of}`;
      mu.innerHTML = doc.matchups.map(x => {
        const a = x.a, b = x.b, done = x.status === 'final';
        let pa = a.win_prob;
        if (pa == null && b.win_prob != null) pa = 1 - b.win_prob;
        if (pa == null) { const ea = (+a.pts) + Math.max(0, (+a.proj) - (+a.pts)) * (done ? 0 : 1), eb = (+b.pts) + Math.max(0, (+b.proj) - (+b.pts)) * (done ? 0 : 1); pa = ea + eb ? ea / (ea + eb) : .5; }
        const aw = done ? a.pts > b.pts : null, bw = done ? b.pts > a.pts : null;
        return `<div class="mu-card">${side(a, aw)}${side(b, bw)}<div class="mu-bar"><i style="width:${(pa * 100).toFixed(0)}%"></i></div>` +
          `<div class="mu-foot"><span>${done ? 'Final' : (a.win_prob != null || b.win_prob != null ? 'Yahoo win odds' : 'Share of projected total')}</span><span>${Math.round(pa * 100)}% / ${Math.round((1 - pa) * 100)}%</span></div></div>`;
      }).join('');
      mu.querySelectorAll('a[data-target]').forEach(a => a.addEventListener('click', ev => {
        ev.preventDefault(); const n = document.querySelector('.nav-link[data-target="' + a.dataset.target + '"]'); if (n) n.click(); }));
    }
    draw(window.WG_LIVE);
    if (location.protocol.startsWith('http')) fetch('scores.json', {cache: 'no-store'}).then(r => r.ok ? r.json() : null).then(d => {
      if (d && d.matchups && d.matchups.length && d.week >= window.WG_LIVE.week) draw(d);
    }).catch(() => {});
  }
})();
"""


# ---------------------------------------------------------------- head-to-head (added for Mike, 2026-11-09)

def h2h_games(L):
    """Every decided game between two managers: (season, week, kind, mgr_a, mgr_b, pts_a, pts_b).
    kind 'r' = regular season, 'p' = championship bracket. Consolation games are left out."""
    out, seen = [], set()
    for m in L.final_games(regular=True):
        a, b = m["team_season_id"], m["opponent_team_season_id"]
        if not b or (m["season"], m["week"], b, a) in seen:
            continue
        seen.add((m["season"], m["week"], a, b))
        out.append((m["season"], m["week"], "r", L.mgr(a), L.mgr(b), m["points"] or 0, m["opponent_points"] or 0))
    for g in L.bracket_games():
        out.append((g["season"], g["week"], "p", L.mgr(g["winner"]), L.mgr(g["loser"]), g["wpts"] or 0, g["lpts"] or 0))
    return sorted(out)


def h2h_summary(games, me, kinds=("r",)):
    """Per-opponent record for one manager."""
    by = defaultdict(list)
    for s, w, k, a, b, pa, pb in games:
        if k not in kinds:
            continue
        if a == me:
            by[b].append((s, w, pa, pb))
        elif b == me:
            by[a].append((s, w, pb, pa))
    rows = []
    for opp, gs in by.items():
        wins = sum(1 for g in gs if g[2] > g[3]); losses = sum(1 for g in gs if g[2] < g[3]); ties = len(gs) - wins - losses
        streak, last = 0, None
        for g in reversed(gs):
            r = "W" if g[2] > g[3] else "L" if g[2] < g[3] else "T"
            if last is None:
                last = r
            if r != last:
                break
            streak += 1
        rows.append({"opp": opp, "g": len(gs), "w": wins, "l": losses, "t": ties,
                     "pf": sum(g[2] for g in gs) / len(gs), "pa": sum(g[3] for g in gs) / len(gs),
                     "streak": f"{last}{streak}" if last else "", "last": gs[-1]})
    return sorted(rows, key=lambda r: (-(r["w"] + r["t"] / 2) / r["g"], -r["g"]))


def h2h_body(L, games):
    mgrs = sorted({g[3] for g in games} | {g[4] for g in games})
    ix = {m: i for i, m in enumerate(mgrs)}
    data = [[s, w, 1 if k == "p" else 0, ix[a], ix[b], round(pa, 2), round(pb, 2)] for s, w, k, a, b, pa, pb in games]
    opts = "".join(f'<option value="{i}"{" selected" if m == "Pete" else ""}>{e(m)}</option>' for i, m in enumerate(mgrs))
    yrs = sorted({g[0] for g in games})
    return (f'<div class="vb-filters"><div class="vb-filter vb-chips" id="h2h-kind">'
            '<button type="button" class="vb-chip is-on" data-k="r">Regular season</button>'
            '<button type="button" class="vb-chip" data-k="p">Playoffs</button>'
            '<button type="button" class="vb-chip" data-k="a">Both</button></div>'
            f'<label class="vb-filter">Manager <select id="h2h-mgr">{opts}</select></label></div>'
            '<div class="viz"><div class="viz-title">Every manager against every manager</div>'
            '<div class="viz-sub">Read across a row: that manager\'s record against each opponent. Blue = winning record, red = losing. '
            'Tap a cell for the details, or a name to make it the selected manager.</div>'
            '<div class="h2h-scroll"><div id="h2h-grid" class="h2h-grid"></div></div>'
            '<div class="viz-legend"><span><i style="background:#1761A0"></i>Owns the matchup</span><span><i style="background:#f0efec;border:1px solid #ddd"></i>Even</span>'
            '<span><i style="background:#e34948"></i>Owned by them</span><span class="tl-via">Fewer than 3 games is shown faint.</span></div></div>'
            '<h2 id="h2h-h"></h2><div id="h2h-detail"></div>'
            f'<p class="note">Every decided game on Yahoo, {yrs[0]} to {yrs[-1]} (Yahoo history before 2012 is not loaded). '
            'Playoffs means the championship bracket only; consolation games are left out. Brad (2012 to 2018) and John (2019 on) '
            'are listed separately even though John took over Brad\'s team.</p>'
            f'<script>window.WG_H2H = {jdump({"m": mgrs, "g": data})};</script>')


def team_h2h_table(L, games, manager, mlink, table):
    rows = h2h_summary(games, manager, ("r",))
    if not rows:
        return ""
    trs = []
    for r in rows:
        s, w, pf, pa = r["last"]
        res = "W" if pf > pa else "L" if pf < pa else "T"
        trs.append([mlink(r["opp"]), str(r["g"]), f'{r["w"]}-{r["l"]}' + (f'-{r["t"]}' if r["t"] else ""),
                    f'{(r["w"] + r["t"] / 2) / r["g"]:.3f}'.lstrip("0"), f'{r["pf"]:.1f}-{r["pa"]:.1f}', r["streak"],
                    f'{s} wk {w}: {res} {pf:.1f}-{pa:.1f}'])
    return ("<h2>Head-to-head (regular season)</h2>" +
            table(["Opponent", "Games", "Record", "Win %", "Avg score", "Streak", "Last meeting"], trs, num=(1, 3)) +
            '<p class="note">Full grid, playoffs and every meeting on the <a href="#" data-target="h2h">Head-to-head</a> page.</p>')


H2H_CSS = """
.h2h-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.h2h-grid { display: grid; gap: 3px; min-width: 760px; font-size: 12px; margin: 8px 0 6px; }
.h2h-h { font-size: 11px; font-weight: 700; color: var(--blue-800); text-align: center; padding: 4px 0; cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.h2h-r { font-size: 12px; font-weight: 600; color: #1d1d1f; display: flex; align-items: center; justify-content: flex-end; padding-right: 6px; cursor: pointer; white-space: nowrap; }
.h2h-c { border-radius: 5px; text-align: center; padding: 6px 2px; font-variant-numeric: tabular-nums; font-weight: 600; cursor: pointer; line-height: 1.15; }
.h2h-c small { display: block; font-size: 9.5px; font-weight: 500; opacity: .8; }
.h2h-c.dark { color: #fff; }
.h2h-c.faint { opacity: .45; }
.h2h-c.self { background: repeating-linear-gradient(45deg, #f4f4f6, #f4f4f6 4px, #ebebed 4px, #ebebed 8px); cursor: default; }
.h2h-c.on, .h2h-r.on, .h2h-h.on { outline: 2px solid #0D3A66; outline-offset: -1px; }
.h2h-rowsel { background: #eef4ff; border-radius: 4px; }
.h2h-bar { display: inline-block; width: 70px; height: 8px; background: #f2a3a3; border-radius: 4px; overflow: hidden; vertical-align: middle; margin-right: 6px; }
.h2h-bar i { display: block; height: 100%; background: #1761A0; }
.h2h-games { font-size: 12px; color: var(--gray-600); line-height: 1.6; }
.h2h-games b.w { color: #0D3A66; } .h2h-games b.l { color: #b42318; }
"""

H2H_JS = r"""
(function(){
  const D = window.WG_H2H, grid = document.getElementById('h2h-grid');
  if (!D || !grid) return;
  const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
  const M = D.m, n = M.length, sel = document.getElementById('h2h-mgr');
  let kind = 'r', me = +sel.value, focus = null;
  function mix(a, b, t) { const p = c => [1,3,5].map(i => parseInt(c.slice(i, i+2), 16)); const x = p(a), y = p(b);
    return '#' + x.map((v, i) => Math.round(v + (y[i] - v) * t).toString(16).padStart(2, '0')).join(''); }
  function fill(p) { const t = Math.max(-1, Math.min(1, (p - .5) / .3));
    return t >= 0 ? (t < .5 ? mix('#f0efec', '#86b6ef', t * 2) : mix('#86b6ef', '#1761A0', (t - .5) * 2))
                  : (-t < .5 ? mix('#f0efec', '#f2a3a3', -t * 2) : mix('#f2a3a3', '#e34948', (-t - .5) * 2)); }
  function games(a, b) {
    return D.g.filter(g => (kind === 'a' || (kind === 'p') === !!g[2]) && ((g[3] === a && g[4] === b) || (g[3] === b && g[4] === a)))
      .map(g => g[3] === a ? {s: g[0], w: g[1], p: g[2], f: g[5], x: g[6]} : {s: g[0], w: g[1], p: g[2], f: g[6], x: g[5]});
  }
  function rec(gs) { const w = gs.filter(g => g.f > g.x).length, l = gs.filter(g => g.f < g.x).length; return {w, l, t: gs.length - w - l, g: gs.length}; }
  const pct = r => r.g ? (r.w + r.t / 2) / r.g : .5;
  const rs = r => `${r.w}-${r.l}${r.t ? '-' + r.t : ''}`;
  function drawGrid() {
    grid.style.gridTemplateColumns = `76px repeat(${n}, minmax(0, 1fr))`;
    let h = '<div></div>' + M.map((m, j) => `<div class="h2h-h${j === me ? ' on' : ''}" data-m="${j}">${esc(m)}</div>`).join('');
    M.forEach((a, i) => {
      h += `<div class="h2h-r${i === me ? ' on' : ''}" data-m="${i}">${esc(a)}</div>`;
      M.forEach((b, j) => {
        if (i === j) { h += '<div class="h2h-c self"></div>'; return; }
        const r = rec(games(i, j));
        if (!r.g) { h += '<div class="h2h-c" style="background:#fafafa;color:#c5c9d2">-</div>'; return; }
        const p = pct(r), dark = Math.abs(p - .5) > .2;
        const tip = `<b>${esc(a)} vs ${esc(b)}</b><br>${rs(r)} in ${r.g} game${r.g > 1 ? 's' : ''} (${(p * 100).toFixed(0)}%)`;
        h += `<div class="h2h-c${dark ? ' dark' : ''}${r.g < 3 ? ' faint' : ''}${i === me && j === focus ? ' on' : ''}" style="background:${fill(p)}" data-a="${i}" data-b="${j}" data-tip="${esc(tip)}">${rs(r)}<small>${(p * 100).toFixed(0)}%</small></div>`;
      });
    });
    grid.innerHTML = h;
    grid.querySelectorAll('[data-m]').forEach(el => el.addEventListener('click', () => { me = +el.dataset.m; sel.value = me; focus = null; drawAll(); }));
    grid.querySelectorAll('.h2h-c[data-a]').forEach(el => el.addEventListener('click', () => { me = +el.dataset.a; focus = +el.dataset.b; sel.value = me; drawAll(); }));
  }
  function drawDetail() {
    const label = {r: 'regular season', p: 'playoffs', a: 'regular season and playoffs'}[kind];
    document.getElementById('h2h-h').textContent = `${M[me]} against everyone (${label})`;
    const rows = M.map((b, j) => j === me ? null : {j, gs: games(me, j)}).filter(x => x && x.gs.length)
      .map(x => Object.assign(x, rec(x.gs))).sort((a, b) => pct(b) - pct(a) || b.g - a.g);
    if (!rows.length) { document.getElementById('h2h-detail').innerHTML = '<p class="note">No games of this kind.</p>'; return; }
    const tot = rows.reduce((t, r) => ({w: t.w + r.w, l: t.l + r.l, t: t.t + r.t, g: t.g + r.g}), {w: 0, l: 0, t: 0, g: 0});
    const body = rows.map(r => {
      const gs = r.gs, last = gs[gs.length - 1];
      let st = 0, k = null; for (let i = gs.length - 1; i >= 0; i--) { const x = gs[i].f > gs[i].x ? 'W' : gs[i].f < gs[i].x ? 'L' : 'T'; if (k === null) k = x; if (x !== k) break; st++; }
      const best = gs.reduce((a, g) => (g.f - g.x > a.f - a.x ? g : a)), worst = gs.reduce((a, g) => (g.f - g.x < a.f - a.x ? g : a));
      const pf = gs.reduce((s, g) => s + g.f, 0) / gs.length, pa = gs.reduce((s, g) => s + g.x, 0) / gs.length;
      const open = r.j === focus;
      const list = open ? `<tr class="h2h-rowsel"><td colspan="8"><div class="h2h-games">` + gs.slice().reverse().map(g =>
        `${g.s} wk ${g.w}${g.p ? ' (playoffs)' : ''}: <b class="${g.f > g.x ? 'w' : 'l'}">${g.f > g.x ? 'W' : g.f < g.x ? 'L' : 'T'}</b> ${g.f.toFixed(2)}-${g.x.toFixed(2)}`).join(' &middot; ') + '</div></td></tr>' : '';
      return `<tr class="${open ? 'h2h-rowsel' : ''}" data-j="${r.j}" style="cursor:pointer"><td><b>${esc(M[r.j])}</b></td><td class="num">${r.g}</td>` +
        `<td class="num"><span class="h2h-bar"><i style="width:${(pct(r) * 100).toFixed(0)}%"></i></span><b>${rs(r)}</b></td><td class="num">${pct(r).toFixed(3).replace(/^0/, '')}</td>` +
        `<td class="num">${pf.toFixed(1)}-${pa.toFixed(1)}</td><td>${k}${st}</td>` +
        `<td class="tl-small">${best.f > best.x ? `+${(best.f - best.x).toFixed(1)} (${best.s})` : '-'}</td>` +
        `<td class="tl-small">${worst.f < worst.x ? `${(worst.f - worst.x).toFixed(1)} (${worst.s})` : '-'}</td></tr>` + list;
    }).join('');
    document.getElementById('h2h-detail').innerHTML = `<p class="note">Overall: <b>${rs(tot)}</b> (${pct(tot).toFixed(3).replace(/^0/, '')}). Tap a row to see every meeting.</p>` +
      `<div class="table-scroll"><table class="roster"><thead><tr><th>Opponent</th><th class="num">Games</th><th class="num">Record</th><th class="num">Win %</th>` +
      `<th class="num">Avg score</th><th>Streak</th><th>Biggest win</th><th>Worst loss</th></tr></thead><tbody>${body}</tbody></table></div>`;
    document.querySelectorAll('#h2h-detail tr[data-j]').forEach(tr => tr.addEventListener('click', () => { focus = focus === +tr.dataset.j ? null : +tr.dataset.j; drawAll(); }));
  }
  function drawAll() { drawGrid(); drawDetail(); }
  sel.addEventListener('change', () => { me = +sel.value; focus = null; drawAll(); });
  document.querySelectorAll('#h2h-kind .vb-chip').forEach(b => b.addEventListener('click', () => {
    kind = b.dataset.k; document.querySelectorAll('#h2h-kind .vb-chip').forEach(x => x.classList.toggle('is-on', x === b)); drawAll(); }));
  drawAll();
})();
"""
