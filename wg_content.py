"""
wg_content.py - the hand-written parts of the site: league rules, the open
questions, rules history and summits, and Mike's Substack index.

Sources (background only, never loaded as data): Mike's League Doc (Rules,
Topics, Discussion Topics 2020/2021, 2020 votes, List of League Summits),
2024 Summit Topic Votes.xlsx, and the Substack posts "2023 Summit Results"
and "Rules Summit Results". Names use the league's first names.
Edit this file to change rules text; rerun generate_site.py.
"""

SUBSTACK = "https://michaelcredit.substack.com"

# (slug, title) newest first, from the Substack archive as of 2026-11-09.
SUBSTACK_POSTS = [
    ("weekly-news", "Weekly News: trades, waivers and power rankings"),
    ("week-2-review", "Week 2 Review"),
    ("week-1-review", "Week 1 Review"),
    ("we-graduated-18-years-old", "We Graduated: 18 Years Old"),
    ("semifinal-preview-530", "2025 Semifinal Preview"),
    ("round-1-preview-f5a", "2025 Round 1 Preview (with playoff history)"),
    ("thanksgiving-and-matchup-of-the-week", "Thanksgiving and Matchup of the Week"),
    ("rules-summit-results", "Rules Summit Results (2025)"),
    ("week-5-preview-ecc", "2025 Week 5 Preview"),
    ("week-2-preview-dd9", "2025 Week 2 Preview"),
    ("2025-season-preview", "2025 Season Preview"),
    ("quick-2025-keeper-thoughts", "Quick 2025 Keeper Thoughts"),
    ("semifinal-preview", "2024 Semifinal Preview"),
    ("round-1-preview-592", "2024 Round 1 Preview"),
    ("week-14-preview-and-playoff-scenarios", "2024 Week 14 Preview and Playoff Scenarios"),
    ("first-trimester-awards", "2024 First Trimester Awards"),
    ("week-5-preview-ed1", "2024 Week 5 Preview"),
    ("week-3-preview-72f", "2024 Week 3 Preview"),
    ("2024-season-preview", "2024 Season Preview"),
    ("quick-keeper-notes", "Quick Keeper Notes (2024)"),
    ("championship-preview", "2023 Championship Preview"),
    ("round-2-preview", "2023 Round 2 Preview"),
    ("round-1-preview", "2023 Round 1 Preview"),
    ("week-13-preview", "2023 Week 13 Preview"),
    ("week-12-preview", "2023 Week 12 Preview"),
    ("week-10-preview", "2023 Week 10 Preview"),
    ("pre-season-predictions-and-week-8", "2023 Preseason Predictions and Week 8"),
    ("week-7-review", "2023 Week 7 Review"),
    ("week-7", "2023 Week 7"),
    ("week-6-preview", "2023 Week 6 Preview"),
    ("week-5-preview", "2023 Week 5 Preview"),
    ("2023-summit-results", "2023 Summit Results"),
    ("week-4-review", "2023 Week 4 Review"),
    ("week-4-preview", "2023 Week 4 Preview"),
    ("week-3-review", "2023 Week 3 Review"),
    ("week-3-preview", "2023 Week 3 Preview"),
    ("week-2-preview", "2023 Week 2 Preview"),
    ("week-1-preview", "2023 Week 1 Preview"),
    ("2023-draft-review", "2023 Draft Review"),
]

