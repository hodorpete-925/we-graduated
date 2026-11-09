"""
wg_value.py - FPOR (fantasy points over replacement) for We Graduated,
ported from I Yearn's value_over_cost.py and adapted:

  * WG starts QB, 2 RB, 3 WR, TE, K, DEF with no flex, so replacement is
    the Nth-best per-game scorer at each position among rostered players:
    QB 15, RB 30, WR 42, TE 14, K 13, DEF 13 (starters plus a little bench).
  * WG has no auction or DRC costs. The "price" of a drafted player is
    his overall pick, so the price line is an OLS fit of FPOR on overall
    pick for rounds 1 to 9 (rounds 10+ are keepers, placed at the back).
  * Keepers and in-season pickups get their own rows; they are compared
    with their own group's average, since neither has a pick price.

Only rostered player-weeks are in the database, so FPOR counts weeks a
player was on a roster in this league. Weeks parked in an IR slot are skipped.
"""

from collections import defaultdict
from datetime import date, timedelta

REPLACEMENT_RANK = {"QB": 15, "RB": 30, "WR": 42, "TE": 14, "K": 13, "DEF": 13}
MIN_WEEKS = 2
Z_CLIP = 2.0
KEEPER_FIRST_ROUND = {2020: 11}   # every other season: round 10


def norm_pos(p):
    p = (p or "").upper()
    return "DEF" if p in ("D/ST", "DST", "DEF") else p.split(",")[0]


