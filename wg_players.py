"""
wg_players.py - the player corpus behind Player search, Player comparison and
the expandable rows on team rosters (ported from I Yearn's search cards).

For every player who has been on a We Graduated roster since 2012:
  * season lines: points, games, positional rank, who had him, how he got there
  * weekly points for his last three seasons in the league
  * the two players ranked just above and below him at his position each of those years
  * ownership lineage: one node per stint (drafted / kept / claimed / traded for),
    with what ended it (dropped, traded, not kept)
  * his last moves

Points and ranks only see rostered weeks: Yahoo gives us rostered players'
points, so "WR14" means 14th among WR who were on a WG roster that season.
"""

from collections import defaultdict
from datetime import date

import wg_value as W

WEEKS = 18


def _d(ts):
    return str(ts)[:10]


def _fmt_date(iso):
    y, m, d = iso.split("-")
    return f"{['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][int(m) - 1]} {int(d)}, {y}"


def build(L):
    c = L.c
    pos_of = {pid: W.norm_pos(p["position"]) for pid, p in L.players.items()}

    # ---- weekly points and season lines
    weekly = defaultdict(dict)            # (pid, season) -> {week: pts}
    games = defaultdict(int)
    owners = defaultdict(list)            # (pid, season) -> [mgr in roster order]
    by_mgr = defaultdict(lambda: defaultdict(float))   # (pid, season) -> {mgr: pts}
    for pid, s, wk, pts, tsid, slot in c.execute(
            "SELECT player_id, season, week, fantasy_points, team_season_id, selected_position "
            "FROM player_weekly_stats ORDER BY season, week"):
        weekly[(pid, s)][wk] = round(pts or 0.0, 1)
        if slot != "IR":
            games[(pid, s)] += 1
        m = L.mgr(tsid)
        by_mgr[(pid, s)][m] += pts or 0.0
        if not owners[(pid, s)] or owners[(pid, s)][-1] != m:
            owners[(pid, s)].append(m)
    season_pts = {k: sum(v.values()) for k, v in weekly.items()}

    # positional rank among rostered players, by season points
    by_pos = defaultdict(list)
    for (pid, s), p in season_pts.items():
        by_pos[(s, pos_of.get(pid, ""))].append((p, pid))
    rank, ranked = {}, {}
    for key, lst in by_pos.items():
        lst.sort(reverse=True)
        ranked[key] = lst
        for i, (_, pid) in enumerate(lst, 1):
            rank[(pid, key[0])] = i

    # ---- the event stream: draft picks and transactions
    events = defaultdict(list)            # pid -> [(iso, order, kind, mgr, detail)]
    for s, pid, rnd, pick, keeper, tsid in c.execute(
            "SELECT season, player_id, draft_round, overall_pick, is_keeper, team_season_id FROM draft_picks"):
        k1 = W.KEEPER_FIRST_ROUND.get(s, 10)
        kept = bool(keeper) or rnd >= k1
        events[pid].append((f"{s}-08-31", 0, "keep" if kept else "draft", L.mgr(tsid),
                            {"rnd": rnd, "pick": pick, "season": s}))
    legs = c.execute("""SELECT t.timestamp, t.season, t.event_type, t.faab_bid, tp.player_id, tp.direction,
                               tp.team_season_id, tp.source_type, tp.destination_type, tp.counterparty_team_season_id
                        FROM transactions t JOIN transaction_players tp USING(transaction_id)
                        WHERE t.status='successful' ORDER BY t.timestamp""").fetchall()
    for ts, s, et, bid, pid, di, tsid, src, dst, cp in legs:
        iso = _d(ts)
        if et == "trade":
            if di == "incoming":
                events[pid].append((iso, 2, "trade", L.mgr(tsid), {"from": L.mgr(cp) if cp else None}))
        elif di == "incoming":
            events[pid].append((iso, 2, "add", L.mgr(tsid), {"src": src, "bid": int(bid) if bid else 0}))
        else:
            events[pid].append((iso, 1, "drop", L.mgr(tsid), {}))

    # ---- assemble per player
    current = L.current
    cur_wk = c.execute("SELECT MAX(week) FROM player_weekly_stats WHERE season=?", (current,)).fetchone()[0]
    cur_owner = {pid: L.mgr(tsid) for pid, tsid in c.execute(
        "SELECT player_id, team_season_id FROM player_weekly_stats WHERE season=? AND week=?", (current, cur_wk))}
    pids = {pid for (pid, _) in weekly} | set(events)
    corpus = {}
    for pid in pids:
        p = L.players.get(pid)
        if not p:
            continue
        pos = pos_of.get(pid, "")
        seasons = sorted({s for (q, s) in weekly if q == pid} |
                         {e[4]["season"] for e in events.get(pid, []) if e[2] in ("draft", "keep")}, reverse=True)
        how = {}
        for iso, _, kind, m, det in events.get(pid, []):
            if kind in ("draft", "keep"):
                how[det["season"]] = "Kept" if kind == "keep" else f"Rd {det['rnd']}"
        lines = []
        for s in seasons:
            lines.append({"y": s, "pts": round(season_pts.get((pid, s), 0.0), 1), "g": games.get((pid, s), 0),
                          "rk": rank.get((pid, s)), "m": owners.get((pid, s)) or [], "how": how.get(s, ""),
                          "mp": [[m, round(v, 1)] for m, v in by_mgr.get((pid, s), {}).items()]})
        recent = [s for s in seasons if (pid, s) in weekly][:3]
        wk = {}
        for s in recent:
            arr = [weekly[(pid, s)].get(w) for w in range(1, WEEKS + 1)]
            while arr and arr[-1] is None:
                arr.pop()
            wk[s] = arr
        nbs = {}
        for s in recent:
            r = rank.get((pid, s))
            lst = ranked.get((s, pos), [])
            if r:
                nbs[s] = [[i + 1, q, round(v, 1)] for i, (v, q) in enumerate(lst) if abs(i + 1 - r) <= 2]
        corpus[pid] = {"id": pid, "n": p["player_name"], "p": pos, "nfl": p.get("nfl_team") or "",
                       "own": cur_owner.get(pid), "s": lines, "wk": wk, "nb": nbs,
                       "lin": _lineage(events.get(pid, []), {l["y"]: l["m"] for l in lines}, cur_owner.get(pid), current), "ev": _event_log(events.get(pid, [])),
                       "t": round(sum(season_pts.get((pid, s), 0.0) for s in seasons), 1)}
    return corpus


