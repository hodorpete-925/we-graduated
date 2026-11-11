"""
wg_dynamic.py - the three season-picker pages ported from I Yearn:
FPOR value board, FAAB ledger and transaction log.

Each page has a season dropdown. Small per-season pieces (summary tables,
12-point charts) are rendered here as hidden panes; the big lists (cards,
every claim, every move) ship as compact JSON and are drawn in the browser
so the page stays small.
"""

import html
import json
from collections import defaultdict

import wg_charts as V
import wg_value as W

e = lambda s: html.escape(str(s if s is not None else ""))
POS = ["QB", "RB", "WR", "TE", "K", "DEF"]


def _j(obj):
    return json.dumps(obj, separators=(",", ":")).replace("</", "<\\/")


def season_select(sid, years, current):
    opts = "".join(f'<option value="{y}"{" selected" if y == current else ""}>{y}</option>' for y in reversed(years))
    return f'<label class="vb-filter yr-pick">Season <select class="season-select" data-for="{sid}">{opts}</select></label>'


def pane(season, current, body):
    return f'<div class="season-pane" data-season="{season}"{"" if season == current else " hidden"}>{body}</div>'


def _tbl(headers, rows, num=(), cls="roster"):
    th = "".join(f'<th class="{"num" if i in num else ""}">{h}</th>' for i, h in enumerate(headers))
    body = "".join("<tr>" + "".join(f'<td class="{"num" if i in num else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="table-scroll"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def _sgn(v, d=1):
    return f"{v:+.{d}f}"


def _cls(v, cut):
    return "pos-good" if v >= cut else "pos-bad" if v <= -cut else ""


# ------------------------------------------------------------------ value board

def value_board(L, mlink):
    data, panes, hist = {}, "", []
    for y in L.years:
        import wg_features as F
        rows, meta = F.value_rows(L, y)
        if not rows:
            continue
        kind_ix = {"pick": 0, "keeper": 1, "pickup": 2}
        pickups = sorted([r for r in rows if r["kind"] == "pickup"], key=lambda r: -r["fpor"])[:36]
        show = [r for r in rows if r["kind"] != "pickup"] + pickups
        data[y] = {"a": round(meta["a"], 2), "b": round(meta["b"], 4), "wk": meta["completed"], "k1": meta["k1"],
                   "repl": {k: round(v, 2) for k, v in meta["repl"].items()},
                   "r": [[r["name"], r["pos"], r["mgr"], kind_ix[r["kind"]], r["rnd"], r["pick"], r["games"],
                          round(r["pts"], 1), round(r["fpor"], 1), None if r["exp"] is None else round(r["exp"], 1),
                          None if r["z"] is None else round(r["z"], 2), r.get("how", "")] for r in show]}
        # per-manager summary (all pickups, not just the cards)
        S = defaultdict(lambda: {"pick": 0.0, "keeper": 0.0, "pickup": 0.0, "best": None})
        for r in rows:
            s = S[r["mgr"]]
            s[r["kind"]] += r["fpor"]
            if r["games"] >= W.MIN_WEEKS and r["exp"] is not None and r["kind"] == "pick":
                res = r["fpor"] - r["exp"]
                if s["best"] is None or res > s["best"][1]:
                    s["best"] = (r, res)
        order = sorted(S.items(), key=lambda kv: -(kv[1]["pick"] + kv[1]["keeper"] + kv[1]["pickup"]))
        trs = []
        for m, s in order:
            tot = s["pick"] + s["keeper"] + s["pickup"]
            b = s["best"]
            trs.append([mlink(m), f'<span class="{_cls(s["pick"], 30)}">{_sgn(s["pick"])}</span>',
                        f'<span class="{_cls(s["keeper"], 30)}">{_sgn(s["keeper"])}</span>',
                        f'<span class="{_cls(s["pickup"], 30)}">{_sgn(s["pickup"])}</span>', f"<b>{_sgn(tot)}</b>",
                        f'{e(b[0]["name"])} <span class="tl-via">Rd {b[0]["rnd"]}, {_sgn(b[1])} vs line</span>' if b else ""])
        segs = [("Draft (rounds 1 to 9)", V.BLUES[0]), ("Keepers", V.BLUES[2]), ("Pickups", V.BLUES[3])]
        chart = V.stacked_hbars(
            [(m, [max(0, s["pick"]), max(0, s["keeper"]), max(0, s["pickup"])],
              f'<b>{e(m)}</b><br>Draft {_sgn(s["pick"])}<br>Keepers {_sgn(s["keeper"])}<br>Pickups {_sgn(s["pickup"])}')
             for m, s in order], segs, f"{y}: where each team's value came from",
            "Positive FPOR by source; hover for the net figure (negatives are in the table).", show_total=False)
        body = chart + _tbl(["Manager", "Draft", "Keepers", "Pickups", "Total FPOR", "Best draft value"], trs, num=(1, 2, 3, 4))
        panes += pane(y, L.current, body)
        if y in L.finished or y == L.current:
            picks = [r for r in rows if r["kind"] == "pick" and r["games"] >= W.MIN_WEEKS]
            keeps = [r for r in rows if r["kind"] == "keeper" and r["games"] >= W.MIN_WEEKS]
            hist.append((y, sum(r["fpor"] for r in picks) / max(len(picks), 1), sum(r["fpor"] for r in keeps) / max(len(keeps), 1)))
    trend = V.vbars([str(h[0])[2:] for h in hist], [round(h[2] - h[1], 1) for h in hist],
                    "The keeper premium: average FPOR of a keeper minus a drafted player",
                    "Per player, every season since 2012. Hover for both averages.", fmt="{:+.0f}",
                    tips=[f"<b>{h[0]}</b><br>Keepers: {h[2]:+.1f} per player<br>Drafted (Rd 1 to 9): {h[1]:+.1f}<br>Premium: {h[2] - h[1]:+.1f}" for h in hist])
    guide = f"""<details class="vb-guide"><summary>How to read this board</summary><div class="vb-guide-body">
      <p><b>FPOR</b> (fantasy points over replacement) is points scored minus what a freely available player at the same position would have scored over the same weeks.
      Replacement is the Nth-best per-game scorer among rostered players: QB 15, RB 30, WR 42, TE 14, K 13, DEF 13 (WG starts QB, 2 RB, 3 WR, TE, K, DEF with no flex).</p>
      <p><b>The price line.</b> WG has no auction prices, so a pick's price is where it was taken. The dashed line is the FPOR an average pick at that slot has produced this season (rounds 1 to 9).
      Cards are shaded by how far each player sits above (blue) or below (red) the line, in standard deviations.
      Keepers and pickups have no pick price, so each is shaded against its own group's average.</p>
      <p><b>Counting.</b> Drafted players and keepers count every week on a roster in this league (weeks parked on IR are skipped); pickups count only the run of weeks on the team that claimed them. Only the top 36 pickups by FPOR get cards.</p>
      <p class="vb-guide-foot">Ported from the I Yearn value board. Points are Yahoo league scoring.</p></div></details>"""
    controls = f"""<div class="vb-filters">{season_select("value-board", list(data), L.current)}
      <label class="vb-filter">Manager <select id="vb-mgr"><option value="">All managers</option>
        {"".join(f'<option value="{e(m)}">{e(m)}</option>' for m in L.managers)}</select></label>
      <div class="vb-filter vb-chips" id="vb-pos"><button type="button" class="vb-chip vb-chip-all is-on" data-all="1">All</button>
        {"".join(f'<button type="button" class="vb-chip is-on" data-pos="{p}">{p}</button>' for p in POS)}</div></div>"""
    legend = """<div class="vb-legend"><span>Below the line</span><span class="vb-legend-bar"></span><span>Above the line</span>
      <span class="vb-legend-nd"><span class="vb-legend-swatch"></span>Fewer than 2 games</span></div>"""
    body = (guide + controls + '<div id="vb-kpis"></div><div id="vb-scatter"></div>' + legend +
            '<div class="vb-grid" id="vb-grid"></div><h2>By manager</h2>' + panes + "<h2>History</h2>" + trend +
            f"<script>window.WG_VB = {_j(data)};</script>")
    return body


# ------------------------------------------------------------------ FAAB ledger

def faab_ledger(L, mlink, offers_doc):
    """Same markup as I Yearn's render_faab_ledger (value_board_sections.py), one
    pane per season. WG-only charts sit after the I Yearn content."""
    data, panes, cpanes = {}, "", ""
    hist = []
    for y in L.years:
        claims, meta = W.faab_claims(L.c, L, y, offers_doc)
        if not claims:
            continue
        blank = lambda: {"spent": 0, "won": 0, "lost": 0, "over": 0, "fpor": 0.0, "best": None, "worst": None}
        S = {t["manager"]: blank() for t in L.teams_in(y)}
        for c in claims:
            s = S.setdefault(c["mgr"], blank())
            s["spent"] += c["bid"]; s["won"] += 1; s["fpor"] += c["fpor"]; s["over"] += c["over"] or 0
            if c["games"]:
                if s["best"] is None or c["fpor"] > s["best"]["fpor"]: s["best"] = c
                if s["worst"] is None or c["fpor"] < s["worst"]["fpor"]: s["worst"] = c
            for m, b, r in c["losers"]:
                S.setdefault(m, blank())["lost"] += 1
        MIN = 10
        eff = lambda s: s["fpor"] / s["spent"] if s["spent"] >= MIN else None
        ranked = sorted(S.items(), key=lambda kv: (eff(kv[1]) is None, -(eff(kv[1]) or 0), -kv[1]["spent"]))
        left = {}
        if y == L.current:
            for t in L.teams_in(y):
                fb = (L.stats.get(t["team_season_id"]) or {}).get("faab_balance")
                if fb is not None:
                    left[t["manager"]] = fb
        trs = []
        for m, s in ranked:
            ef = eff(s)
            best = f'{e(s["best"]["player"])} ({s["best"]["fpor"]:+.1f} for ${s["best"]["bid"]})' if s["best"] else ""
            worst = (f'{e(s["worst"]["player"])} ({s["worst"]["fpor"]:+.1f} for ${s["worst"]["bid"]})'
                     if s["worst"] and s["worst"] is not s["best"] else "")
            trs.append(f'<tr><td>{mlink(m)}</td><td class="num">{s["won"]}</td><td class="num">{s["lost"]}</td>'
                       f'<td class="num">${s["spent"]}</td><td class="num">${s["over"]}</td>'
                       f'<td class="num">{s["fpor"]:+.1f}</td><td class="num"><b>{f"<span class=tl-via>under ${MIN}</span>" if ef is None else f"{ef:+.2f}"}</b></td>'
                       f'<td class="num">{"" if left.get(m) is None else "$" + str(left[m])}</td>'
                       f'<td class="tl-small">{best}</td><td class="tl-small">{worst}</td></tr>')
        big = sorted([c for c in claims if (c["over"] or 0) > 0], key=lambda c: -c["over"])[:5]
        over = "".join(f'<li><b>{e(c["mgr"])}</b> paid ${c["bid"]} for {e(c["player"])} against a next-best ${c["bid"] - c["over"]}: ${c["over"]} over</li>' for c in big)
        nlost = sum(len(c["losers"]) for c in claims)
        body = (f'<p class="kb-hint" style="margin-top:0">{y}: {len(claims)} claims won, {nlost} losing offers behind them'
                f'{", through week " + str(meta["completed"]) if y == L.current else ""}.</p>'
                '<h2 class="tl-h2">Spending efficiency by manager</h2>'
                '<p class="kb-hint" style="margin-top:0">FPOR per $ is the headline: fantasy points over replacement the claimed players produced for that manager, divided by FAAB spent. '
                'Overpay is the gap between a winning bid and the next-best real offer (claims nobody else bid on count as $0 over). Managers under $10 spent are not ranked. Sorted most efficient first.</p>'
                '<table class="tl-summary fl-summary"><thead><tr><th>Manager</th><th class="num">Won</th><th class="num">Outbid</th><th class="num">Spent</th>'
                '<th class="num">Overpay</th><th class="num">FPOR bought</th><th class="num">FPOR / $</th><th class="num">FAAB left</th><th>Best buy</th><th>Worst buy</th></tr></thead>'
                f'<tbody>{"".join(trs)}</tbody></table>' +
                (f"<h2 class='tl-h2'>Biggest overpays</h2><ul class='fl-list'>{over}</ul>" if over else ""))
        panes += pane(y, L.current, body)
        # WG-only chart for the season, shown under the I Yearn content
        pts = [(s["spent"], round(s["fpor"], 1), m,
                f'<b>{e(m)}</b><br>${s["spent"]} on {s["won"]} claims<br>{_sgn(s["fpor"])} FPOR' + (f'<br>{eff(s):+.2f} per $' if eff(s) is not None else ""),
                V.ACCENT if s["fpor"] >= 0 else V.NEG) for m, s in S.items() if s["won"]]
        cpanes += pane(y, L.current, V.scatter_xy(pts, f"{y}: FAAB spent vs. FPOR bought", "Up and to the left is efficient: lots of value for little money.",
                                                  "FAAB spent ($)", "FPOR from claimed players", xfmt="${:g}"))
        data[y] = {"wk": meta["completed"], "c": [[c["date"], c["mgr"], c["player"], c["pos"], c["bid"],
                                                    [[m, b, (r or "lower offer").lower()] for m, b, r in c["losers"]],
                                                    c["over"], c["games"], round(c["pts"], 1), round(c["fpor"], 1)] for c in claims]}
        hist.append((y, sum(c["bid"] for c in claims), len(claims), sum(c["contested"] for c in claims)))
    trend = V.stacked_vbars([str(h[0])[2:] for h in hist],
                            [("Contested claims", V.BLUES[1], [h[3] for h in hist]), ("Uncontested", V.BLUES[3], [h[2] - h[3] for h in hist])],
                            "Waiver claims won per season", "Contested = at least one other team bid on the same player.", W=460)
    spend = V.vbars([str(h[0])[2:] for h in hist], [h[1] for h in hist], "FAAB spent per season", "All 12 teams, winning bids only.", fmt="${:,.0f}", W=460, height=230)
    mgr_opts = "".join(f'<option value="{e(m)}">{e(m)}</option>' for m in L.managers)
    body = (f'<div class="tl-app"><div class="vb-filters">{season_select("faab", list(data), L.current)}</div>' + panes +
            '<h2 class="tl-h2">Every claim</h2><div class="vb-filters">'
            f'<label class="vb-filter">Manager <select id="fl-mgr"><option value="">All managers</option>{mgr_opts}</select></label>'
            '<div class="vb-filter vb-chips" id="fl-type"><button type="button" class="vb-chip is-on" data-type="contested">Contested</button>'
            '<button type="button" class="vb-chip is-on" data-type="uncontested">Uncontested</button></div></div>'
            '<table class="tl-table fl-table"><thead><tr><th>Processed</th><th>Winner</th><th>Player</th><th class="num">Bid</th>'
            '<th>Other offers</th><th class="num">Over</th><th>Since pickup</th><th class="num">Pts / $</th></tr></thead><tbody id="fl-body"></tbody></table>'
            '<p class="kb-hint">"Since pickup" counts only weeks the player was on the claiming manager\'s roster. A $0 bid won on waiver priority shows as free. '
            'Free-agent adds (no waiver period) are not claims and are not here; see the transaction log. Winning bids come from the Yahoo API; losing offers from '
            'Yahoo\'s FAB Offers page for every season, last read Nov 9, 2026.</p>'
            '<h2>Charts</h2>' + cpanes + '<div class="viz-grid2">' + trend + spend + '</div></div>'
            f"<script>window.WG_FL = {_j(data)};</script>")
    return body


# --------------------------------------------------------------- transaction log

def transaction_log(L, mlink):
    """Same markup as I Yearn's render_transaction_log, one pane per season."""
    data, panes, cpanes, hist = {}, "", "", []
    pid_ix = {}
    pnames = []

    def pref(pid):
        if pid not in pid_ix:
            p = L.players[pid]
            pid_ix[pid] = len(pnames)
            pnames.append(f'{p["player_name"]} ({W.norm_pos(p["position"])})')
        return pid_ix[pid]

    for y in L.years:
        txns = L.c.execute("""SELECT transaction_id, timestamp, event_type, faab_bid FROM transactions
                              WHERE season=? AND status='successful' ORDER BY timestamp DESC, yahoo_transaction_id DESC""", (y,)).fetchall()
        legs = defaultdict(list)
        for r in L.c.execute("""SELECT tp.transaction_id, tp.player_id, tp.direction, tp.team_season_id, tp.source_type, tp.counterparty_team_season_id
                                FROM transaction_players tp JOIN transactions t USING(transaction_id) WHERE t.season=?""", (y,)):
            legs[r[0]].append(tuple(r)[1:])
        picks = defaultdict(list)
        for r in L.c.execute("""SELECT tk.transaction_id, tk.draft_round, tk.source_team_season_id, tk.destination_team_season_id
                                FROM transaction_picks tk JOIN transactions t USING(transaction_id) WHERE t.season=?""", (y,)):
            picks[r[0]].append(tuple(r)[1:])
        S = defaultdict(lambda: {"adds": 0, "drops": 0, "trades": 0, "bids": 0, "faab": 0})
        for t in L.teams_in(y):
            S[t["manager"]]
        rows = []
        for tid, ts, et, faab in txns:
            Lg = legs.get(tid, [])
            if not Lg and et == "commish":
                continue
            d = str(ts)[:10]
            if et == "trade":
                sides = defaultdict(lambda: [[], []])
                for pid, di, tsid, st, cp in Lg:
                    sides[tsid][0].append(pref(pid))
                for rd, s_, dst in picks.get(tid, []):
                    sides[dst][1].append(rd)
                for tsid in sides:
                    S[L.mgr(tsid)]["trades"] += 1
                rows.append([d, "t", [[L.mgr(k), v[0], v[1]] for k, v in sides.items()]])
                continue
            tsid = next((x[2] for x in Lg if x[2] is not None), None)
            m = L.mgr(tsid)
            ins = [pref(x[0]) for x in Lg if x[1] == "incoming"]
            outs = [pref(x[0]) for x in Lg if x[1] != "incoming"]
            src = next((x[3] for x in Lg if x[1] == "incoming"), None)
            if ins: S[m]["adds"] += 1
            if outs: S[m]["drops"] += 1
            if faab: S[m]["faab"] += int(faab); S[m]["bids"] += 1
            kind = "ad" if ins and outs else ("a" if ins else "d")
            rows.append([d, kind, m, ins, outs, int(faab) if faab else 0, "w" if src == "waivers" else ("f" if src == "freeagents" else "")])
        data[y] = rows
        left = {}
        if y == L.current:
            for t in L.teams_in(y):
                fb = (L.stats.get(t["team_season_id"]) or {}).get("faab_balance")
                if fb is not None:
                    left[t["manager"]] = fb
        order = sorted(S.items(), key=lambda kv: (-(kv[1]["adds"] + kv[1]["drops"] + kv[1]["trades"]), kv[0]))
        trs = "".join(f'<tr><td>{mlink(m)}</td><td class="num">{s["adds"]}</td><td class="num">{s["drops"]}</td>'
                      f'<td class="num">{s["trades"]}</td><td class="num">{s["bids"]}</td><td class="num">${s["faab"]}</td>'
                      f'<td class="num">{"" if left.get(m) is None else "$" + str(left[m])}</td></tr>' for m, s in order)
        panes += pane(y, L.current,
                      f'<p class="kb-hint" style="margin-top:0">{y}: every move on Yahoo, newest first: {len(rows)} waiver claims, free-agent adds, drops and trades.</p>'
                      '<h2 class="tl-h2">By manager</h2><table class="tl-summary"><thead><tr><th>Manager</th><th class="num">Adds</th><th class="num">Drops</th>'
                      '<th class="num">Trades</th><th class="num">Bids won</th><th class="num">FAAB spent</th><th class="num">FAAB left</th></tr></thead>'
                      f'<tbody>{trs}</tbody></table>')
        segs = [("Adds", V.BLUES[1]), ("Trades", "#e1b523")]
        cpanes += pane(y, L.current, V.stacked_hbars(
            [(m, [s["adds"], s["trades"]], f'<b>{e(m)}</b><br>{s["adds"]} adds, {s["drops"]} drops<br>{s["trades"]} trades<br>{s["bids"]} winning bids, ${s["faab"]}')
             for m, s in order], segs, f"{y}: moves by manager", "Adds (including add/drops) and trades. Hover for drops and FAAB."))
        hist.append((y, sum(s["adds"] for s in S.values()), sum(1 for r in rows if r[1] == "t")))
    trend = V.stacked_vbars([str(h[0])[2:] for h in hist], [("Adds", V.BLUES[1], [h[1] for h in hist]), ("Trades", "#e1b523", [h[2] for h in hist])],
                            "League moves per season", f"{L.current} is in progress.")
    mgr_opts = "".join(f'<option value="{e(m)}">{e(m)}</option>' for m in L.managers)
    body = (f'<div class="tl-app"><div class="vb-filters">{season_select("txlog", list(data), L.current)}</div>' + panes +
            '<h2 class="tl-h2">All moves</h2><div class="vb-filters">'
            f'<label class="vb-filter">Manager <select id="tl-mgr"><option value="">All managers</option>{mgr_opts}</select></label>'
            '<div class="vb-filter vb-chips" id="tl-type"><button type="button" class="vb-chip vb-chip-all is-on" data-all="1">All</button>'
            '<button type="button" class="vb-chip is-on" data-type="add">Adds</button><button type="button" class="vb-chip is-on" data-type="add/drop">Add / drop</button>'
            '<button type="button" class="vb-chip is-on" data-type="drop">Drops</button><button type="button" class="vb-chip is-on" data-type="trade">Trades</button></div></div>'
            '<table class="tl-table"><thead><tr><th>Date</th><th>Type</th><th>Manager</th><th>Detail</th><th class="num">Bid</th></tr></thead>'
            '<tbody id="tl-body"></tbody></table>'
            '<p class="kb-hint">Source: Yahoo Fantasy Sports API, pulled on every refresh. Off-season trades never entered in Yahoo are not here.</p>'
            "<h2>Charts</h2>" + cpanes + trend + '</div>'
            f"<script>window.WG_TL = {_j(data)}; window.WG_P = {_j(pnames)};</script>")
    return body


# ------------------------------------------------------------------------- CSS/JS

DYN_CSS = """
.vb-filters { display: flex; flex-wrap: wrap; gap: 12px 22px; align-items: center; margin: 4px 0 14px; }
.vb-filter { font-size: 12.5px; color: var(--gray-600); display: flex; align-items: center; gap: 8px; }
.vb-filter select { font: inherit; font-size: 13px; padding: 5px 8px; border: 1px solid #d8d8dc; border-radius: 6px; background: #fff; color: #000; }
.yr-pick select { font-weight: 600; color: var(--blue-800); border-color: var(--blue-400); }
.vb-chips { gap: 6px; flex-wrap: wrap; }
.vb-chip { font: inherit; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 999px; border: 1px solid #d8d8dc; background: #fff; color: var(--gray-500); cursor: pointer; }
.vb-chip.is-on { background: var(--blue-800); border-color: var(--blue-800); color: #fff; }
.vb-chip-all { margin-right: 4px; }
.vb-chip-all.is-on { background: var(--gray-700); border-color: var(--gray-700); }
.vb-legend { display: flex; align-items: center; gap: 10px; font-size: 12px; color: var(--gray-600); margin: 0 0 14px; flex-wrap: wrap; }
.vb-legend-bar { display: inline-block; width: 180px; height: 10px; border-radius: 5px; background: linear-gradient(90deg, #e34948, #f2a3a3 30%, #f0efec 50%, #86b6ef 70%, #1761A0); }
.vb-legend-nd { margin-left: 14px; display: inline-flex; align-items: center; gap: 6px; }
.vb-legend-swatch { display: inline-block; width: 14px; height: 10px; border-radius: 3px; background: var(--gray-100); border: 1px dashed #d8d8dc; }
.vb-grid { display: flex; flex-direction: column; gap: 4px; margin-bottom: 18px; }
.vb-row { display: grid; grid-template-columns: 96px 1fr; gap: 10px; align-items: start; padding: 6px 0; border-top: 1px solid var(--gray-100); }
.vb-rowlabel { font-size: 13px; font-weight: 700; color: var(--gray-700); }
.vb-rowsub { font-size: 11px; color: var(--gray-500); line-height: 1.3; margin-top: 2px; }
.vb-cards { display: flex; flex-wrap: wrap; gap: 6px; }
.vb-card { width: 128px; min-height: 64px; padding: 7px 8px 6px; border-radius: 8px; background: var(--gray-100); color: #000; border: 1px solid rgba(0,0,0,.04); transition: transform .08s ease; }
.vb-card:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,.14); }
.vb-card.dark { color: #fff; }
.vb-card.dark .vb-sub, .vb-card.dark .vb-mgr, .vb-card.dark .vb-ppd { color: rgba(255,255,255,.82); }
.vb-card.vb-nodata { background: var(--gray-50); border: 1px dashed #d8d8dc; color: var(--gray-600); }
.vb-name { font-size: 12.5px; font-weight: 600; line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.vb-sub { font-size: 10.5px; color: rgba(0,0,0,.62); margin-top: 1px; }
.vb-mgr { font-size: 10.5px; color: rgba(0,0,0,.72); margin-top: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.vb-foot { display: flex; justify-content: space-between; align-items: baseline; margin-top: 3px; gap: 4px; }
.vb-fpor { font-size: 14px; font-weight: 700; font-variant-numeric: tabular-nums; }
.vb-ppd { font-size: 10px; color: rgba(0,0,0,.6); font-variant-numeric: tabular-nums; white-space: nowrap; }
.vb-guide { margin: 0 0 14px; border: 1px solid var(--gray-200); border-radius: 10px; background: var(--gray-50); }
.vb-guide summary { cursor: pointer; padding: 10px 14px; font-size: 13px; font-weight: 600; color: var(--blue-800); list-style: none; display: flex; align-items: center; gap: 8px; }
.vb-guide summary::-webkit-details-marker { display: none; }
.vb-guide summary::before { content: '?'; display: inline-flex; width: 18px; height: 18px; border-radius: 50%; background: var(--blue-800); color: #fff; font-size: 11px; align-items: center; justify-content: center; font-weight: 700; }
.vb-guide[open] summary { border-bottom: 1px solid var(--gray-200); }
.vb-guide-body { padding: 10px 16px 6px; font-size: 13.5px; line-height: 1.55; max-width: 860px; }
.vb-guide-body p { margin: 0 0 10px; }
.vb-guide-foot { font-size: 12px; color: var(--gray-500); }
.vb-repl { display: flex; flex-wrap: wrap; gap: 6px 8px; align-items: center; margin: 0 0 14px; font-size: 13px; }
.vb-repl-k { color: var(--gray-500); font-size: 12px; margin-right: 4px; }
.vb-repl-i { background: var(--gray-100); border-radius: 999px; padding: 3px 10px; font-variant-numeric: tabular-nums; }
.vb-repl-i b { color: var(--blue-800); margin-right: 3px; }
@media (max-width: 720px) {
  .vb-row { grid-template-columns: 1fr; gap: 4px; }
  .vb-card { width: calc(50% - 3px); }
}

.tl-small { color: var(--gray-500); font-size: 12px; }
.tl-summary a { color: inherit; text-decoration: none; }
/* Copied verbatim from I Yearn dashboard.html (2026-11-11): transaction log + FAAB ledger */
.kb-hint { color:#606C71; font-size:12px; margin:10px 0 0; }
.vb-app, .tl-app { max-width: 1240px; }
.vb-filters { display: flex; flex-wrap: wrap; gap: 14px 22px; align-items: center; margin: 4px 0 14px; }
.vb-filter { font-size: 12.5px; color: var(--gray-600); display: flex; align-items: center; gap: 8px; }
.vb-filter select { font: inherit; font-size: 13px; padding: 5px 8px; border: 1px solid var(--gray-200); border-radius: 6px; background: #fff; color: #000; }
.vb-chips { gap: 6px; }
.vb-chip { font: inherit; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 999px; border: 1px solid var(--gray-200); background: #fff; color: var(--gray-500); cursor: pointer; }
.vb-chip.is-on { background: var(--blue-800); border-color: var(--blue-800); color: #fff; }
.vb-chip-all { margin-right: 4px; }
.vb-chip-all.is-on { background: var(--gray-700); border-color: var(--gray-700); }
.tl-h2 { font-size: 15px; font-weight: 600; margin: 18px 0 8px; color: var(--gray-700); }
.tl-summary, .tl-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.tl-summary th, .tl-table th { text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: var(--gray-500); font-weight: 600; padding: 6px 8px; border-bottom: 1px solid var(--gray-200); }
.tl-summary td, .tl-table td { padding: 7px 8px; border-bottom: 1px solid var(--gray-100); vertical-align: top; }
.tl-summary .num, .tl-table .num { text-align: right; font-variant-numeric: tabular-nums; }
.tl-date { white-space: nowrap; color: var(--gray-600); font-variant-numeric: tabular-nums; }
.tl-mgr { white-space: nowrap; font-weight: 600; }
.tl-faab { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.tl-badge { display: inline-block; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 999px; white-space: nowrap; }
.tl-add { background: rgba(28,122,74,.14); color: #1c7a4a; }
.tl-drop { background: rgba(180,35,24,.12); color: #b42318; }
.tl-adddrop { background: rgba(2,36,121,.10); color: var(--blue-800); }
.tl-trade { background: rgba(225,181,35,.22); color: #7a5d05; }
.tl-in { color: #1c7a4a; font-weight: 600; }
.tl-out { color: #b42318; }
.tl-via { color: var(--gray-500); font-size: 12px; }
.tl-side { line-height: 1.4; }
.tl-row.is-hidden { display: none; }
.fl-summary td.tl-small { font-size: 12px; color: var(--gray-600); }
.fl-loser { font-size: 12.5px; line-height: 1.4; white-space: nowrap; }
.fl-list { font-size: 13.5px; line-height: 1.6; margin: 0 0 6px 18px; padding: 0; }
@media (max-width: 720px) {
  .tl-table:not(.fl-table) th:nth-child(2), .tl-table:not(.fl-table) td:nth-child(2) { display: none;}
  .tl-summary { font-size: 12px;}
}
@media (max-width: 720px) {
  .fl-summary th:nth-child(n+9), .fl-summary td:nth-child(n+9) { display: none;}
  .fl-table th:nth-child(1), .fl-table td:nth-child(1),
  .fl-table th:nth-child(6), .fl-table td:nth-child(6),
  .fl-table th:nth-child(7), .fl-table td:nth-child(7),
  .fl-table th:nth-child(8), .fl-table td:nth-child(8) { display: none;}
  .fl-table { font-size: 12.5px;}
  .fl-loser { white-space: normal;}
  .fl-loser .tl-via { display: none;}
}
"""

DYN_JS = r"""
(function(){
  const esc = s => String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
  const fd = d => { const p = String(d).split('-'); return p.length < 3 ? d : ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+p[1] - 1] + ' ' + (+p[2]); };
  const sg = (v, d) => (v >= 0 ? '+' : '') + Number(v).toFixed(d === undefined ? 1 : d);
  function mix(a, b, t) { const p = c => [1,3,5].map(i => parseInt(c.slice(i, i+2), 16)); const x = p(a), y = p(b);
    return '#' + x.map((v, i) => Math.round(v + (y[i] - v) * t).toString(16).padStart(2, '0')).join(''); }
  function zFill(z) { if (z == null) return null; const t = Math.max(-1, Math.min(1, z / 2));
    if (t >= 0) return t < .5 ? mix('#f0efec', '#86b6ef', t * 2) : mix('#86b6ef', '#1761A0', (t - .5) * 2);
    return -t < .5 ? mix('#f0efec', '#f2a3a3', -t * 2) : mix('#f2a3a3', '#e34948', (-t - .5) * 2); }
  // chips: click isolates, gray pills add back, All restores (same as I Yearn)
  window.vbChips = function(container, onChange) {
    if (!container) return;
    const opts = Array.from(container.querySelectorAll('.vb-chip:not(.vb-chip-all)'));
    const all = container.querySelector('.vb-chip-all');
    function sync() { const on = opts.filter(c => c.classList.contains('is-on')); if (all) all.classList.toggle('is-on', on.length === opts.length); onChange(); }
    opts.forEach(c => c.addEventListener('click', () => {
      const on = opts.filter(x => x.classList.contains('is-on'));
      if (on.length === opts.length) opts.forEach(x => x.classList.toggle('is-on', x === c));
      else if (c.classList.contains('is-on')) { if (on.length === 1) opts.forEach(x => x.classList.add('is-on')); else c.classList.remove('is-on'); }
      else c.classList.add('is-on');
      sync(); }));
    if (all) all.addEventListener('click', () => { opts.forEach(x => x.classList.add('is-on')); sync(); });
  };
  const RENDER = {};
  document.querySelectorAll('.season-select').forEach(sel => {
    const sec = document.getElementById(sel.dataset.for);
    const go = () => { sec.querySelectorAll('.season-pane').forEach(p => p.hidden = p.dataset.season !== sel.value);
      if (RENDER[sel.dataset.for]) RENDER[sel.dataset.for](sel.value); };
    sel.addEventListener('change', go);
    setTimeout(go, 0);
  });
  const cur = id => { const s = document.querySelector('.season-select[data-for="' + id + '"]'); return s ? s.value : null; };

  // ---------------- scatter (value board)
  function ticks(lo, hi) { const span = (hi - lo) || 1, raw = span / 5, mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(s => s >= raw); const out = [Math.floor(lo / step) * step];
    while (out[out.length - 1] < hi - 1e-9) out.push(out[out.length - 1] + step); return out; }
  function scatter(pts, o) {
    const W = 760, H = 380, L = 52, R = 20, T = 14, B = 40;
    const xt = ticks(Math.min(0, ...pts.map(p => p.x)), Math.max(...pts.map(p => p.x)));
    const yt = ticks(Math.min(0, ...pts.map(p => p.y)), Math.max(...pts.map(p => p.y)));
    const x0 = xt[0], x1 = xt[xt.length - 1], y0 = yt[0], y1 = yt[yt.length - 1];
    const px = v => L + (W - L - R) * (v - x0) / (x1 - x0), py = v => T + (H - T - B) * (y1 - v) / (y1 - y0);
    let s = yt.map(t => `<line x1="${L}" x2="${W - R}" y1="${py(t)}" y2="${py(t)}" stroke="#ebebed"/><text x="${L - 6}" y="${py(t) + 4}" text-anchor="end" font-size="11" fill="#8e8e93">${t}</text>`).join('');
    s += xt.map(t => `<text x="${px(t)}" y="${H - 22}" text-anchor="middle" font-size="11" fill="#8e8e93">${t}</text>`).join('');
    if (y0 < 0) s += `<line x1="${L}" x2="${W - R}" y1="${py(0)}" y2="${py(0)}" stroke="#8e8e93"/>`;
    s += `<text x="${(L + W - R) / 2}" y="${H - 4}" text-anchor="middle" font-size="11" fill="#606C71">${o.xl}</text>`;
    s += `<text x="12" y="${(T + H - B) / 2}" font-size="11" fill="#606C71" transform="rotate(-90 12 ${(T + H - B) / 2})" text-anchor="middle">${o.yl}</text>`;
    if (o.line) { const [a, b, lx0, lx1] = o.line;
      s += `<line x1="${px(lx0)}" y1="${py(a + b * lx0)}" x2="${px(lx1)}" y2="${py(a + b * lx1)}" stroke="#1d1d1f" stroke-width="1.5" stroke-dasharray="5 4"/>` +
           `<text x="${px(lx1)}" y="${py(a + b * lx1) - 7}" text-anchor="end" font-size="10.5" fill="#1d1d1f">price line</text>`; }
    if (o.band) s += `<rect x="${px(o.band[0])}" y="${T}" width="${px(o.band[1]) - px(o.band[0])}" height="${H - T - B}" fill="#1761A0" opacity=".04"/>` +
      `<text x="${px(o.band[0]) + 6}" y="${T + 12}" font-size="10.5" fill="#8e8e93">keeper slots</text>`;
    s += pts.map(p => `<circle cx="${px(p.x)}" cy="${py(p.y)}" r="${p.hl ? 6 : 4.5}" fill="${p.c}" stroke="#fff" stroke-width="1.2" opacity="${p.dim ? .25 : 1}" data-tip="${esc(p.tip)}"/>`).join('');
    const leg = (o.legend || []).map(([n, c]) => `<span><i style="background:${c}"></i>${n}</span>`).join('');
    return `<div class="viz"><div class="viz-title">${o.title}</div><div class="viz-sub">${o.sub}</div><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(o.title)}">${s}</svg><div class="viz-legend">${leg}</div></div>`;
  }

  // ---------------- value board
  if (window.WG_VB) {
    const grid = document.getElementById('vb-grid'), sel = document.getElementById('vb-mgr');
    const chips = Array.from(document.querySelectorAll('#vb-pos .vb-chip:not(.vb-chip-all)'));
    let season = null;
    function draw() {
      const D = window.WG_VB[season]; if (!D) return;
      const mgr = sel.value, on = new Set(chips.filter(c => c.classList.contains('is-on')).map(c => c.dataset.pos));
      const ok = r => on.has(r[1]) && (!mgr || r[2] === mgr);
      document.getElementById('vb-kpis').innerHTML = '<div class="vb-repl"><span class="vb-repl-k">Replacement per game</span>' + ['QB','RB','WR','TE','K','DEF'].map(p =>
        `<span class="vb-repl-i"><b>${p}</b> ${(D.repl[p] || 0).toFixed(1)}</span>`).join('') + '</div>';
      const picks = D.r.filter(r => r[3] < 2 && r[6] >= 1);
      const maxPick = Math.max(...D.r.filter(r => r[3] === 0).map(r => r[5]));
      const minKeep = Math.min(...D.r.filter(r => r[3] === 1).map(r => r[5]));
      const pts = picks.map(r => ({x: r[5], y: r[8], c: r[3] === 0 ? '#1761A0' : '#86b6ef', dim: !ok(r), hl: mgr && r[2] === mgr,
        tip: `<b>${esc(r[0])}</b> ${r[1]}<br>${esc(r[2])}, ${r[3] ? 'keeper (Rd ' + r[4] + ')' : 'Rd ' + r[4] + ', pick ' + r[5]}<br>${r[7]} pts in ${r[6]} g<br><b>${sg(r[8])} FPOR</b>` + (r[9] != null ? `<br>Line: ${sg(r[9])}` : '')}));
      document.getElementById('vb-scatter').innerHTML = scatter(pts, {title: `${season}: FPOR by draft slot`,
        sub: `Every pick and keeper, through week ${D.wk}. Dashed line = what an average pick at that slot produced. Use the filters to spotlight a manager or position.`,
        xl: 'Overall pick', yl: 'FPOR', line: [D.a, D.b, 1, maxPick], band: isFinite(minKeep) ? [minKeep - .5, Math.max(...D.r.map(r => r[5] || 0)) + .5] : null,
        legend: [['Drafted (Rd 1 to 9)', '#1761A0'], ['Keeper', '#86b6ef']]});
      if (window.wgCharts) { wgCharts.wrap(document.getElementById('vb-scatter')); setTimeout(wgCharts.cue, 30); }
      const groups = [];
      for (let rd = 1; rd < D.k1; rd++) groups.push([`Round ${rd}`, '', D.r.filter(r => r[3] === 0 && r[4] === rd)]);
      groups.push(['Keepers', `Rounds ${D.k1}+`, D.r.filter(r => r[3] === 1)]);
      groups.push(['Pickups', 'top 36 by FPOR', D.r.filter(r => r[3] === 2)]);
      grid.innerHTML = groups.map(([lab, sub, rows]) => {
        const cards = rows.filter(ok).sort((a, b) => a[3] === 0 ? a[5] - b[5] : b[8] - a[8]).map(r => {
          const f = zFill(r[10]), dark = r[10] != null && Math.abs(r[10]) > 1.3;
          const tip = `<b>${esc(r[0])}</b> ${r[1]} &middot; ${esc(r[2])}<br>${r[3] === 2 ? esc(r[11]) : r[3] === 1 ? 'Keeper' : 'Pick ' + r[5]}` +
            `<br>${r[6]} games, ${r[7]} pts (${r[6] ? (r[7] / r[6]).toFixed(1) : '0'}/g)<br>Replacement: ${(D.repl[r[1]] || 0).toFixed(1)}/g<br><b>FPOR ${sg(r[8])}</b>` +
            (r[9] != null ? `<br>${r[3] === 0 ? 'Price line' : 'Group average'}: ${sg(r[9])}` : '') + (r[10] != null ? `<br>${sg(r[10], 2)} sd` : '');
          return `<div class="vb-card${f ? '' : ' vb-nodata'}${dark ? ' dark' : ''}" style="${f ? 'background:' + f : ''}" data-tip="${esc(tip)}">` +
            `<div class="vb-name">${esc(r[0])}</div><div class="vb-sub">${r[1]} &middot; ${r[3] === 0 ? '#' + r[5] : r[3] === 1 ? 'Kept' : esc(r[11])}</div>` +
            `<div class="vb-mgr">${esc(r[2])}</div><div class="vb-foot"><span class="vb-fpor">${sg(r[8])}</span><span class="vb-ppd">${r[6]} g</span></div></div>`; }).join('');
        return cards ? `<div class="vb-row"><div><div class="vb-rowlabel">${lab}</div><div class="vb-rowsub">${sub}</div></div><div class="vb-cards">${cards}</div></div>` : '';
      }).join('') || '<p class="note">No players match these filters.</p>';
    }
    RENDER['value-board'] = s => { season = s; draw(); };
    sel.addEventListener('change', draw);
    vbChips(document.getElementById('vb-pos'), draw);
  }

  // ---------------- FAAB ledger: every claim (I Yearn markup)
  if (window.WG_FL) {
    const body = document.getElementById('fl-body'), sel = document.getElementById('fl-mgr');
    const chips = Array.from(document.querySelectorAll('#fl-type .vb-chip'));
    function draw() {
      const D = window.WG_FL[cur('faab')]; if (!D) return;
      const mgr = sel.value, on = new Set(chips.filter(c => c.classList.contains('is-on')).map(c => c.dataset.type));
      body.innerHTML = D.c.map(c => {
        const t = c[5].length ? 'contested' : 'uncontested';
        const hid = !(on.has(t) && (!mgr || c[1] === mgr));
        const los = c[5].length ? c[5].slice().sort((a, b) => b[1] - a[1]).map(l => `<div class="fl-loser">${esc(l[0])} $${l[1]} <span class="tl-via">${esc(l[2])}</span></div>`).join('') : '<span class="tl-via">uncontested</span>';
        const over = c[6] == null ? '' : (c[6] > 0 ? '$' + c[6] : '$0');
        const prod = c[7] ? `${sg(c[9])} FPOR in ${c[7]} g` : '<span class="tl-via">no games yet</span>';
        const ppd = c[7] ? (c[4] ? (c[8] / c[4]).toFixed(1) : (c[8] ? 'free' : '')) : '';
        return `<tr class="tl-row${hid ? ' is-hidden' : ''}" data-mgr="${esc(c[1])}" data-type="${t}"><td class="tl-date">${c[0]}</td><td class="tl-mgr">${esc(c[1])}</td>` +
          `<td><b>${esc(c[2])}</b> <span class="tl-via">${c[3]}</span></td><td class="num"><b>$${c[4]}</b></td><td>${los}</td><td class="num">${over}</td><td>${prod}</td><td class="num">${ppd}</td></tr>`; }).join('');
    }
    RENDER['faab'] = draw;
    sel.addEventListener('change', draw);
    vbChips(document.getElementById('fl-type'), draw);
  }

  // ---------------- transaction log: all moves (I Yearn markup, no row limit)
  if (window.WG_TL) {
    const body = document.getElementById('tl-body'), sel = document.getElementById('tl-mgr');
    const chips = Array.from(document.querySelectorAll('#tl-type .vb-chip:not(.vb-chip-all)'));
    const P = window.WG_P, names = ix => ix.map(i => esc(P[i])).join(', ');
    const T = {a: 'add', d: 'drop', ad: 'add/drop', t: 'trade'};
    const B = {add: ['tl-add', 'Add'], drop: ['tl-drop', 'Drop'], 'add/drop': ['tl-adddrop', 'Add / drop']};
    let season = null;
    function build() {
      const D = window.WG_TL[season]; if (!D) return;
      body.innerHTML = D.map(r => {
        if (r[1] === 't') return `<tr class="tl-row" data-type="trade" data-mgr="${r[2].map(s => esc(s[0])).join('|')}"><td class="tl-date">${r[0]}</td>` +
          `<td><span class="tl-badge tl-trade">Trade</span></td><td class="tl-mgr">${r[2].map(s => esc(s[0])).join(' &harr; ')}</td>` +
          `<td class="tl-detail">${r[2].map(s => `<div class="tl-side"><b>${esc(s[0])}</b> gets ${[names(s[1]), ...s[2].map(k => 'R' + k + ' pick')].filter(Boolean).join(', ') || 'nothing'}</div>`).join('')}</td><td class="tl-faab"></td></tr>`;
        const k = T[r[1]], det = [];
        if (r[3].length) det.push(`<span class="tl-in">+ ${names(r[3])}</span><span class="tl-via">${r[6] === 'w' ? ' via waivers' : r[6] === 'f' ? ' free agent' : ''}</span>`);
        if (r[4].length) det.push(`<span class="tl-out">&minus; ${names(r[4])}</span>`);
        return `<tr class="tl-row" data-type="${k}" data-mgr="${esc(r[2])}"><td class="tl-date">${r[0]}</td><td><span class="tl-badge ${B[k][0]}">${B[k][1]}</span></td>` +
          `<td class="tl-mgr">${esc(r[2])}</td><td class="tl-detail">${det.join('<br>')}</td><td class="tl-faab">${r[5] ? '$' + r[5] : ''}</td></tr>`;
      }).join('');
      apply();
    }
    function apply() {
      const mgr = sel.value, on = new Set(chips.filter(c => c.classList.contains('is-on')).map(c => c.dataset.type));
      body.querySelectorAll('.tl-row').forEach(r => {
        const mgrOk = !mgr || r.dataset.mgr.split('|').includes(mgr);
        r.classList.toggle('is-hidden', !(mgrOk && on.has(r.dataset.type)));
      });
    }
    RENDER['txlog'] = s => { if (s !== season) { season = s; build(); } };
    sel.addEventListener('change', apply);
    vbChips(document.getElementById('tl-type'), apply);
  }
})();
"""
