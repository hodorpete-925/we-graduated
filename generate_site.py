"""
generate_site.py - builds index.html, the We Graduated league site.

Read-only against fantasy.db. Output: index.html in this folder (a single
self-contained page, like I Yearn's dashboard). Never edit index.html by
hand; change this file, wg_data.py or wg_content.py and rerun.

    venv\\Scripts\\python.exe generate_site.py
"""

import base64
import html
import json
from datetime import datetime
from pathlib import Path

import wg_charts as V
import wg_content as C
import wg_data as D
import wg_dynamic as DY
import wg_features as F
from wg_template import CSS, FEEDBACK, JS

HERE = Path(__file__).parent
OUT = HERE / "index.html"
LOGO = HERE / "assets" / "logo.png"
OFFERS = HERE / "faab_offers.json"
LEAGUE = "We Graduated"

e = lambda s: html.escape(str(s if s is not None else ""))


def f1(x):
    return "" if x is None else f"{x:,.1f}"


def f2(x):
    return "" if x is None else f"{x:,.2f}"


def rec(w, l, t=0):
    return f"{w}-{l}" + (f"-{t}" if t else "")


def pct(w, l, t=0):
    g = w + l + t
    return f"{(w + 0.5 * t) / g:.3f}".lstrip("0") if g else ""


def mlink(name):
    return f'<a href="#" data-target="team-{D.slug(name)}">{e(name)}</a>'


def table(headers, rows, cls="roster", num=()):
    """headers: list of str; rows: list of lists (cells already HTML); num: column indexes to right-align."""
    th = "".join(f'<th class="{"num" if i in num else ""}">{h}</th>' for i, h in enumerate(headers))
    body = "".join("<tr>" + "".join(f'<td class="{"num" if i in num else ""}">{c}</td>' for i, c in enumerate(r))
                   + "</tr>" for r in rows)
    return f'<div class="table-scroll"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def section(sid, title, sub, body, eyebrow="", hidden=True):
    eb = f'<div class="eyebrow">{eyebrow}</div>' if eyebrow else ""
    return f"""
    <section class="team-section" id="{sid}"{" hidden" if hidden else ""}>
      {eb}<h1 class="team-name">{title}</h1>
      <p class="manager-name">{sub}</p>
      {body}
    </section>"""


def kpis(items):
    return '<div class="kpis">' + "".join(
        f'<div class="kpi"><div class="k">{k}</div><div class="v{" kpi-text" if len(str(v)) > 9 else ""}">{v}</div></div>'
        for k, v in items) + "</div>"


def collapsible(title, meta, body, open_=False):
    return f"""<div class="year-collapsible{" open" if open_ else ""}">
      <div class="year-collapsible-header"><span class="year-chev">&#9656;</span>
        <span class="year-title">{title}</span><span class="year-meta">{meta}</span></div>
      <div class="year-collapsible-body">{body}</div></div>"""


EXTRA_CSS = """
.table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
@media (max-width: 720px) {
  /* Tighter tables on phones so more columns fit before you have to swipe. */
  .content table.roster { font-size: 13px; }
  .content table.roster th { padding: 9px 7px; letter-spacing: .06em; font-size: 10px; }
  .content table.roster td { padding: 9px 7px; }
  .content table.roster td.num, .content table.roster th.num { white-space: nowrap; }
}
.brand-logo { width: 56px; height: 56px; border-radius: 10px; background: #fff; padding: 4px; margin-bottom: 10px; display: block; }
.oq-block { border: 1px solid #f0d78c; background: #fffaeb; border-radius: 10px; padding: 18px 22px; margin: 8px 0 28px; }
.oq-block h2 { margin: 0 0 6px; font-size: 17px; }
.oq-q { font-weight: 600; margin: 16px 0 6px; color: var(--blue-800); }
.oq-v { margin: 4px 0 4px 0; padding-left: 12px; border-left: 3px solid #f0d78c; }
.oq-src { color: var(--gray-500); font-size: 12.5px; }
.hist-year h2 { margin-top: 36px; }
.outcome-pass { color: #1c7a4a; font-weight: 600; }
.outcome-fail { color: #b42318; font-weight: 600; }
.outcome-other { color: var(--gray-600); font-weight: 600; }
.trade-card { border: 1px solid var(--gray-200); border-radius: 10px; padding: 12px 16px; margin: 0 0 10px; }
.trade-card .tmeta { font-size: 12.5px; color: var(--gray-500); margin-bottom: 6px; }
.trade-card .tside { margin: 2px 0; }
.trade-card.vetoed { opacity: 0.6; }
.tag { display: inline-block; font-size: 11px; font-weight: 600; padding: 1px 7px; border-radius: 999px; background: var(--gray-100); color: var(--gray-600); margin-left: 6px; }
.tag.keeper { background: #e6efff; color: var(--blue-800); }
.tag.vetoed { background: #fdecea; color: #b42318; }
.pos-good { color: #1c7a4a; font-weight: 600; }
.pos-bad { color: #b42318; font-weight: 600; }
.ps-wrap { max-width: 560px; }
.ps-card { border: 1px solid var(--gray-200); border-radius: 10px; padding: 12px 16px; margin: 10px 0; }
.ps-card h3 { margin: 0 0 6px; font-size: 15px; }
.ps-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }
.desk-list { list-style: none; padding: 0; margin: 0; }
.desk-list li { padding: 9px 0; border-bottom: 1px solid var(--gray-200); }
.note { color: var(--gray-600); font-size: 13px; }
table.roster td a, table.rules-table td a, .tside a { color: var(--blue-800); text-decoration: none; font-weight: 600; }
table.roster td a:hover, .tside a:hover { text-decoration: underline; }
.content .sub-line { display: block; font-size: 11.5px; color: var(--gray-500); font-weight: 400; }
.content p a, .desk-list a { color: var(--blue-600); }
"""


# ------------------------------------------------------------------ sections