# --------------------------------------------------------------------- rules
# (heading, [paragraphs or ("table", headers, rows)])
RULES = [
    ("League basics", [
        "Twelve teams, keeper league, on Yahoo since 2010 (the league itself dates to 2006).",
        "Buy-in is $50 per team, paid before the draft. The pot pays the champion 80% and the runner-up 20%. "
        "Teams may opt out, but once in they stay in. An opted-out team cannot be paid; if one finishes in the money, "
        "the next team down takes that prize. (Adopted at the 2024 summit, 6 to 4.)",
    ]),
    ("Roster", [
        ("table", ["Slot", "Count"], [["QB", "1"], ["WR", "3"], ["RB", "2"], ["TE", "1"], ["K", "1"], ["DEF", "1"],
                                      ["Bench", "6"], ["IR", "1"]]),
        "No flex. In 2020 only, the league added a seventh bench spot for COVID, which is why the 2020 draft ran 16 rounds.",
        "You must start an active player in every slot, every week, including after you are eliminated. "
        "A player on bye or injured does not count as active. See the open question on the penalty amount below. "
        "If the team that would be fined wins that matchup, the fine is waived.",
    ]),
    ("Keepers", [
        "Each team may keep up to 6 players. Keepers can be any players on your roster at the end of the prior season, "
        "or players you traded for in the off-season.",
        "Keepers fill your last 6 draft slots, normally Rounds 10 to 15. Keeper slots are tradeable, so a team can hold "
        "more or fewer than 6 in a given year.",
        "Keepers are declared in Yahoo by the keeper deadline, usually a week before the draft. A pre-keeper trade "
        "deadline falls about 24 hours earlier. After the keeper deadline, anyone not kept goes back into the draft pool "
        "and cannot be traded.",
    ]),
    ("Draft", [
        "Draft order for Rounds 1 and 2 comes from a lottery among the six non-playoff teams. Current odds of the #1 pick:",
        ("table", ["Finish", "Odds of #1 pick"], [["12th", "25%"], ["11th", "25%"], ["10th", "15%"], ["9th", "15%"],
                                                  ["8th", "10%"], ["7th", "10%"]]),
        "Starting with the 2027 draft, all six non-playoff teams get equal odds (16.667%). Adopted at the 2025 summit.",
        "Playoff teams pick by the round they were eliminated, with regular-season standing as the tiebreaker. "
        "Rounds 3 to 15: lottery teams pick in reverse regular-season order; playoff teams keep their Round 1 order.",
        "Each pick has a 60-second clock.",
    ]),
    ("Trades", [
        "Trades process immediately; there is no review period.",
        "Trades may include any rostered player and any draft pick a team controls, with no limit on how far ahead. "
        "Conditions may be attached to picks (for example, a 1st becomes a 2nd if the player misses a set number of games).",
        "Picks already tied up in a conditional trade can be traded again, but only with an agreed backup pick in case "
        "the condition goes the other way. Deals cannot be renegotiated later.",
        "No player-to-be-named-later. Only picks and FAAB can move as part of a condition.",
        "Trade back rule: if you trade a player away, you cannot reacquire him by trade for the rest of that season and "
        "the following season (seasons end at the Championship). He can be reacquired sooner if he passes through "
        "waivers or the draft.",
        "Trade moratorium: from 10pm on the Wednesday after Thanksgiving until the Championship ends. "
        "(Moved one week later at the 2023 summit, effective 2024.)",
    ]),
    ("Waivers", [
        "FAAB waivers with 2-day claims. The waiver tiebreaker is a weekly rolling list: the last-place team gets top "
        "priority only on the first claim of the week (2020 summit). Players can be added straight to IR (2020 summit).",
    ]),
    ("Schedule and playoffs", [
        "14-week regular season since 2021 (13 weeks before that).",
        "Six teams make the playoffs. The top two seeds get a Round 1 bye. The bracket is reseeded before the "
        "semifinals. Round 1 is Week 15.",
    ]),
    ("Scoring", [
        "Non-PPR. Passing: 1 point per 25 yards, 6 per TD, -2 per INT. Rushing and receiving: 1 point per 10 yards, "
        "6 per TD. Two-point conversions 2. Every fumble is -2, even if recovered by the offense.",
        "Kickers score by distance since 2022: 0.1 point per yard of a made field goal, 1 per extra point made, -1 per "
        "extra point missed. Missed field goals: see the open question below.",
        "Defense: sack 1, interception 2, fumble recovery 1, TD 6, safety 2, blocked kick 3, 4th-down stop 1, "
        "tackle for loss 0.5, three-and-out forced 0.5, plus points-allowed and yards-allowed tiers.",
    ]),
    ("Summits", [
        "To put a topic on the summit agenda, five managers must agree to discuss it. Agreeing to discuss is not "
        "agreeing to the change.",
    ]),
]

# (question, [(version label, text, source)])
OPEN_QUESTIONS = [
    ("How big is the fine for not starting a full lineup?", [
        ("Version A", "The fine climbs 15, 30, 45, 60 FAAB and keeps going, per empty slot. If you run out of FAAB, "
                      "it rolls into future years.", "League Doc, Rules tab"),
        ("Version B", "Per empty slot, 15, 30, 45, then 45 for each one after that.", "League Doc, 2023 summit topics"),
        ("Version C", "Per empty slot, rising 15 per violation, capped at 45.", "Substack, \"2023 Summit Results\""),
    ]),
    ("Do missed field goals from 40 to 49 yards cost a point, and since when?", [
        ("Version A", "Misses from 0 to 39 yards are -1. Misses of 40+ cost nothing.",
         "Yahoo league settings, 2026 season (this is what actually scored)"),
        ("Version B", "All misses under 50 yards are -1.", "League Doc, Rules tab (kicker scoring from 2022)"),
        ("Version C", "Passed: add -1 for misses from 40 to 49 yards. No start season recorded.",
         "2025 summit (League Doc topics and Substack \"Rules Summit Results\")"),
    ]),
]