def _lineage(evs, owners_by_season, owner_now, current):
    """Stints: [mgr, how, first season, last season, kept count, how it ended].
    'end' is dropped / traded / not kept, or None while he is still on that roster."""
    out = []
    cur = None
    for iso, _, kind, m, det in sorted(evs, key=lambda e: (e[0], e[1])):
        yr = int(iso[:4]) if iso[5:7] >= "07" else int(iso[:4]) - 1
        if kind == "keep" and cur and cur["m"] == m and cur["end"] is None:
            cur["kept"] += 1
            cur["y1"] = yr
            continue
        if kind in ("draft", "keep", "add", "trade"):
            if cur and cur["end"] is None:
                cur["end"] = "traded" if kind == "trade" else "not kept"
            how = {"draft": f"Drafted Rd {det.get('rnd')}", "keep": "Kept",
                   "trade": f"Traded from {det.get('from') or '?'}",
                   "add": (f"Waivers ${det.get('bid', 0)}" if det.get("src") == "waivers" else "Free agent")}[kind]
            cur = {"m": m, "how": how, "y0": yr, "y1": yr, "kept": 0, "end": None, "d": iso}
            out.append(cur)
        elif kind == "drop" and cur and cur["m"] == m and cur["end"] is None:
            cur["end"] = "dropped"
            cur["y1"] = yr
    for i, x in enumerate(out):
        nxt = out[i + 1]["y0"] if i + 1 < len(out) else 9999
        boundary = i + 1 < len(out) and out[i + 1]["d"].endswith("-08-31")   # next stint starts at a draft
        yrs = [y for y, ms in owners_by_season.items() if x["m"] in ms and x["y0"] <= y and (y < nxt or (y == nxt and not boundary))]
        if yrs:
            x["y1"] = max(x["y1"], min(max(yrs), nxt))
        if x["end"] is None and not (i == len(out) - 1 and owner_now == x["m"]):
            x["end"] = "not kept"
    return [[x["m"], x["how"], x["y0"], x["y1"], x["kept"], x["end"]] for x in out]


def _event_log(evs, n=6):
    rows = []
    for iso, _, kind, m, det in sorted(evs, key=lambda e: (e[0], e[1])):
        if kind == "draft":
            txt = f"Drafted by {m} (round {det['rnd']}, pick {det['pick']})"
            when = f"{det['season']} draft"
        elif kind == "keep":
            txt = f"Kept by {m}"
            when = f"{det['season']} draft"
        elif kind == "trade":
            txt = f"Traded {det.get('from') or '?'} to {m}"
            when = _fmt_date(iso)
        elif kind == "add":
            txt = f"Claimed by {m} for ${det.get('bid', 0)}" if det.get("src") == "waivers" else f"Added by {m} (free agent)"
            when = _fmt_date(iso)
        else:
            txt = f"Dropped by {m}"
            when = _fmt_date(iso)
        rows.append([when, txt])
    return rows[-n:][::-1]