def sec_home(L, generated):
    y = L.current
    wk = L.last_final_week(y)
    rows = L.season_table(y)
    games = [m for m in L.matchups if m["season"] == y]
    live_wk = max((m["week"] for m in games if m["status"] != "preevent"), default=wk)
    this_week = [m for m in games if m["week"] == live_wk]
    seen, mu = set(), []
    for m in this_week:
        k = tuple(sorted((m["team_season_id"], m["opponent_team_season_id"] or 0)))
        if k in seen:
            continue
        seen.add(k)
        a, b = L.team(m["team_season_id"]), L.team(m["opponent_team_season_id"])
        mu.append([f'{mlink(a["manager"])}<span class="sub-line">{e(a["team_name"])}</span>', f2(m["points"]),
                   f2(m["opponent_points"]), f'{mlink(b["manager"])}<span class="sub-line">{e(b["team_name"])}</span>'])
    status = "final" if all(m["status"] == "postevent" for m in this_week) else "in progress"
    st = [[str(r["rank"]), f'{mlink(r["manager"])}<span class="sub-line">{e(r["team_name"])}</span>',
           rec(r["wins"], r["losses"], r["ties"]), f1(r["points_for"]), f1(r["points_against"])] for r in rows]
    season_games = [m for m in L.final_games(y)]
    hi = max(season_games, key=lambda m: m["points"]) if season_games else None
    lo = min(season_games, key=lambda m: m["points"]) if season_games else None
    top_pw = L.c.execute("""SELECT p.player_name, s.week, s.fantasy_points, s.team_season_id FROM player_weekly_stats s
                            JOIN players p USING(player_id) WHERE s.season=? AND s.selected_position NOT IN ('BN','IR')
                            ORDER BY s.fantasy_points DESC LIMIT 1""", (y,)).fetchone()
    latest = C.SUBSTACK_POSTS[0]
    body = kpis([
        ("Season", f"{y}, week {live_wk}"),
        ("Leader", rows[0]["manager"] if rows else ""),
        ("High score", f'{f2(hi["points"])} ({L.mgr(hi["team_season_id"])}, wk {hi["week"]})' if hi else ""),
        ("Top player week", f'{top_pw["player_name"]} {f2(top_pw["fantasy_points"])}' if top_pw else ""),
    ])
    allg = [m for m in L.final_games(y)]
    lavg = sum(m["points"] for m in allg) / max(len(allg), 1)
    pf_rows = []
    for r in sorted(rows, key=lambda r: -r["points_for"]):
        g = sum(1 for m in allg if m["team_season_id"] == r["team_season_id"])
        pf_rows.append((r["manager"], r["points_for"],
                        f'<b>{e(r["manager"])}</b> ({rec(r["wins"], r["losses"], r["ties"])})<br>{f1(r["points_for"])} PF, {f1(r["points_against"])} PA'
                        + (f'<br>{r["points_for"] / g:.1f} per game' if g else "")))
    luckd = {L.mgr(t): v for (s_, t), v in L.luck().items() if s_ == y}
    body += '<div class="viz-grid2">' + V.hbars(pf_rows, "Points for", f"Through week {wk}. Hover for record and points against.", fmt="{:,.0f}", lw=64, W=460)
    body += V.diverging_bars(sorted([(m, v["w"] - v["xw"]) for m, v in luckd.items()], key=lambda r: -r[1]),
                             "Luck so far", "Actual minus all-play expected wins. More on the Luck report.") + "</div>"
    body += F.live_block(L)
    body += f"<h2>{y} standings</h2>" + table(["#", "Team", "Record", "PF", "PA"], st, cls="roster wg-standings", num=(2, 3, 4))
    body += (f'<h2>From the Commissioner</h2><p>Latest: <a href="{C.SUBSTACK}/p/{latest[0]}" target="_blank" rel="noopener">'
             f'{e(latest[1])}</a>. More on the <a href="#" data-target="desk">Commissioner\'s Desk</a>.</p>')
    if lo:
        body += f'<p class="note">Low score so far: {f2(lo["points"])} ({e(L.mgr(lo["team_season_id"]))}, week {lo["week"]}).</p>'
    body += f'<p class="footnote">Data: Yahoo Fantasy, through {e(generated)}. Fantasy data provided by Yahoo Fantasy.</p>'
    return section("summary", LEAGUE, f"12-team keeper league since 2006 &middot; {y} season", body,
                   eyebrow="League home", hidden=False)


def sec_about(L):
    body = f"""
    <div class="rules-grid">
      <section class="rule-block"><h2 class="rule-h2">What this is</h2>
        <p>The league's record book and reference shelf, rebuilt from Yahoo's data for every season since 2012
        and refreshed as games finish. It turns the analysis Mike has done by hand for years (luck, records,
        keeper streaks, playoff history) into pages that keep themselves current.</p></section>
      <section class="rule-block"><h2 class="rule-h2">What's in it</h2>
        <p><strong>Commentary &amp; League Info</strong>: Mike's writeups, the rules, and how they got that way.<br>
        <strong>Standings &amp; Records</strong>: this season, all time, champions, the record book, playoffs.<br>
        <strong>Manager Resources</strong>: luck, over and under achievers, positional strength, player search.<br>
        <strong>Draft &amp; Keepers</strong> and <strong>Transactions</strong>: every draft, keeper, trade and FAAB bid on Yahoo.<br>
        <strong>Teams</strong>: one page per manager.</p></section>
      <section class="rule-block"><h2 class="rule-h2">Known gaps</h2>
        <p>Yahoo's history starts in 2010, and 2010 and 2011 are not loaded yet; 2006 to 2011 champions and records
        will come from Mike's records. Off-season trades and future picks that were never entered in Yahoo do not
        appear yet. Season player points count only the weeks a player was on a roster in this league.</p></section>
    </div>"""
    return section("about", "About this site", "How it works, what's covered, what isn't yet.", body)


def sec_desk():
    items = "".join(f'<li><a href="{C.SUBSTACK}/p/{s}" target="_blank" rel="noopener">{e(t)}</a></li>'
                    for s, t in C.SUBSTACK_POSTS)
    body = (f'<p>Mike writes the <a href="{C.SUBSTACK}" target="_blank" rel="noopener">We Graduated Report</a> '
            f'on Substack: previews, reviews, awards and summit results. Every post since 2023:</p>'
            f'<ul class="desk-list">{items}</ul>'
            '<p class="note">Earlier writeups (2012 to 2022) are in Mike\'s archive and will be added over time.</p>')
    return section("desk", "Commissioner's Desk", "The We Graduated Report, by Mike.", body)


def sec_rules():
    oq = '<div class="oq-block"><h2>Open questions for the league</h2>' \
         '<p class="note">These rules are written down more than one way. Every version is listed with its source. ' \
         'They are for the league to settle; none is marked as correct here.</p>'
    for q, versions in C.OPEN_QUESTIONS:
        oq += f'<div class="oq-q">{e(q)}</div>'
        for label, text, src in versions:
            oq += f'<div class="oq-v"><strong>{e(label)}:</strong> {e(text)} <span class="oq-src">Source: {e(src)}</span></div>'
    oq += "</div>"
    blocks = ""
    for head, parts in C.RULES:
        inner = ""
        for p in parts:
            if isinstance(p, tuple) and p[0] == "table":
                _, hd, rows = p
                inner += table(hd, [[e(c) for c in r] for r in rows], cls="rules-table")
            else:
                inner += f"<p>{e(p)}</p>"
        blocks += f'<section class="rule-block"><h2 class="rule-h2">{e(head)}</h2>{inner}</section>'
    return section("league-rules", "League rules", "Current rules, with the open questions up top.",
                   oq + f'<div class="rules-grid">{blocks}</div>')


def outcome_cls(o):
    lo = o.lower()
    if lo.startswith(("passed", "in effect", "adopted")):
        return "outcome-pass"
    if lo.startswith(("failed", "voted down", "not adopted")):
        return "outcome-fail"
    return "outcome-other"