# Rules history: (year, title, [(item, outcome)])
HISTORY = [
    (2026, "Proposals on the table for the next summit", [
        ("A proposal's sponsor must be at the draft for it to come to a vote (Chris)", "Pending"),
        ("What happens to the schedule if the NFL adds an 18th game? (Chris)", "Pending"),
        ("Play against the league median each week (Mike)", "Pending; needs Yahoo Commissioner+"),
        ("Play a second opponent each week (Mike)", "Pending; needs Yahoo Commissioner+"),
        ("Seven-team playoff (Mike)", "Pending; needs Yahoo Commissioner+"),
        ("Bigger or different penalty for inactive starters, such as losing picks (Ryan)", "Pending"),
        ("Add punters (Ryan)", "Pending"),
        ("Lottery order set by worst optimal lineup (Mike)", "Pending"),
        ("Full-lineup exemption for teams that clinched a playoff spot or bye (Ryan)", "Pending"),
        ("Proposals cost $50, plus $25 more if the rule fails (Pete)", "Pending"),
    ]),
    (2025, "Houston summit", [
        ("-1 for missed field goals from 40 to 49 yards (Andy)", "Passed; start season not recorded"),
        ("Equal lottery odds for all six non-playoff teams (Mike)", "Passed; starts with the 2027 draft"),
        ("Half-point PPR (Pete)", "Not adopted"),
        ("Add 3 keepers to reduce tanking (Andy)", "Not adopted"),
        ("Format changes: WR3 to flex, add a flex, more or fewer keepers, add teams, redraft (Mike)",
         "Tabled for future summits"),
    ]),
    (2024, "Charleston summit", [
        ("League dues of $50, paid 80/20 to champion and runner-up, with opt-out", "Passed, 6 to 4"),
        ("Get rid of kickers and/or defenses", "Failed, 3 to 9"),
        ("Punishment for last place", "Failed, 4 to 6"),
        ("Eliminate or shorten the trade back rule", "Split vote, 3 to 2; rule still in place"),
        ("Eliminate the full-lineup FAAB penalty", "Split vote, 1 to 1; rule still in place"),
        ("2025 summit location", "Houston"),
    ]),
    (2023, "Denver summit", [
        ("Move the trade deadline one week later", "Passed by voice vote; effective 2024"),
        ("Full-lineup fine charged per empty slot, rising each time", "Passed; see open question on the amount"),
        ("Summit competition for better draft odds", "Failed"),
        ("Charge eliminated teams' fines against next year's FAAB", "Failed"),
        ("Waiver period from 2 days to 1", "Failed"),
        ("Move the league to Sleeper", "Failed"),
    ]),
    (2022, "Mystic summit", [
        ("Kickers score by field goal distance (proposed 2021 by Mike)", "In effect from 2022"),
    ]),
    (2021, "Chicago summit", [
        ("Regular season set at 14 weeks", "In effect from 2021"),
        ("Draft pick clock of 60 seconds", "Adopted"),
        ("Add 1 or 2 keeper slots, to 7 or 8 (John)", "Voted down before the summit"),
        ("Add 1 or 2 bench spots (John)", "Not adopted"),
        ("Remove lottery odds for Round 2 (Chris)", "Not adopted"),
    ]),
    (2020, "Rules discussion (virtual)", [
        ("Starters must be active players (no byes, no injured players)", "Passed"),
        ("Waiver tiebreaker: last place gets top priority only on the first claim of the week", "Passed"),
        ("Allow adding players directly to IR", "Passed"),
        ("Extra lottery incentive for the 5th and 6th seeds who lose in Round 1", "Passed"),
        ("Add 1 bench spot for the 2020 season (COVID)", "Passed; 2020 only"),
        ("Cut 4th-down stops for defenses to 0.5 points", "Failed; stays at 1"),
        ("Add a flex spot (John)", "Failed"),
        ("Trade moratorium for new managers", "Failed"),
        ("Let the commissioner change a lineup if texted before kickoff", "Failed"),
        ("Lock eliminated teams' lineups (Pete)", "Withdrawn"),
    ]),
]

# (year, location, hosts, attendance out of 12)
SUMMITS = [
    (2025, "Houston", "Jeff, Howard", 7),
    (2024, "Charleston", "Pete", 6),
    (2023, "Denver", "Ryan", 8),
    (2022, "Mystic, CT", "Will", 9),
    (2021, "Chicago", "Joel", 8),
    (2017, "Westminster, MD", "Mike", 7),
    (2016, "Houston", "Jeff, Howard, Joel", 9),
]