def week_of(season, ts):
    """Yahoo week a waiver claim processed on `ts` first plays in. Week 1
    starts the Tuesday after Labor Day; claims run early Wednesday."""
    d = date.fromisoformat(str(ts)[:10])
    sep1 = date(season, 9, 1)
    labor = sep1 + timedelta(days=(7 - sep1.weekday()) % 7)
    return max(1, (d - (labor + timedelta(days=1))).days // 7 + 1)


def _ols(xs, ys):
    n = len(xs)
    if n < 3:
        return 0.0, 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return my, 0.0
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return my - b * mx, b


class Season:
    """Weekly points, replacement levels and roster-by-week for one season."""

    def __init__(self, conn, season, cap=None):
        self.season = season
        self.weekly = defaultdict(dict)        # pid -> {week: pts}
        self.team_week = {}                    # (pid, week) -> tsid
        weeks_with_points = set()
        for pid, wk, pts, tsid, slot in conn.execute(
                "SELECT player_id, week, fantasy_points, team_season_id, selected_position FROM player_weekly_stats WHERE season=?",
                (season,)):
            pts = float(pts or 0.0)
            self.team_week[(pid, wk)] = tsid
            if slot == "IR":        # an IR stash costs no lineup slot; skip the week
                continue
            self.weekly[pid][wk] = pts
            if pts:
                weeks_with_points.add(wk)
        self.completed = max(weeks_with_points) if weeks_with_points else 0
        if cap:
            self.completed = min(self.completed, cap)
        for pid in self.weekly:
            self.weekly[pid] = {w: p for w, p in self.weekly[pid].items() if w <= self.completed}
        self.pos_of = {pid: norm_pos(p) for pid, p in conn.execute("SELECT player_id, position FROM players")}
        ppg = defaultdict(list)
        for pid, wks in self.weekly.items():
            if len(wks) >= MIN_WEEKS:
                ppg[self.pos_of.get(pid)].append(sum(wks.values()) / len(wks))
        self.repl = {}
        for pos, rank in REPLACEMENT_RANK.items():
            vals = sorted(ppg.get(pos, []), reverse=True)
            self.repl[pos] = vals[min(rank, len(vals)) - 1] if vals else 0.0

    def fpor(self, pid, weeks=None):
        """(games, pts, fpor) over the given weeks (default: every rostered week)."""
        wk = self.weekly.get(pid, {})
        r = self.repl.get(self.pos_of.get(pid), 0.0)
        ws = [w for w in (weeks if weeks is not None else wk) if w in wk]
        pts = sum(wk[w] for w in ws)
        return len(ws), pts, pts - r * len(ws)

    def run_on_team(self, pid, tsid, start):
        """Consecutive weeks from `start` that the player sat on team `tsid`."""
        out, w = [], start
        while w <= self.completed:
            if self.team_week.get((pid, w)) == tsid:
                out.append(w)
            elif out:
                break
            elif w > start + 1:      # never showed up on the roster
                break
            w += 1
        return out


def value_board(conn, L, season):
    """Rows for the draft value board: every draft pick plus waiver/FA pickups.
    Returns (rows, meta). Each row: name, pos, mgr, kind (pick|keeper|pickup),
    rnd, pick, games, pts, ppg, repl, fpor, exp, z."""
    S = Season(conn, season, L.last_final_week(season))
    k1 = KEEPER_FIRST_ROUND.get(season, 10)
    rows = []
    for p in L.draft(season):
        pid = p["player_id"]
        g, pts, f = S.fpor(pid)
        keeper = bool(p["is_keeper"]) or p["draft_round"] >= k1
        rows.append({"pid": pid, "name": p["player_name"], "pos": S.pos_of.get(pid) or "", "mgr": L.mgr(p["team_season_id"]),
                     "kind": "keeper" if keeper else "pick", "rnd": p["draft_round"], "pick": p["overall_pick"],
                     "games": g, "pts": pts, "fpor": f, "repl": S.repl.get(S.pos_of.get(pid), 0.0)})
    drafted = {r["pid"] for r in rows}
    seen = set()
    for pid, tsid, ts, bid, src in conn.execute("""
            SELECT tp.player_id, tp.team_season_id, t.timestamp, t.faab_bid, tp.source_type
            FROM transactions t JOIN transaction_players tp USING(transaction_id)
            WHERE t.season=? AND t.status='successful' AND tp.direction='incoming'
              AND tp.source_type IN ('waivers','freeagents') ORDER BY t.timestamp""", (season,)):
        if pid in drafted or (pid, tsid) in seen:
            continue
        weeks = S.run_on_team(pid, tsid, week_of(season, ts))
        if not weeks:
            continue
        seen.add((pid, tsid))
        g, pts, f = S.fpor(pid, weeks)
        rows.append({"pid": pid, "name": L.players[pid]["player_name"], "pos": S.pos_of.get(pid) or "",
                     "mgr": L.mgr(tsid), "kind": "pickup", "rnd": None, "pick": None, "games": g, "pts": pts,
                     "fpor": f, "repl": S.repl.get(S.pos_of.get(pid), 0.0),
                     "how": (f"${bid}" if bid else "$0") + " claim" if src == "waivers" else "free agent"})
    fit = [r for r in rows if r["kind"] == "pick" and r["games"] >= MIN_WEEKS]
    a, b = _ols([r["pick"] for r in fit], [r["fpor"] for r in fit])
    for r in rows:
        r["exp"] = a + b * r["pick"] if r["kind"] == "pick" else None
    for kind in ("pick", "keeper", "pickup"):
        grp = [r for r in rows if r["kind"] == kind and r["games"] >= MIN_WEEKS]
        if kind != "pick":
            m = sum(r["fpor"] for r in grp) / len(grp) if grp else 0.0
            for r in rows:
                if r["kind"] == kind:
                    r["exp"] = m
        res = [r["fpor"] - r["exp"] for r in grp]
        sd = (sum(v * v for v in res) / len(res)) ** 0.5 if res else 1.0
        for r in rows:
            if r["kind"] == kind:
                r["z"] = max(-Z_CLIP, min(Z_CLIP, (r["fpor"] - r["exp"]) / sd)) if (r["games"] >= MIN_WEEKS and sd) else None
    meta = {"season": season, "completed": S.completed, "repl": S.repl, "a": a, "b": b, "k1": k1}
    return rows, meta


def faab_claims(conn, L, season, offers_doc):
    """Every winning waiver claim in a season with what it produced for the
    claiming team, plus losing offers from the FAB Offers page."""
    S = Season(conn, season, L.last_final_week(season))
    tsid_by_ytid = {t["yahoo_team_id"]: t["team_season_id"] for t in L.teams_in(season)}
    claims = []
    for tid, ts, bid in conn.execute("""
            SELECT transaction_id, timestamp, faab_bid FROM transactions
            WHERE season=? AND status='successful' AND event_type IN ('add','add/drop')
            ORDER BY timestamp DESC""", (season,)):
        leg = conn.execute("SELECT player_id, team_season_id, source_type FROM transaction_players "
                           "WHERE transaction_id=? AND direction='incoming'", (tid,)).fetchone()
        if not leg or leg[2] != "waivers":
            continue
        pid, tsid, _ = leg
        wk = week_of(season, ts)
        g, pts, f = S.fpor(pid, S.run_on_team(pid, tsid, wk))
        claims.append({"date": str(ts)[:10], "week": wk, "pid": pid, "player": L.players[pid]["player_name"],
                       "pos": S.pos_of.get(pid) or "", "tsid": tsid, "mgr": L.mgr(tsid), "bid": int(bid or 0),
                       "games": g, "pts": pts, "fpor": f, "losers": [], "over": None, "contested": False})
    by_pid = defaultdict(list)
    for c in claims:
        by_pid[(c["pid"], c["tsid"])].append(c)
    unmatched = 0
    for o in (offers_doc or {}).get("seasons", {}).get(str(season), []):
        wt = tsid_by_ytid.get(o["winner_tid"])
        cands = [c for c in by_pid.get((o["player_id"], wt), [])
                 if abs((date.fromisoformat(c["date"]) - date.fromisoformat(o["processed"])).days) <= 1 and not c["contested"]]
        if not cands:
            unmatched += 1
            continue
        c = cands[0]
        c["contested"] = True
        c["losers"] = [(L.mgr(tsid_by_ytid.get(l["tid"])), l["bid"], l["reason"]) for l in o["losing_offers"]]
        real = [l["bid"] for l in o["losing_offers"] if l["reason"] == "Lower Offer"]
        c["over"] = c["bid"] - max(real) if real else 0
    return claims, {"completed": S.completed, "unmatched": unmatched}