def sec_rules_history():
    yrs = [h for h in C.HISTORY if any(not o.lower().startswith("pending") for _, o in h[2])]
    yrs = sorted(yrs, key=lambda h: h[0])
    cnt = lambda h, c: sum(1 for _, o in h[2] if outcome_cls(o) == c and not o.lower().startswith("pending"))
    body = V.stacked_vbars([str(h[0]) for h in yrs], [("Passed / adopted", V.ACCENT, [cnt(h, "outcome-pass") for h in yrs]),
                                                       ("Failed / voted down", V.NEG, [cnt(h, "outcome-fail") for h in yrs]),
                                                       ("Tabled, split or other", V.MUTED, [cnt(h, "outcome-other") for h in yrs])],
                           "Summit outcomes by year", "Every logged proposal and topic, from Mike's league doc and Substack.", height=220)
    for year, title, items in C.HISTORY:
        rows = [[e(i), f'<span class="{outcome_cls(o)}">{e(o)}</span>'] for i, o in items]
        body += f'<div class="hist-year"><h2>{year}: {e(title)}</h2>' + table(["Topic", "Outcome"], rows, cls="rules-table") + "</div>"
    srows = [[str(y), e(loc), e(h), f"{n} of 12"] for y, loc, h, n in C.SUMMITS]
    body += "<h2>Summits</h2>" + table(["Year", "Where", "Hosts", "Attendance"], srows, cls="rules-table")
    body += '<p class="note">From Mike\'s league doc and Substack. Vote counts shown where they were recorded.</p>'
    return section("rules-history", "Rules history", "What the league changed, when, and what it turned down.", body)


def sec_standings(L):
    y = L.current
    body = ""
    weeks = sorted({m["week"] for m in L.matchups if m["season"] == y and m["status"] != "preevent"})
    for wk in reversed(weeks):
        seen, rows = set(), []
        for m in [m for m in L.matchups if m["season"] == y and m["week"] == wk]:
            k = tuple(sorted((m["team_season_id"], m["opponent_team_season_id"] or 0)))
            if k in seen:
                continue
            seen.add(k)
            a, b = m["team_season_id"], m["opponent_team_season_id"]
            win = "" if m["is_winner"] is None else (L.mgr(a) if m["is_winner"] else L.mgr(b))
            rows.append([mlink(L.mgr(a)), f2(m["points"]), f2(m["opponent_points"]), mlink(L.mgr(b)), e(win)])
        final = all(m["status"] == "postevent" for m in L.matchups if m["season"] == y and m["week"] == wk)
        body += collapsible(f"Week {wk}", "final" if final else "in progress",
                            table(["Team", "Pts", "Pts", "Opponent", "Winner"], rows, num=(1, 2)), open_=wk == weeks[-1])
    cols = []
    for wk in weeks:
        g = [m for m in L.final_games(y) if m["week"] == wk]
        if g:
            cols.append((f"Wk {wk}", [(L.mgr(m["team_season_id"]), m["points"],
                         f'<b>{e(L.mgr(m["team_season_id"]))}</b>, week {wk}<br>{f2(m["points"])} vs {e(L.mgr(m["opponent_team_season_id"]))} {f2(m["opponent_points"])}'
                         f'<br>{"Won" if m["is_winner"] else "Lost"}') for m in g]))
    lead = L.season_table(y)[0]["manager"] if L.season_table(y) else None
    chart = V.strip(cols, f"{y}: every score, every week", "Each dot is a team's score; the black tick is the weekly median. Pick a manager to follow.", default=lead) if cols else ""
    return section("standings", f"{y} scores", "Every matchup this season, newest first.", chart + body)


def sec_alltime(L):
    at = L.alltime()
    pr = L.playoff_records()
    rows = []
    for m, a in sorted(at.items(), key=lambda kv: -((kv[1]["w"] + 0.5 * kv[1]["t"]) / max(kv[1]["g"], 1))):
        p = pr.get(m, {"w": 0, "l": 0})
        rows.append([mlink(m), str(a["seasons"]), rec(a["w"], a["l"], a["t"]), pct(a["w"], a["l"], a["t"]),
                     f1(a["pf"] / a["g"]) if a["g"] else "", str(a["playoffs"]), rec(p["w"], p["l"]),
                     str(a["finals"]), str(a["titles"])])
    recs = L.regular_season_records()
    series = {}
    for m in at:
        run, ys = 0, []
        for y in L.years:
            t = next((t for t in L.teams_in(y) if t["manager"] == m), None)
            r = recs.get((y, t["team_season_id"])) if t else None
            if r:
                run += r["w"] + 0.5 * r["t"]
                ys.append(run)
            else:
                ys.append(None if run == 0 or y > max(yy for yy in L.years if any(tt["manager"] == m for tt in L.teams_in(yy))) else None)
        series[m] = ys
    leader = max(series, key=lambda m: max(v for v in series[m] if v is not None))
    body = V.multi_line(series, L.years, "Cumulative regular-season wins",
                        "Click a name or hover a line to follow a manager. Yahoo history starts in 2012; Brad left after 2018 and John took over his team in 2019.",
                        default=leader)
    body += table(["Manager", "Seasons", "Reg. season", "Win %", "PPG", "Playoff yrs", "Playoff W-L", "Finals", "Titles"],
                 rows, num=(1, 2, 3, 4, 5, 6, 7, 8))
    # wins by season grid
    grid = []
    for m in sorted(at):
        cells = [mlink(m)]
        for y in L.years:
            t = next((t for t in L.teams_in(y) if t["manager"] == m), None)
            r = recs.get((y, t["team_season_id"])) if t else None
            cells.append(str(r["w"]) if r else "")
        grid.append(cells)
    body += "<h2>Regular-season wins by year</h2>" + table(["Manager"] + [str(y)[2:] for y in L.years], grid,
                                                           num=tuple(range(1, len(L.years) + 1)))
    body += f'<p class="note">Regular season only, {L.years[0]} on. {L.current} is in progress.</p>'
    return section("alltime", "All-time standings", f"Every manager, {L.years[0]} to today.", body)


def sec_champions(L):
    rows = []
    for y in reversed(L.finished):
        a = L.season_awards(y)
        rows.append([str(y), mlink(a["champion"]["manager"]), mlink(a["runner_up"]["manager"]),
                     mlink(a["reg_champ"]["manager"]),
                     f'{mlink(a["most_points"]["manager"])} <span class="note">{f1(a["most_points"]["points_for"])}</span>'])
    at = L.alltime()
    crow = sorted(at.items(), key=lambda kv: (-kv[1]["titles"], -kv[1]["finals"], -kv[1]["playoffs"], kv[0]))
    chart = V.stacked_hbars(
        [(m, [a["titles"], a["finals"] - a["titles"], a["playoffs"] - a["finals"]],
          f'<b>{e(m)}</b><br>{a["titles"]} titles<br>{a["finals"]} finals<br>{a["playoffs"]} playoff seasons of {a["seasons"]}')
         for m, a in crow],
        [("Titles", V.BLUES[0]), ("Lost in final", V.BLUES[2]), ("Other playoff seasons", V.BLUES[3])],
        "Titles, finals and playoff seasons", f"Each bar is a manager's playoff seasons since {L.years[0]}; the darkest part is titles.")
    body = chart + table(["Season", "Champion", "Runner-up", "Regular-season #1", "Most points"], rows)
    body += "<h2>Championship rosters</h2>"
    for i, y in enumerate(reversed(L.finished)):
        ch = L.season_awards(y)["champion"]
        r = [[e(p["player_name"]), e(p["position"]), f1(p["pts"])] for p in L.champion_roster(y)]
        body += collapsible(f'{y}: {e(ch["manager"])}', e(ch["team_name"]),
                            table(["Player", "Pos", "Starting pts"], r, num=(2,)), open_=i == 0)
    body += '<p class="note">2006 to 2011 champions will be added from Mike\'s records.</p>'
    return section("champions", "Champions & awards", "Who won what, every season on Yahoo.", body)


