"""
wg_data.py - every number the We Graduated site shows, computed from
fantasy.db. Read-only: opens the database with mode=ro.

Conventions
- "Regular season" = weeks before seasons.playoff_start_week.
- A game counts once it is final (matchups.status = 'postevent').
- Championship bracket: Yahoo flags consolation AND placement games as
  playoffs, so playoff records follow the bracket. A team is "alive" from
  its seed until its first loss; only games between two live teams count.
- Season player points = a player's points in weeks he was rostered by
  anyone in the league (we do not hold unrostered weeks yet).
"""

import sqlite3
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
DB = HERE / "fantasy.db"


def connect():
    c = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    return c


def slug(name):
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")


class League:
    def __init__(self, conn):
        self.c = conn
        q = lambda s, *a: conn.execute(s, a).fetchall()
        self.seasons = {r["season"]: dict(r) for r in q(
            "SELECT * FROM seasons WHERE season IN (SELECT DISTINCT season FROM teams) ORDER BY season")}
        self.years = sorted(self.seasons)
        self.current = max(self.years)
        self.finished = [y for y in self.years if self.seasons[y]["is_finished"]]
        self.teams = {r["team_season_id"]: dict(r) for r in q("SELECT * FROM v_team_seasons")}
        self.managers = sorted({t["manager"] for t in self.teams.values()})
        self.standings = {r["team_season_id"]: dict(r) for r in q("SELECT * FROM team_standings")}
        self.players = {r["player_id"]: dict(r) for r in q("SELECT * FROM players")}
        self.matchups = [dict(r) for r in q("SELECT * FROM matchups ORDER BY season, week")]
        self.stats = self.team_season_stats = {r["team_season_id"]: dict(r) for r in q("SELECT * FROM team_season_stats")}
        self._bracket = None

    # ---------------------------------------------------------------- basics
    def team(self, tsid):
        return self.teams.get(tsid, {})

    def mgr(self, tsid):
        return self.team(tsid).get("manager", "?")

    def teams_in(self, season):
        return [t for t in self.teams.values() if t["season"] == season]

    def reg_weeks(self, season):
        return self.seasons[season]["playoff_start_week"] - 1

    def final_games(self, season=None, regular=None):
        for m in self.matchups:
            if m["status"] != "postevent" or (season and m["season"] != season):
                continue
            is_reg = m["week"] <= self.reg_weeks(m["season"])
            if regular is True and not is_reg:
                continue
            if regular is False and is_reg:
                continue
            yield m

    def last_final_week(self, season):
        weeks = [m["week"] for m in self.final_games(season)]
        return max(weeks) if weeks else 0

    # -------------------------------------------------------------- standings
    def season_table(self, season):
        rows = []
        for t in self.teams_in(season):
            s = self.standings.get(t["team_season_id"], {})
            rows.append({**t, **{k: s.get(k) for k in ("rank", "playoff_seed", "wins", "losses", "ties",
                                                       "points_for", "points_against")}})
        return sorted(rows, key=lambda r: (r["rank"] or 99))

    def regular_season_records(self):
        """(season, tsid) -> dict(w, l, t, pf, pa, games) from final regular-season games."""
        out = defaultdict(lambda: {"w": 0, "l": 0, "t": 0, "pf": 0.0, "pa": 0.0, "g": 0})
        for m in self.final_games(regular=True):
            r = out[(m["season"], m["team_season_id"])]
            r["g"] += 1
            r["pf"] += m["points"] or 0
            r["pa"] += m["opponent_points"] or 0
            if m["is_tied"]:
                r["t"] += 1
            elif m["is_winner"]:
                r["w"] += 1
            else:
                r["l"] += 1
        return out

    def alltime(self):
        recs = self.regular_season_records()
        agg = defaultdict(lambda: {"seasons": 0, "w": 0, "l": 0, "t": 0, "pf": 0.0, "pa": 0.0, "g": 0,
                                   "titles": 0, "finals": 0, "playoffs": 0, "best": None, "byes": 0})
        for (season, tsid), r in recs.items():
            a = agg[self.mgr(tsid)]
            for k in ("w", "l", "t", "pf", "pa", "g"):
                a[k] += r[k]
        for y in self.years:
            for t in self.teams_in(y):
                a = agg[t["manager"]]
                a["seasons"] += 1
                s = self.standings.get(t["team_season_id"], {})
                if y in self.finished:
                    rk = s.get("rank")
                    if rk == 1:
                        a["titles"] += 1
                    if rk in (1, 2):
                        a["finals"] += 1
                    if (s.get("playoff_seed") or 99) <= self.seasons[y]["num_playoff_teams"]:
                        a["playoffs"] += 1
                    if (s.get("playoff_seed") or 99) <= 2:
                        a["byes"] += 1
                    if rk and (a["best"] is None or rk < a["best"]):
                        a["best"] = rk
        return agg

    # ---------------------------------------------------------------- awards
    def season_awards(self, season):
        rows = self.season_table(season)
        by_rank = {r["rank"]: r for r in rows}
        seed1 = next((r for r in rows if r["playoff_seed"] == 1), None)
        most = max(rows, key=lambda r: r["points_for"] or 0)
        return {"champion": by_rank.get(1), "runner_up": by_rank.get(2), "reg_champ": seed1, "most_points": most}

    def champion_roster(self, season):
        champ = self.season_awards(season)["champion"]
        if not champ:
            return []
        rows = self.c.execute(
            """SELECT p.player_name, p.position, SUM(s.fantasy_points) pts
               FROM player_weekly_stats s JOIN players p USING(player_id)
               WHERE s.season=? AND s.team_season_id=? AND s.selected_position NOT IN ('BN','IR')
               GROUP BY s.player_id ORDER BY pts DESC LIMIT 12""",
            (season, champ["team_season_id"])).fetchall()
        return [dict(r) for r in rows]

    # --------------------------------------------------------------- records
    def single_week_scores(self):
        return [m for m in self.final_games() if m["points"] is not None]

    def high_low(self, n=10):
        games = self.single_week_scores()
        reg = [m for m in games if m["week"] <= self.reg_weeks(m["season"])]
        high = sorted(reg, key=lambda m: -m["points"])[:n]
        low = sorted(reg, key=lambda m: m["points"])[:n]
        uniq = {}
        for m in reg:
            key = (m["season"], m["week"], min(m["team_season_id"], m["opponent_team_season_id"] or 0))
            uniq[key] = m
        blow = sorted(uniq.values(), key=lambda m: -abs(m["points"] - (m["opponent_points"] or 0)))[:n]
        close = sorted([m for m in uniq.values() if m["points"] != m["opponent_points"]],
                       key=lambda m: abs(m["points"] - (m["opponent_points"] or 0)))[:n]
        return high, low, blow, close

    # --------------------------------------------------------------- playoffs
    def bracket_games(self):
        """List of championship-bracket games: dict(season, week, round, winner, loser, wpts, lpts)."""
        if self._bracket is not None:
            return self._bracket
        out = []
        for y in self.finished:
            n = self.seasons[y]["num_playoff_teams"]
            ps = self.seasons[y]["playoff_start_week"]
            alive = {t["team_season_id"] for t in self.teams_in(y)
                     if (self.standings.get(t["team_season_id"], {}).get("playoff_seed") or 99) <= n}
            rnd = 0
            for wk in range(ps, self.seasons[y]["end_week"] + 1):
                rnd += 1
                seen = set()
                for m in self.final_games(y):
                    if m["week"] != wk or not m["is_playoffs"] or m["is_consolation"]:
                        continue
                    a, b = m["team_season_id"], m["opponent_team_season_id"]
                    if a not in alive or b not in alive or (b, a) in seen:
                        continue
                    seen.add((a, b))
                    win = a if m["is_winner"] else b
                    lose = b if win == a else a
                    wp = m["points"] if win == a else m["opponent_points"]
                    lp = m["opponent_points"] if win == a else m["points"]
                    out.append({"season": y, "week": wk, "round": rnd, "winner": win, "loser": lose,
                                "wpts": wp, "lpts": lp})
                alive -= {g["loser"] for g in out if g["season"] == y and g["week"] == wk}
        for g in out:
            rounds = max(x["round"] for x in out if x["season"] == g["season"])
            g["round_name"] = {rounds: "Final", rounds - 1: "Semifinal"}.get(g["round"], "Round 1")
        self._bracket = out
        return out

    def playoff_records(self):
        rec = defaultdict(lambda: {"w": 0, "l": 0})
        for g in self.bracket_games():
            rec[self.mgr(g["winner"])]["w"] += 1
            rec[self.mgr(g["loser"])]["l"] += 1
        return rec

    def bye_outcomes(self):
        out = []
        for y in self.finished:
            for t in self.season_table(y):
                if (t["playoff_seed"] or 99) <= 2:
                    rk = t["rank"]
                    res = "Won title" if rk == 1 else "Lost final" if rk == 2 else "Lost semifinal"
                    out.append((y, t["playoff_seed"], t["manager"], res))
        return out

    # ------------------------------------------------------------------ luck
    def luck(self):
        """(season, tsid) -> actual wins, all-play expected wins, games."""
        weekly = defaultdict(list)
        for m in self.final_games(regular=True):
            weekly[(m["season"], m["week"])].append(m)
        out = defaultdict(lambda: {"w": 0.0, "xw": 0.0, "g": 0})
        for (season, wk), games in weekly.items():
            scores = [g["points"] for g in games]
            n = len(scores) - 1
            for g in games:
                r = out[(season, g["team_season_id"])]
                beat = sum(1 for s in scores if s < g["points"]) + 0.5 * (sum(1 for s in scores if s == g["points"]) - 1)
                r["xw"] += beat / n if n else 0
                r["w"] += 1 if g["is_winner"] and not g["is_tied"] else (0.5 if g["is_tied"] else 0)
                r["g"] += 1
        return out

    def over_under(self):
        out = defaultdict(lambda: {"pts": 0.0, "proj": 0.0, "g": 0})
        for m in self.final_games(regular=True):
            if m["projected_points"] is None:
                continue
            r = out[(m["season"], m["team_season_id"])]
            r["pts"] += m["points"] or 0
            r["proj"] += m["projected_points"]
            r["g"] += 1
        return out

    def positional(self, season):
        rows = self.c.execute(
            """SELECT s.team_season_id, s.selected_position pos, SUM(s.fantasy_points) pts
               FROM player_weekly_stats s
               WHERE s.season=? AND s.selected_position NOT IN ('BN','IR')
                 AND s.week < (SELECT playoff_start_week FROM seasons WHERE season=?)
               GROUP BY s.team_season_id, s.selected_position""", (season, season)).fetchall()
        out = defaultdict(dict)
        for r in rows:
            out[r["team_season_id"]][r["pos"]] = r["pts"] or 0.0
        return out

    # ----------------------------------------------------------- draft/keeper
    def season_player_points(self):
        rows = self.c.execute("SELECT season, player_id, SUM(fantasy_points) pts FROM player_weekly_stats "
                              "GROUP BY season, player_id").fetchall()
        return {(r["season"], r["player_id"]): r["pts"] or 0.0 for r in rows}

    def draft(self, season):
        rows = self.c.execute(
            """SELECT d.*, p.player_name, p.position FROM draft_picks d JOIN players p USING(player_id)
               WHERE d.season=? ORDER BY d.overall_pick""", (season,)).fetchall()
        return [dict(r) for r in rows]

    def keeper_streaks(self):
        """Consecutive seasons a manager kept the same player. Returns list of
        dict(player, manager, start, end, years, active)."""
        rows = self.c.execute(
            """SELECT d.season, d.player_id, v.manager FROM draft_picks d
               JOIN v_team_seasons v USING(team_season_id) WHERE d.is_keeper=1 ORDER BY d.season""").fetchall()
        kept = defaultdict(set)
        for r in rows:
            kept[(r["player_id"], r["manager"])].add(r["season"])
        out = []
        for (pid, mgr), yrs in kept.items():
            yrs = sorted(yrs)
            start = prev = yrs[0]
            for y in yrs[1:] + [None]:
                if y is not None and y == prev + 1:
                    prev = y
                    continue
                out.append({"player": self.players[pid]["player_name"], "pos": self.players[pid]["position"],
                            "manager": mgr, "start": start, "end": prev, "years": prev - start + 1,
                            "active": prev == self.current})
                if y is not None:
                    start = prev = y
        return sorted(out, key=lambda s: (-s["years"], -s["end"], s["player"]))

    def repeat_keeper_rate(self):
        rows = self.c.execute(
            """SELECT d.season, d.player_id, v.manager FROM draft_picks d
               JOIN v_team_seasons v USING(team_season_id) WHERE d.is_keeper=1""").fetchall()
        by = defaultdict(set)
        for r in rows:
            by[r["season"]].add((r["player_id"], r["manager"]))
        return [(y, len(by[y] & by[y - 1]), len(by[y])) for y in self.years if y - 1 in by]

    # ----------------------------------------------------------- transactions
    def trades(self):
        txns = self.c.execute(
            "SELECT * FROM transactions WHERE event_type='trade' ORDER BY timestamp DESC").fetchall()
        out = []
        for t in txns:
            sides = defaultdict(lambda: {"players": [], "picks": []})
            for p in self.c.execute(
                    """SELECT tp.*, pl.player_name, pl.position FROM transaction_players tp
                       JOIN players pl USING(player_id) WHERE transaction_id=?""", (t["transaction_id"],)):
                sides[p["team_season_id"]]["players"].append(f'{p["player_name"]} ({p["position"]})')
            for k in self.c.execute("SELECT * FROM transaction_picks WHERE transaction_id=?", (t["transaction_id"],)):
                orig = self.mgr(k["original_team_season_id"])
                sides[k["destination_team_season_id"]]["picks"].append(f'Rd {k["draft_round"]} pick ({orig}\'s)')
            for tsid in (t["trader_team_season_id"], t["tradee_team_season_id"]):
                if tsid:
                    sides[tsid]
            out.append({"season": t["season"], "date": t["timestamp"][:10], "status": t["status"],
                        "sides": {self.mgr(k): v for k, v in sides.items() if k}})
        return out

    def faab_bids(self):
        rows = self.c.execute(
            """SELECT t.season, t.timestamp, t.faab_bid, tp.team_season_id, p.player_name, p.position
               FROM transactions t JOIN transaction_players tp USING(transaction_id) JOIN players p USING(player_id)
               WHERE t.faab_bid IS NOT NULL AND t.faab_bid > 0 AND tp.direction='incoming'
                 AND t.status='successful' ORDER BY t.timestamp""").fetchall()
        return [dict(r) for r in rows]

    def transactions_for(self, season):
        rows = self.c.execute(
            """SELECT t.transaction_id, t.timestamp, t.event_type, t.status, t.faab_bid,
                      tp.direction, tp.team_season_id, tp.source_type, tp.destination_type,
                      tp.counterparty_team_season_id, p.player_name, p.position
               FROM transactions t JOIN transaction_players tp USING(transaction_id) JOIN players p USING(player_id)
               WHERE t.season=? ORDER BY t.timestamp DESC, tp.direction DESC""", (season,)).fetchall()
        return [dict(r) for r in rows]

    # ----------------------------------------------------------------- teams
    def current_roster(self, tsid):
        wk = self.c.execute("SELECT MAX(week) FROM player_weekly_stats WHERE team_season_id=?", (tsid,)).fetchone()[0]
        rows = self.c.execute(
            """SELECT s.player_id, p.player_name, p.position, p.nfl_team, s.selected_position, s.fantasy_points,
                      (SELECT SUM(fantasy_points) FROM player_weekly_stats x WHERE x.player_id=s.player_id
                         AND x.season=s.season AND x.team_season_id=s.team_season_id) season_pts
               FROM player_weekly_stats s JOIN players p USING(player_id)
               WHERE s.team_season_id=? AND s.week=?""", (tsid, wk)).fetchall()
        order = {"QB": 0, "WR": 1, "RB": 2, "TE": 3, "K": 4, "DEF": 5, "BN": 6, "IR": 7}
        return wk, sorted([dict(r) for r in rows], key=lambda r: (order.get(r["selected_position"], 9), -(r["season_pts"] or 0)))

    def player_index(self):
        """Every player with every season he was rostered: manager(s), points, how acquired."""
        pts = defaultdict(float)
        owners = defaultdict(set)
        for r in self.c.execute("""SELECT s.season, s.player_id, v.manager, SUM(s.fantasy_points) p
                                   FROM player_weekly_stats s JOIN v_team_seasons v USING(team_season_id)
                                   GROUP BY s.season, s.player_id, v.manager"""):
            pts[(r["player_id"], r["season"])] += r["p"] or 0
            owners[(r["player_id"], r["season"])].add(r["manager"])
        drafted = {}
        for r in self.c.execute("""SELECT d.season, d.player_id, d.draft_round, d.is_keeper, v.manager
                                   FROM draft_picks d JOIN v_team_seasons v USING(team_season_id)"""):
            drafted[(r["player_id"], r["season"])] = (r["manager"], "Kept" if r["is_keeper"] else f"Rd {r['draft_round']}")
        out = {}
        for (pid, season) in set(pts) | set(drafted):
            p = self.players.get(pid)
            if not p:
                continue
            e = out.setdefault(pid, {"n": p["player_name"], "p": p["position"], "s": []})
            d = drafted.get((pid, season))
            e["s"].append({"y": season, "m": ", ".join(sorted(owners.get((pid, season), set()) or ({d[0]} if d else set()))),
                           "pts": round(pts.get((pid, season), 0), 1), "how": d[1] if d else ""})
        for e in out.values():
            e["s"].sort(key=lambda s: -s["y"])
            e["t"] = round(sum(s["pts"] for s in e["s"]), 1)
        return sorted(out.values(), key=lambda e: -e["t"])
