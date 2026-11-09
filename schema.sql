-- We Graduated fantasy.db schema (forked from I Yearn 2026-11-08).
-- Dropped vs I Yearn: DRC tables, roster_seasons, synthetic transactions,
-- transaction_overrides, and the real+synthetic union views.
-- CHECK constraints on transaction types were removed on purpose: 17 seasons
-- of Yahoo data may carry values the 2023+ I Yearn data never showed.
-- verify_db.py lists the distinct values instead.

-- =========================================================================
-- DIMENSIONS
-- =========================================================================

CREATE TABLE seasons (
    season              INTEGER PRIMARY KEY,
    nfl_game_id         INTEGER NOT NULL,
    yahoo_league_id     TEXT    NOT NULL,
    league_key          TEXT    NOT NULL UNIQUE,
    league_name         TEXT,
    num_teams           INTEGER,
    -- filled by ingest_league.py from Yahoo metadata/settings
    start_week          INTEGER,
    end_week            INTEGER,
    playoff_start_week  INTEGER,
    num_playoff_teams   INTEGER,
    uses_faab           INTEGER,
    waiver_type         TEXT,
    trade_ratify_type   TEXT,
    draft_type          TEXT,
    is_finished         INTEGER
);

-- One row per real person across all seasons. canonical_name is the short
-- name the league uses (the commissioner sheets use first names: Andy, Aric,
-- Brian, Credit, Pete...). yahoo_guid is NULL when Yahoo hides it.
CREATE TABLE managers (
    manager_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_name      TEXT    NOT NULL UNIQUE,
    yahoo_guid          TEXT    UNIQUE,
    latest_nickname     TEXT,
    is_pete             INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE players (
    player_id           INTEGER PRIMARY KEY,
    player_name         TEXT    NOT NULL,
    position            TEXT,
    nfl_team            TEXT
);

CREATE TABLE teams (
    team_season_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    season              INTEGER NOT NULL,
    yahoo_team_id       INTEGER NOT NULL,
    team_name           TEXT    NOT NULL,
    manager_id          INTEGER NOT NULL,
    yahoo_nickname      TEXT,          -- raw, as Yahoo returned it that season
    yahoo_guid_raw      TEXT,          -- raw, may be '--hidden--' or blank
    is_commissioner     INTEGER,
    draft_position      INTEGER,
    FOREIGN KEY (season)     REFERENCES seasons(season),
    FOREIGN KEY (manager_id) REFERENCES managers(manager_id),
    UNIQUE (season, yahoo_team_id)
);

-- =========================================================================
-- TRANSACTIONS
-- =========================================================================

CREATE TABLE transactions (
    transaction_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    yahoo_transaction_id    INTEGER  NOT NULL,
    season                  INTEGER  NOT NULL,
    timestamp               DATETIME NOT NULL,
    event_type              TEXT     NOT NULL,   -- add, drop, add/drop, trade, commish
    status                  TEXT     NOT NULL,   -- successful, vetoed, ...
    faab_bid                INTEGER,             -- winning bid on waiver claims
    trader_team_season_id   INTEGER,
    tradee_team_season_id   INTEGER,
    FOREIGN KEY (season) REFERENCES seasons(season),
    UNIQUE (season, yahoo_transaction_id)
);

-- Drops = one 'outgoing' row. Adds = one 'incoming' row. Trades = one
-- 'incoming' row per player, counterparty in counterparty_team_season_id.
CREATE TABLE transaction_players (
    transaction_id              INTEGER NOT NULL,
    player_id                   INTEGER NOT NULL,
    direction                   TEXT    NOT NULL,
    team_season_id              INTEGER,
    source_type                 TEXT,
    destination_type            TEXT,
    counterparty_team_season_id INTEGER,
    PRIMARY KEY (transaction_id, player_id, direction),
    FOREIGN KEY (transaction_id)              REFERENCES transactions(transaction_id),
    FOREIGN KEY (player_id)                   REFERENCES players(player_id),
    FOREIGN KEY (team_season_id)              REFERENCES teams(team_season_id),
    FOREIGN KEY (counterparty_team_season_id) REFERENCES teams(team_season_id)
);

CREATE TABLE transaction_picks (
    transaction_id              INTEGER NOT NULL,
    draft_round                 INTEGER NOT NULL,
    source_team_season_id       INTEGER,
    destination_team_season_id  INTEGER,
    original_team_season_id     INTEGER,
    PRIMARY KEY (transaction_id, draft_round, source_team_season_id, original_team_season_id),
    FOREIGN KEY (transaction_id)             REFERENCES transactions(transaction_id),
    FOREIGN KEY (source_team_season_id)      REFERENCES teams(team_season_id),
    FOREIGN KEY (destination_team_season_id) REFERENCES teams(team_season_id),
    FOREIGN KEY (original_team_season_id)    REFERENCES teams(team_season_id)
);

CREATE INDEX idx_tp_player ON transaction_players(player_id);

-- =========================================================================
-- DRAFTS AND ROSTERS
-- =========================================================================

-- is_keeper is NULL until keeper logic is settled. Yahoo's draft results do
-- not reliably flag keepers; the commissioner's All Time Keepers sheet and
-- final_rosters.is_keeper_yahoo are the cross-checks.
CREATE TABLE draft_picks (
    season              INTEGER NOT NULL,
    overall_pick        INTEGER NOT NULL,
    draft_round         INTEGER NOT NULL,
    pick_in_round       INTEGER NOT NULL,
    team_season_id      INTEGER,
    player_id           INTEGER,
    cost_yahoo          INTEGER,
    is_keeper           INTEGER,
    PRIMARY KEY (season, overall_pick),
    FOREIGN KEY (season)         REFERENCES seasons(season),
    FOREIGN KEY (team_season_id) REFERENCES teams(team_season_id),
    FOREIGN KEY (player_id)      REFERENCES players(player_id)
);

-- Snapshot of every roster at the season's last scoring week.
CREATE TABLE final_rosters (
    season              INTEGER NOT NULL,
    team_season_id      INTEGER NOT NULL,
    player_id           INTEGER NOT NULL,
    week                INTEGER NOT NULL,
    selected_position   TEXT,
    is_keeper_yahoo     INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (season, team_season_id, player_id),
    FOREIGN KEY (season)         REFERENCES seasons(season),
    FOREIGN KEY (team_season_id) REFERENCES teams(team_season_id),
    FOREIGN KEY (player_id)      REFERENCES players(player_id)
);

-- =========================================================================
-- RESULTS AND PERFORMANCE
-- =========================================================================

-- Points for every rostered player, every week, under league scoring.
-- selected_position tells you whether he started (anything but BN/IR).
CREATE TABLE player_weekly_stats (
    season              INTEGER NOT NULL,
    week                INTEGER NOT NULL,
    player_id           INTEGER NOT NULL,
    team_season_id      INTEGER,
    selected_position   TEXT,
    fantasy_points      REAL,
    fetched_at          DATETIME NOT NULL,
    PRIMARY KEY (season, week, player_id),
    FOREIGN KEY (player_id)      REFERENCES players(player_id),
    FOREIGN KEY (team_season_id) REFERENCES teams(team_season_id)
);
CREATE INDEX idx_pws_player_season ON player_weekly_stats(player_id, season);
CREATE INDEX idx_pws_team_week     ON player_weekly_stats(team_season_id, week);

CREATE TABLE team_standings (
    season          INTEGER NOT NULL,
    team_season_id  INTEGER NOT NULL,
    rank            INTEGER,
    playoff_seed    INTEGER,
    wins            INTEGER,
    losses          INTEGER,
    ties            INTEGER,
    points_for      REAL,
    points_against  REAL,
    fetched_at      DATETIME NOT NULL,
    PRIMARY KEY (season, team_season_id),
    FOREIGN KEY (season)         REFERENCES seasons(season),
    FOREIGN KEY (team_season_id) REFERENCES teams(team_season_id)
);

CREATE TABLE matchups (
    season                  INTEGER NOT NULL,
    week                    INTEGER NOT NULL,
    team_season_id          INTEGER NOT NULL,
    points                  REAL,
    projected_points        REAL,
    opponent_team_season_id INTEGER,
    opponent_points         REAL,
    is_playoffs             INTEGER NOT NULL DEFAULT 0,
    is_consolation          INTEGER NOT NULL DEFAULT 0,
    is_tied                 INTEGER,
    is_winner               INTEGER,
    status                  TEXT,
    fetched_at              DATETIME NOT NULL,
    PRIMARY KEY (season, week, team_season_id),
    FOREIGN KEY (season)                  REFERENCES seasons(season),
    FOREIGN KEY (team_season_id)          REFERENCES teams(team_season_id),
    FOREIGN KEY (opponent_team_season_id) REFERENCES teams(team_season_id)
);

CREATE TABLE team_season_stats (
    season           INTEGER NOT NULL,
    team_season_id   INTEGER NOT NULL,
    number_of_moves  INTEGER,
    number_of_trades INTEGER,
    faab_balance     INTEGER,
    fetched_at       DATETIME NOT NULL,
    PRIMARY KEY (season, team_season_id),
    FOREIGN KEY (season)         REFERENCES seasons(season),
    FOREIGN KEY (team_season_id) REFERENCES teams(team_season_id)
);

-- =========================================================================
-- CONVENIENCE VIEW
-- =========================================================================

CREATE VIEW v_team_seasons AS
    SELECT t.team_season_id, t.season, t.yahoo_team_id, t.team_name,
           m.manager_id, m.canonical_name AS manager, m.is_pete
    FROM teams t JOIN managers m ON m.manager_id = t.manager_id;