def game_row(L, m, show_opp=True):
    return [str(m["season"]), str(m["week"]), mlink(L.mgr(m["team_season_id"])), f2(m["points"]),
            mlink(L.mgr(m["opponent_team_season_id"])), f2(m["opponent_points"])]


def sec_records(L):
    hi, lo, blow, close = L.high_low(10)
    hd = ["Year", "Wk", "Team", "Pts", "Opponent", "Opp pts"]
    ys, mid, lo_, hi_, lt, ht = [], [], [], [], [], []
    for y in L.years:
        g = [m for m in L.final_games(y, regular=True)]
        if not g:
            continue
        a, b = min(g, key=lambda m: m["points"]), max(g, key=lambda m: m["points"])
        ys.append(y); mid.append(sum(m["points"] for m in g) / len(g)); lo_.append(a["points"]); hi_.append(b["points"])
        lt.append(f'<b>{y} low</b><br>{f2(a["points"])}, {e(L.mgr(a["team_season_id"]))} (wk {a["week"]})')
        ht.append(f'<b>{y} high</b><br>{f2(b["points"])}, {e(L.mgr(b["team_season_id"]))} (wk {b["week"]})')
    body = V.band_line(ys, mid, lo_, hi_, "Scoring by season", "Average weekly score with the season's single highest and lowest. Regular season.",
                       fmt="{:.1f}", lo_tip=lt, hi_tip=ht, mid_name="Average score")
    body += "<h2>Highest scores</h2>" + table(hd, [game_row(L, m) for m in hi], num=(3, 5))
    body += "<h2>Lowest scores</h2>" + table(hd, [game_row(L, m) for m in lo], num=(3, 5))
    body += "<h2>Biggest blowouts</h2>" + table(hd + ["Margin"], [game_row(L, m) + [f2(abs(m["points"] - m["opponent_points"]))]
                                                                 for m in blow], num=(3, 5, 6))
    body += "<h2>Closest games</h2>" + table(hd + ["Margin"], [game_row(L, m) + [f2(abs(m["points"] - m["opponent_points"]))]
                                                              for m in close], num=(3, 5, 6))
    # player single weeks
    pw = L.c.execute("""SELECT s.season, s.week, p.player_name, p.position, s.fantasy_points, s.team_season_id
                        FROM player_weekly_stats s JOIN players p USING(player_id)
                        WHERE s.selected_position NOT IN ('BN','IR') ORDER BY s.fantasy_points DESC LIMIT 10""").fetchall()
    body += "<h2>Best player weeks (started)</h2>" + table(["Year", "Wk", "Player", "Pos", "Pts", "Manager"],
        [[str(r["season"]), str(r["week"]), e(r["player_name"]), e(r["position"]), f2(r["fantasy_points"]),
          mlink(L.mgr(r["team_season_id"]))] for r in pw], num=(4,))
    body += '<p class="note">Regular-season games, 2012 on.</p>'
    return section("records", "Record book", "Highs, lows, blowouts and nail-biters.", body)


def sec_playoffs(L):
    pr = L.playoff_records()
    at = L.alltime()
    rows = [[mlink(m), str(at[m]["playoffs"]), str(at[m]["byes"]), rec(p["w"], p["l"]), str(at[m]["finals"]), str(at[m]["titles"])]
            for m, p in sorted(pr.items(), key=lambda kv: (-kv[1]["w"], kv[1]["l"]))]
    games = L.bracket_games()
    exit_ = {}
    for g in games:
        exit_[(g["season"], g["loser"])] = g["round_name"]
    seed_out = {}
    for y in L.finished:
        for t in L.season_table(y):
            sd = t["playoff_seed"]
            if not sd or sd > L.seasons[y]["num_playoff_teams"]:
                continue
            res = "Champion" if t["rank"] == 1 else {"Final": "Lost final", "Semifinal": "Lost semifinal"}.get(exit_.get((y, t["team_season_id"])), "Lost round 1")
            seed_out.setdefault(sd, {}).setdefault(res, []).append(f'{y} {t["manager"]}')
    order = ["Champion", "Lost final", "Lost semifinal", "Lost round 1"]
    seed_chart = V.stacked_hbars(
        [(f"Seed {sd}", [len(seed_out[sd].get(k, [])) for k in order],
          f"<b>Seed {sd}</b><br>" + "<br>".join(f'{k}: {len(seed_out[sd].get(k, []))}' for k in order)
          + (f'<br>Champions: {e(", ".join(seed_out[sd].get("Champion", [])))}' if seed_out[sd].get("Champion") else ""))
         for sd in sorted(seed_out)],
        list(zip(order, V.BLUES)), "How each seed has fared", f"Every bracket since {L.finished[0]}. Seeds 1 and 2 get byes.", lw=64, W=460)
    wl = sorted(pr.items(), key=lambda kv: (-kv[1]["w"], kv[1]["l"]))
    wl_chart = V.stacked_hbars([(m, [p["w"], p["l"]], f'<b>{e(m)}</b><br>{p["w"]}-{p["l"]} in bracket games') for m, p in wl],
                               [("Wins", V.ACCENT), ("Losses", "#f2a3a3")], "Playoff wins and losses", "Championship bracket only.", lw=64, W=460)
    body = '<div class="viz-grid2">' + seed_chart + wl_chart + "</div>"
    body += table(["Manager", "Appearances", "Byes", "W-L", "Finals", "Titles"], rows, num=(1, 2, 3, 4, 5))
    bye = L.bye_outcomes()
    tally = {}
    for _, seed, _, res in bye:
        tally.setdefault(res, 0)
        tally[res] += 1
    body += "<h2>How the top two seeds fared</h2>"
    body += f'<p>{len(bye)} bye teams since {L.finished[0]}: ' + ", ".join(f"{v} {k.lower()}" for k, v in tally.items()) + ".</p>"
    body += table(["Season", "Seed", "Manager", "Result"], [[str(y), str(s), mlink(m), e(r)] for y, s, m, r in reversed(bye)])
    body += "<h2>Every playoff game</h2>"
    for i, y in enumerate(reversed(L.finished)):
        g = [x for x in games if x["season"] == y]
        r = [[e(x["round_name"]), mlink(L.mgr(x["winner"])), f2(x["wpts"]), mlink(L.mgr(x["loser"])), f2(x["lpts"])] for x in g]
        body += collapsible(str(y), f"{len(g)} games", table(["Round", "Winner", "Pts", "Loser", "Pts"], r, num=(2, 4)), open_=i == 0)
    body += '<p class="note">Championship bracket only. Consolation and placement games are not counted.</p>'
    return section("playoffs", "Playoff history", "Records, byes and every bracket game.", body)


def sec_luck(L):
    lk = L.luck()
    y = L.current
    cur = sorted([(L.mgr(t), v) for (s, t), v in lk.items() if s == y], key=lambda kv: -(kv[1]["w"] - kv[1]["xw"]))
    rows = [[mlink(m), f'{v["w"]:g}', f1(v["xw"]), luck_cell(v["w"] - v["xw"])] for m, v in cur]
    body = f"<h2>{y} so far</h2>" + V.scatter_luck([(m, v["xw"], v["w"]) for m, v in cur], f"{y}: actual vs expected wins",
        "On the line = record matches scoring. Above the line = lucky. Below = unlucky.")
    body += table(["Manager", "Wins", "Expected wins", "Luck"], rows, num=(1, 2, 3))
    career = {}
    for (s, t), v in lk.items():
        c = career.setdefault(L.mgr(t), {"w": 0, "xw": 0, "g": 0, "best": None, "worst": None})
        d = v["w"] - v["xw"]
        c["w"] += v["w"]; c["xw"] += v["xw"]; c["g"] += v["g"]
        if s in L.finished:
            if c["best"] is None or d > c["best"][1]:
                c["best"] = (s, d)
            if c["worst"] is None or d < c["worst"][1]:
                c["worst"] = (s, d)
    rows = [[mlink(m), f'{c["w"]:g}', f1(c["xw"]), luck_cell(c["w"] - c["xw"]),
             f'{c["best"][0]} ({c["best"][1]:+.1f})' if c["best"] else "", f'{c["worst"][0]} ({c["worst"][1]:+.1f})' if c["worst"] else ""]
            for m, c in sorted(career.items(), key=lambda kv: -(kv[1]["w"] - kv[1]["xw"]))]
    body += "<h2>Career</h2>" + V.diverging_bars(
        [(m, c["w"] - c["xw"]) for m, c in sorted(career.items(), key=lambda kv: -(kv[1]["w"] - kv[1]["xw"]))],
        "Career luck, in wins", f"Actual minus expected wins, {L.years[0]} to today") + table(["Manager", "Wins", "Expected", "Luck", "Luckiest year", "Unluckiest year"], rows, num=(1, 2, 3))
    allyears = sorted(((s, L.mgr(t), v["w"] - v["xw"]) for (s, t), v in lk.items() if s in L.finished), key=lambda r: -r[2])
    body += "<h2>Luckiest and unluckiest seasons</h2>" + table(["Season", "Manager", "Luck"],
        [[str(s), mlink(m), luck_cell(d)] for s, m, d in allyears[:5] + allyears[-5:]], num=(2,))
    body += ('<p class="note">Expected wins: each week, your score is compared with all 11 other teams. Beat 8 of 11 '
             'and you earn 0.73 expected wins. Luck = actual wins minus expected wins. Regular season only.</p>')
    return section("luck", "Luck report", "Actual wins against the wins your scores deserved.", body)


def luck_cell(d):
    cls = "pos-good" if d >= 1 else "pos-bad" if d <= -1 else ""
    return f'<span class="{cls}">{d:+.1f}</span>'


def sec_overunder(L):
    ou = L.over_under()
    y = L.current
    rows = sorted([(L.mgr(t), v) for (s, t), v in ou.items() if s == y and v["g"]], key=lambda kv: -(kv[1]["pts"] - kv[1]["proj"]))
    body = f"<h2>{y} so far</h2>" + V.diverging_bars([(m, (v["pts"] - v["proj"]) / v["g"]) for m, v in rows],
        f"{y}: points vs. Yahoo projection, per game", "Positive = the lineup you started beat its projection.")
    car = {}
    for (s_, t), v in ou.items():
        if v["g"]:
            c = car.setdefault(L.mgr(t), [0, 0, 0]); c[0] += v["pts"]; c[1] += v["proj"]; c[2] += v["g"]
    body += table(["Manager", "Points", "Projected", "Difference", "Per game"],
        [[mlink(m), f1(v["pts"]), f1(v["proj"]), luck_cell_pts(v["pts"] - v["proj"]), f"{(v['pts'] - v['proj']) / v['g']:+.1f}"]
         for m, v in rows], num=(1, 2, 3, 4))
    hist = sorted([(s, L.mgr(t), v) for (s, t), v in ou.items() if s in L.finished and v["g"]],
                  key=lambda r: -(r[2]["pts"] - r[2]["proj"]) / r[2]["g"])
    fmt = lambda r: [str(r[0]), mlink(r[1]), f1(r[2]["pts"]), f1(r[2]["proj"]), f"{(r[2]['pts'] - r[2]['proj']) / r[2]['g']:+.1f}"]
    body += "<h2>Career</h2>" + V.diverging_bars(sorted([(m, (c[0] - c[1]) / c[2]) for m, c in car.items()], key=lambda r: -r[1]),
        "Career: points vs. projection, per game", f"Regular season, {min(s_ for s_, _ in ou)} on (seasons where Yahoo kept projections).")
    body += "<h2>Biggest overachievers</h2>" + table(["Season", "Manager", "Points", "Projected", "Per game"], [fmt(r) for r in hist[:8]], num=(2, 3, 4))
    body += "<h2>Biggest underachievers</h2>" + table(["Season", "Manager", "Points", "Projected", "Per game"], [fmt(r) for r in hist[-8:][::-1]], num=(2, 3, 4))
    body += '<p class="note">Projected = Yahoo\'s weekly projection for the lineup you started. Regular season only.</p>'
    return section("overunder", "Over & under achievers", "Points scored against what Yahoo projected.", body)


def luck_cell_pts(d):
    cls = "pos-good" if d >= 25 else "pos-bad" if d <= -25 else ""
    return f'<span class="{cls}">{d:+.1f}</span>'


def sec_positional(L):
    y = L.current
    pos = ["QB", "RB", "WR", "TE", "K", "DEF"]
    body = ""
    for i, season in enumerate([y] + list(reversed(L.finished))):
        data = L.positional(season)
        if not data:
            continue
        avg = {p: sum(d.get(p, 0) for d in data.values()) / len(data) for p in pos}
        tot_avg = sum(avg.values())
        hm = []
        for tsid, d in sorted(data.items(), key=lambda kv: -sum(kv[1].values())):
            vals = {p: (d.get(p, 0), (d.get(p, 0) - avg[p]) / avg[p] if avg[p] else 0) for p in pos}
            tot = sum(d.values())
            vals["Total"] = (tot, (tot - tot_avg) / tot_avg if tot_avg else 0)
            hm.append((L.mgr(tsid), vals))
        hm.append(("League avg", {**{p: (avg[p], 0) for p in pos}, "Total": (tot_avg, 0)}))
        chart = V.heatmap(hm, pos + ["Total"], f"{season} starting points by slot",
                          "Shaded against the league average for that slot. Hover a cell for the gap.")
        body += collapsible(str(season), "in progress" if season == y else "", chart, open_=i == 0)
    body += '<p class="note">Points from players in each starting slot, regular season. Full color = 35% or more above (blue) or below (red) the league average.</p>'
    return section("positional", "Positional strength", "Where each team's starting points come from.", body)


def sec_search(L, C):
    return section("player-search", "Player search",
                   "Every player who has been on a We Graduated roster: the all-time leaders, how each one scored, who had him, and how he got there.",
                   F.search_body(L, C, ""))


def sec_h2h(L, games):
    return section("h2h", "Head-to-head", "Every manager's record against every other manager.", F.h2h_body(L, games))


def sec_compare(L):
    return section("player-compare", "Player comparison",
                   "Pin up to three players side by side: season points, this year week by week, and who has had them.",
                   F.compare_body())


SEARCH_JS = r"""
(function(){
  const box = document.getElementById('wg-ps'), out = document.getElementById('wg-ps-out');
  if (!box || !window.WG_PLAYERS) return;
  const esc = s => String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
  function spark(ss){
    const by = {}; ss.forEach(s => by[s.y] = (by[s.y] || 0) + s.pts);
    const ys = Object.keys(by).map(Number).sort((a, b) => a - b);
    if (ys.length < 2) return '';
    const y0 = ys[0], y1 = ys[ys.length - 1], hi = Math.max(...ys.map(y => by[y])) || 1, W = 220, H = 46;
    const px = y => 6 + (W - 12) * (y - y0) / Math.max(y1 - y0, 1), py = v => H - 14 - (H - 22) * v / hi;
    const pts = ys.map(y => px(y).toFixed(1) + ',' + py(by[y]).toFixed(1));
    return '<svg class="ps-spark" width="' + W + '" height="' + H + '" viewBox="0 0 ' + W + ' ' + H + '"><path d="M' + pts.join(' L') +
      '" fill="none" stroke="#1761A0" stroke-width="1.8"/>' + ys.map(y => '<circle cx="' + px(y).toFixed(1) + '" cy="' + py(by[y]).toFixed(1) +
      '" r="3" fill="#1761A0" data-tip="<b>' + y + '</b>: ' + by[y].toFixed(1) + ' pts"/>').join('') +
      '<text x="6" y="' + (H - 2) + '" font-size="10" fill="#8e8e93">' + y0 + '</text><text x="' + (W - 6) + '" y="' + (H - 2) +
      '" font-size="10" fill="#8e8e93" text-anchor="end">' + y1 + '</text></svg>';
  }
  function render(q){
    q = q.trim().toLowerCase();
    if (q.length < 2) { out.innerHTML = ''; return; }
    const hits = window.WG_PLAYERS.filter(p => p.n.toLowerCase().includes(q)).slice(0, 15);
    out.innerHTML = hits.map(p => '<div class="ps-card"><div class="ps-head"><h3>' + esc(p.n) + ' <span class="tag">' + esc(p.p) + '</span>' +
      ' <span class="note">' + p.t.toFixed(1) + ' pts in this league</span></h3>' + spark(p.s) + '</div><table class="roster"><thead><tr><th>Season</th><th>Manager</th><th>How</th><th class="num">Pts</th></tr></thead><tbody>' +
      p.s.map(s => '<tr><td>' + s.y + '</td><td>' + esc(s.m) + '</td><td>' + (s.how === 'Kept' ? '<span class="tag keeper">Kept</span>' : esc(s.how || 'Waivers / trade')) +
        '</td><td class="num">' + s.pts.toFixed(1) + '</td></tr>').join('') + '</tbody></table></div>').join('') ||
      '<p class="note">No player found.</p>';
  }
  box.addEventListener('input', () => render(box.value));
})();
"""


def sec_drafts(L):
    board = F.draft_board_body(L)
    pts = L.season_player_points()
    byr = {}
    for y in L.finished:
        for p in L.draft(y):
            byr.setdefault(p["draft_round"], []).append(pts.get((y, p["player_id"]), 0))
    rds = sorted(r for r in byr if r <= 15)
    avg = [sum(byr[r]) / len(byr[r]) for r in rds]
    body = V.vbars([str(r) for r in rds], avg, "Average season points by draft round",
                   f"Finished seasons {L.finished[0]} to {L.finished[-1]}. Rounds 10 to 15 (light) are keepers, which is why the back of the draft out-scores the front.",
                   fmt="{:,.0f}", colors=[V.ACCENT if r < 10 else "#86b6ef" for r in rds],
                   tips=[f"<b>Round {r}</b><br>{a:.1f} pts on average<br>{len(byr[r])} picks" for r, a in zip(rds, avg)])
    for i, y in enumerate(reversed(L.years)):
        picks = L.draft(y)
        rows = []
        for p in picks:
            tag = '<span class="tag keeper">Keeper</span>' if p["is_keeper"] else ""
            rows.append([str(p["draft_round"]), str(p["overall_pick"]), mlink(L.mgr(p["team_season_id"])),
                         e(p["player_name"]) + tag, e(p["position"]), f1(pts.get((y, p["player_id"]), 0))])
        nk = sum(1 for p in picks if p["is_keeper"])
        body += collapsible(str(y), f"{len(picks)} picks, {nk} keepers",
                            table(["Rd", "Pick", "Manager", "Player", "Pos", "Season pts"], rows, num=(0, 1, 5)), open_=i == 0)
    body += '<p class="note">Keepers fill each team\'s last six slots (Rounds 10 to 15; Rounds 11 to 16 in 2020). Season points count weeks on any roster in this league.</p>'
    body = ('<h2 style="margin-top:6px">Draft board</h2><p class="note">Every pick laid out like the draft room: one column per draft slot, one row per round, with the manager who made each pick (traded picks show up under the slot they came from). '
            'Each square shows the player\'s FPOR (points over a replacement-level player). Shade by value vs. what that slot usually returns, by raw FPOR, or by position. Hover or tap a square for details.</p>'
            + board + "<h2>Season by season</h2>" + body)
    return section("drafts", "Draft results", "Every pick since 2012, keepers marked.", body)


def sec_firstround(L):
    pts = L.season_player_points()
    slot, mix = {}, {}
    for y in L.years:
        for p in L.draft(y):
            if p["draft_round"] != 1:
                continue
            if y in L.finished:
                slot.setdefault(p["pick_in_round"], []).append((pts.get((y, p["player_id"]), 0), y, p["player_name"]))
            pos = (p["position"] or "").split(",")[0]
            mix.setdefault(y, {}).setdefault(pos, 0)
            mix[y][pos] += 1
    sl = sorted(slot)
    av = [sum(v[0] for v in slot[k]) / len(slot[k]) for k in sl]
    tips = []
    for k, a in zip(sl, av):
        b = max(slot[k]); w = min(slot[k])
        tips.append(f"<b>Pick {k}</b><br>{a:.1f} pts on average<br>Best: {e(b[2])} {b[1]} ({b[0]:.0f})<br>Worst: {e(w[2])} {w[1]} ({w[0]:.0f})")
    lavg = sum(v[0] for k in sl for v in slot[k]) / max(sum(len(slot[k]) for k in sl), 1)
    body = '<div class="viz-grid2">' + V.vbars([str(k) for k in sl], av, "Average season points by first-round slot",
                                               "Finished seasons. The dashed line is the first-round average.", fmt="{:,.0f}", tips=tips,
                                               ref=("Rd 1 avg", lavg), height=260, W=460)
    yrs = sorted(mix)
    pc = [("RB", V.ACCENT), ("WR", "#86b6ef"), ("QB", "#e1b523"), ("TE", "#606C71")]
    body += V.stacked_vbars([str(y)[2:] for y in yrs], [(n, c, [mix[y].get(n, 0) for y in yrs]) for n, c in pc],
                            "First-round picks by position", "Twelve picks a year.", height=260, W=460) + "</div>"
    for i, y in enumerate(reversed(L.years)):
        r1 = [p for p in L.draft(y) if p["draft_round"] == 1]
        ranked = sorted(r1, key=lambda p: -pts.get((y, p["player_id"]), 0))
        best = {p["overall_pick"]: n + 1 for n, p in enumerate(ranked)}
        rows = [[str(p["overall_pick"]), mlink(L.mgr(p["team_season_id"])), e(p["player_name"]), e(p["position"]),
                 f1(pts.get((y, p["player_id"]), 0)), str(best[p["overall_pick"]])] for p in r1]
        body += collapsible(str(y), "in progress" if y == L.current else "",
                            table(["Pick", "Manager", "Player", "Pos", "Season pts", "Rank in Rd 1"], rows, num=(0, 4, 5)), open_=i == 0)
    return section("firstround", "First-round history", "Every first-round pick and how it turned out.", body)


def sec_keepers(L):
    streaks = L.keeper_streaks()
    active = [s for s in streaks if s["active"]][:15]
    top = streaks[:18]
    body = V.timeline([(f'{s["player"]} ({s["manager"]})', s["start"], s["end"], s["active"],
                        f'<b>{e(s["player"])}</b><br>Kept by {e(s["manager"])} {s["start"]} to {s["end"]} ({s["years"]} yrs)')
                       for s in top], L.years, "The longest keeper streaks",
                      "Consecutive seasons the same manager kept the player, 2012 on.")
    body += f"<h2>Longest active streaks ({L.current})</h2>" + table(["Player", "Pos", "Manager", "Kept since", "Years"],
        [[e(s["player"]), e(s["pos"]), mlink(s["manager"]), str(s["start"]), str(s["years"])] for s in active], num=(3, 4))
    body += "<h2>Longest streaks ever</h2>" + table(["Player", "Pos", "Manager", "Years kept", "Streak"],
        [[e(s["player"]), e(s["pos"]), mlink(s["manager"]), f'{s["start"]} to {s["end"]}' + (" (active)" if s["active"] else ""),
          str(s["years"])] for s in streaks[:20]], num=(4,))
    rr = L.repeat_keeper_rate()
    avg_rr = sum(a for _, a, b in rr) / max(sum(b for _, a, b in rr), 1) * 100
    body += "<h2>Repeat keepers</h2>" + V.vbars([str(y)[2:] for y, a, b in rr], [a / b * 100 for y, a, b in rr],
        "Share of keepers kept again by the same manager", "Of each season's keepers, how many the same manager kept the year before.",
        fmt="{:.0f}%", ref=("average", avg_rr), tips=[f"<b>{y}</b><br>{a} of {b} ({a / b:.1%})" for y, a, b in rr]) + table(["Season", "Kept again by same manager", "Of", "Rate"],
        [[str(y), str(a), str(b), f"{a / b:.1%}"] for y, a, b in reversed(rr)], num=(1, 2, 3))
    body += '<p class="note">A streak is consecutive seasons the same manager kept the player. Keepers before 2012 will be added from Mike\'s records, which will lengthen some streaks.</p>'
    return section("keepers", "Keeper history", "Who holds on, and for how long.", body)


def sec_trades(L):
    trades = L.trades()
    ok = [t for t in trades if t["status"] == "successful"]
    per = [sum(1 for t in ok if t["season"] == y) for y in L.years]
    cnt = {}
    for t in ok:
        for m in t["sides"]:
            cnt[m] = cnt.get(m, 0) + 1
    pairs = {}
    for t in ok:
        ms = sorted(t["sides"])
        if len(ms) == 2:
            pairs[tuple(ms)] = pairs.get(tuple(ms), 0) + 1
    top = sorted(pairs.items(), key=lambda kv: -kv[1])[:3]
    body = '<div class="viz-grid2">' + V.vbars([str(y)[2:] for y in L.years], per, "Trades per season", f"{L.current} is in progress.",
                                               tips=[f"<b>{y}</b><br>{n} trades" for y, n in zip(L.years, per)], W=460, height=280)
    body += V.hbars([(m, n, f"<b>{e(m)}</b><br>{n} trades since {L.years[0]}") for m, n in sorted(cnt.items(), key=lambda kv: -kv[1])],
                    "Trades by manager", "Every completed trade since " + str(L.years[0]) + ".", lw=60, W=480) + "</div>"
    if top:
        body += '<p class="note">Most frequent trade partners: ' + "; ".join(f"{e(a)} and {e(b)} ({n})" for (a, b), n in top) + ".</p>"
    years = sorted({t["season"] for t in trades}, reverse=True)
    for i, y in enumerate(years):
        cards = ""
        ty = [t for t in trades if t["season"] == y]
        for t in ty:
            sides = "".join(
                f'<div class="tside"><strong>{mlink(m)}</strong> gets: {e(", ".join(v["players"] + v["picks"]) or "nothing listed")}</div>'
                for m, v in t["sides"].items())
            vet = t["status"] != "successful"
            vtag = '<span class="tag vetoed">' + e(t["status"]) + "</span>" if vet else ""
            vcls = " vetoed" if vet else ""
            cards += f'<div class="trade-card{vcls}"><div class="tmeta">{e(t["date"])}{vtag}</div>{sides}</div>'
        body += collapsible(str(y), f"{len(ty)} trades", cards, open_=i == 0)
    body += '<p class="note">Trades as recorded on Yahoo. Off-season and future-pick trades that were never entered in Yahoo are not shown yet.</p>'
    return section("trades", "Trades", f"Every trade on Yahoo since {L.years[0]}.", body)


def sec_value(L):
    return section("value-board", "FPOR value board",
                   "Fantasy points over replacement for every pick, keeper and pickup, against what the draft slot usually returns.",
                   DY.value_board(L, mlink))


def sec_faab(L):
    offers = json.loads(OFFERS.read_text()) if OFFERS.exists() else {}
    return section("faab", "FAAB ledger", "Every waiver claim: who won, who was outbid, and what each dollar bought.",
                   DY.faab_ledger(L, mlink, offers))


def sec_txlog(L):
    return section("txlog", "Transaction log", "Every add, drop and trade on Yahoo, any season.", DY.transaction_log(L, mlink))


def sec_team(L, manager, generated, wk_by_pid, h2h):
    cur = next((t for t in L.teams_in(L.current) if t["manager"] == manager), None)
    at = L.alltime()[manager]
    pr = L.playoff_records().get(manager, {"w": 0, "l": 0})
    recs = L.regular_season_records()
    body = kpis([("Career record", f'{rec(at["w"], at["l"], at["t"])} ({pct(at["w"], at["l"], at["t"])})'),
                 ("Titles", str(at["titles"])), ("Playoff record", rec(pr["w"], pr["l"])),
                 ("Best finish", str(at["best"] or "-"))])
    head, body = body, ""
    seasons = []
    for y in reversed(L.years):
        t = next((t for t in L.teams_in(y) if t["manager"] == manager), None)
        if not t:
            continue
        s = L.standings.get(t["team_season_id"], {})
        r = recs.get((y, t["team_season_id"]), {"w": 0, "l": 0, "t": 0, "pf": 0})
        fin = "" if y not in L.finished else ("Champion" if s.get("rank") == 1 else f'{s.get("rank")}')
        seasons.append([str(y), e(t["team_name"]), rec(r["w"], r["l"], r["t"]), f1(r["pf"]), str(s.get("playoff_seed") or ""), e(fin)])
    arc = []
    for y in L.years:
        t = next((t for t in L.teams_in(y) if t["manager"] == manager), None)
        s = L.standings.get(t["team_season_id"], {}) if t else {}
        if t and y in L.finished:
            arc.append((y, s.get("rank"), t["team_name"]))
    if arc:
        body += V.finish_line(arc, 12, "Finish by season", "1 is the champion. The shaded band is playoff territory (top 6).")
    diff, cats, tips = [], [], []
    for y in L.years:
        t = next((t for t in L.teams_in(y) if t["manager"] == manager), None)
        g = list(L.final_games(y, regular=True))
        mine = [m["points"] for m in g if t and m["team_season_id"] == t["team_season_id"]]
        if not mine:
            continue
        lg = sum(m["points"] for m in g) / len(g)
        my = sum(mine) / len(mine)
        cats.append(str(y)[2:]); diff.append(my - lg)
        tips.append(f"<b>{y}</b><br>{my:.1f} per game vs league {lg:.1f}<br>{my - lg:+.1f}")
    if cats:
        body += V.vbars(cats, diff, "Points per game vs. the league average", "Regular season. Blue = above average, red = below.",
                        fmt="{:+.0f}", tips=tips, height=210)
    body += "<h2>Season by season</h2>" + table(["Season", "Team name", "Record", "PF", "Seed", "Finish"], seasons, num=(3, 4))
    streaks = [s for s in L.keeper_streaks() if s["manager"] == manager][:8]
    body += "<h2>Longest keeper streaks</h2>" + table(["Player", "Pos", "Years", "Streak"],
        [[e(s["player"]), e(s["pos"]), f'{s["start"]} to {s["end"]}', str(s["years"])] for s in streaks], num=(3,))
    body += F.team_h2h_table(L, h2h, manager, mlink, table)
    sl = f"team-{D.slug(manager)}"
    body = head + F.tabs(sl, [("overview", "Overview", body),
                              ("roster", f"{L.current} roster", F.team_roster_tab(L, manager, cur, table)),
                              ("drafts", "Drafts", F.team_drafts_tab(L, manager, collapsible)),
                              ("trades", "Trades", F.team_trades_tab(L, manager, wk_by_pid))])
    title = e(cur["team_name"]) if cur else e(manager)
    sub = f"{e(manager)}" + (f" &middot; {at['seasons']} seasons since {L.years[0]}" if at["seasons"] else "")
    return section(f"team-{D.slug(manager)}", title, sub, body, eyebrow="Team")


# --------------------------------------------------------------------- shell

def sidebar(L):
    def group(title, links, open_=False):
        items = "".join(f'<a class="nav-link" data-target="{t}">{lbl}</a>' for t, lbl in links)
        return f'<details class="sidebar-teams"{" open" if open_ else ""}><summary>{title}</summary><div class="sidebar-team-list">{items}</div></details>'
    logo = ""
    if LOGO.exists():
        logo = f'<img class="brand-logo" alt="" src="data:image/png;base64,{base64.b64encode(LOGO.read_bytes()).decode()}">'
    cur = sorted(L.teams_in(L.current), key=lambda t: t["manager"])
    teams = "".join(f'<a class="nav-link" data-target="team-{D.slug(t["manager"])}">{e(t["team_name"])}'
                    f'<span class="manager">{e(t["manager"])}</span></a>' for t in cur)
    former = [m for m in L.managers if m not in {t["manager"] for t in cur}]
    teams += "".join(f'<a class="nav-link" data-target="team-{D.slug(m)}">{e(m)}<span class="manager">former manager</span></a>' for m in former)
    return f"""
    <aside class="sidebar">
      <button class="brand-home" data-target="summary" type="button">
        {logo}
        <span class="brand-home-eyebrow">&#8962; League home</span>
        <span class="brand-title">{LEAGUE}</span>
        <span class="brand-home-sub">12-team keeper league &middot; {L.current}</span>
      </button>
      <h3>League</h3>
      {group("Commentary &amp; League Info", [("desk", "Commissioner's Desk"), ("league-rules", "League rules"), ("rules-history", "Rules history"), ("about", "About this site")])}
      {group("Standings &amp; Records", [("summary", "League home"), ("standings", f"{L.current} scores"), ("alltime", "All-time standings"), ("champions", "Champions &amp; awards"), ("records", "Record book"), ("playoffs", "Playoff history"), ("h2h", "Head-to-head")])}
      {group("Manager Resources", [("luck", "Luck report"), ("overunder", "Over &amp; under achievers"), ("positional", "Positional strength"), ("value-board", "FPOR value board"), ("player-search", "Player search"), ("player-compare", "Player comparison")])}
      {group("Draft &amp; Keepers", [("drafts", "Draft results"), ("keepers", "Keeper history"), ("firstround", "First-round history")])}
      {group("Transactions", [("trades", "Trades"), ("faab", "FAAB ledger"), ("txlog", "Transaction log")])}
      {group("Teams", [])[:-len('</div></details>')]}{teams}</div></details>
      <button class="fb-trigger" id="fb-trigger" type="button" aria-label="Open feedback form">
        <span class="fb-icon">&#9993;</span><span class="fb-label">Send feedback to Pete</span>
      </button>
    </aside>"""


def main():
    L = D.League(D.connect())
    C, corpus_js = F.corpus_script(L)
    wk_by_pid = F.weekly_by_pid(L)
    h2h = F.h2h_games(L)
    generated = datetime.now().strftime("%b %d, %Y %I:%M %p").replace(" 0", " ")
    parts = [sec_home(L, generated), sec_about(L), sec_desk(), sec_rules(), sec_rules_history(),
             sec_standings(L), sec_alltime(L), sec_champions(L), sec_records(L), sec_playoffs(L), sec_h2h(L, h2h),
             sec_luck(L), sec_overunder(L), sec_positional(L), sec_value(L), sec_search(L, C), sec_compare(L),
             sec_drafts(L), sec_keepers(L), sec_firstround(L),
             sec_trades(L), sec_faab(L), sec_txlog(L)]
    parts += [sec_team(L, m, generated, wk_by_pid, h2h) for m in L.managers]
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{LEAGUE}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}{EXTRA_CSS}{V.CHART_CSS}{DY.DYN_CSS}{F.FEAT_CSS}{F.H2H_CSS}</style>
</head>
<body>
<div class="layout">
<button class="menu-toggle" aria-label="Open menu" type="button"><span class="menu-icon"><span></span></span> Menu</button>
<button class="sidebar-tab" aria-label="Open menu" type="button"><span>Menu</span></button>
<div class="sidebar-backdrop"></div>
{sidebar(L)}
<main class="content">
<div class="crumb-bar"><button class="crumb-back" data-target="summary" type="button">&larr; League home</button><span class="crumb-sep">&rsaquo;</span><span class="crumb-current"></span></div>
{"".join(parts)}
{F.footer(L, generated)}
{corpus_js}
{FEEDBACK}
</main>
</div>
<script>{JS}</script>
<script>{V.CHART_JS}</script>
<script>{DY.DYN_JS}</script>
<script>{F.FEAT_JS}</script>
<script>{F.H2H_JS}</script>
</body>
</html>"""
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT.name}: {len(page) / 1024:,.0f} KB, {len(parts)} sections, generated {generated}")


if __name__ == "__main__":
    main()
