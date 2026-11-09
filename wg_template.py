"""wg_template.py - page shell copied from the I Yearn site (CSS, core navigation JS,
feedback modal) on 2026-11-09, recolored to the We Graduated logo blues.
Independent copy: changes here do not affect I Yearn."""

CSS = r"""
:root {
  --blue-800: #0D3A66;
  --blue-600: #1761A0;
  --blue-400: #3B82C4;
  --blue-200: #81BEF6;
  --gold-400: #E1B523;
  --gray-700: #2a2a2e;
  --gray-600: #606C71;
  --gray-500: #8e8e93;
  --gray-200: #ebebed;
  --gray-100: #f5f5f5;
  --gray-50:  #fcfcfd;
  --off-white: #fafafb;
  color-scheme: light;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Inter", "Helvetica Neue", Arial, sans-serif;
  background: #fff;
  color: #000;
  font-size: 14.5px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

.layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  min-height: 100vh;
}

/* --- Sidebar ----------------------------------------------------------- */
.sidebar {
  background: var(--blue-800);
  color: #fff;
  padding: 32px 24px 40px;
  position: sticky;
  top: 0;
  align-self: start;
  height: 100vh;
  overflow-y: auto;
  /* Keep touch scrolling contained to the sidebar — without this, when the
     sidebar hits its top/bottom, the scroll gesture "chains" to the
     underlying page and the sidebar feels stuck. */
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
}
/* Subtle draft-slot indicator prepended to each team name in the sidebar
   Teams list. Small, muted, tabular; a hint, not a competing element. */
.sidebar .draft-slot {
  display: inline-block;
  min-width: 18px;
  margin-right: 8px;
  color: rgba(255, 255, 255, 0.42);
  font-size: 11px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.04em;
  text-align: right;
}
.sidebar .brand {
  font-size: 11px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--blue-200);
  font-weight: 600;
  margin-bottom: 6px;
}
.sidebar .brand-title {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.01em;
  line-height: 1.25;
  margin-bottom: 4px;
  color: #fff;
}
.sidebar .brand-sub {
  font-size: 11.5px;
  color: var(--blue-200);
  margin-bottom: 36px;
}
.sidebar h3 {
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--blue-200);
  margin: 24px 0 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}
.nav-link {
  display: block;
  padding: 9px 10px;
  color: rgba(255, 255, 255, 0.82);
  text-decoration: none;
  font-size: 13.5px;
  border-radius: 4px;
  margin-bottom: 1px;
  cursor: pointer;
}
.nav-link:hover { background: rgba(255, 255, 255, 0.08); color: #fff; }
.nav-link.active {
  background: var(--blue-600);
  color: #fff;
  font-weight: 500;
}
.nav-link .manager {
  display: block;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.55);
  margin-top: 1px;
}
.nav-link.active .manager { color: rgba(255, 255, 255, 0.75); }

/* --- Navigation chrome (Design handoff) --- */
.brand-home {
  display: block; width: 100%; text-align: left; border: none; background: none;
  color: inherit; cursor: pointer; padding: 8px 10px; border-radius: 8px; font: inherit;
  margin-bottom: 6px;
}
.brand-home:hover { background: rgba(255, 255, 255, 0.06); }
.brand-home-eyebrow {
  display: flex; align-items: center; gap: 6px; font-size: 10px; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--blue-200); font-weight: 600;
}
.brand-home-sub { display: block; font-size: 11px; color: var(--blue-200); margin-top: 3px; }
.crumb-bar {
  position: sticky; top: 0; z-index: 30; background: #fff;
  border-bottom: 1px solid var(--gray-200); padding: 10px 40px;
  display: flex; align-items: center; gap: 12px; font-size: 12.5px;
}
.crumb-back {
  border: 1px solid #d8e0f5; background: #f4f7ff; color: var(--blue-600); border-radius: 8px;
  padding: 6px 12px; font: inherit; font-size: 12.5px; font-weight: 600; cursor: pointer;
  display: inline-flex; align-items: center; gap: 6px; white-space: nowrap;
}
.crumb-back:hover { background: #e9f0ff; }
.crumb-sep { color: #c4c4c8; }
.crumb-current {
  color: var(--gray-700); font-weight: 600;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.crumb-bar.at-home .crumb-sep,
.crumb-bar.at-home .crumb-current { display: none; }

/* --- Main content ------------------------------------------------------ */
.content {
  padding: 56px 64px 96px;
  max-width: 1100px;
}

.eyebrow {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--gray-500);
  margin-bottom: 8px;
}
h1.team-name {
  font-size: 32px;
  font-weight: 600;
  letter-spacing: -0.015em;
  margin: 0;
  line-height: 1.15;
  color: #000;
}
.manager-name {
  font-size: 14.5px;
  color: var(--gray-600);
  margin: 10px 0 0;
}

h2 {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.01em;
  margin: 56px 0 16px;
  color: #000;
}

/* --- KPI cards --------------------------------------------------------- */
/* League home: weekly matchups + standings (scores.json) */
.mu-block { margin: 0 0 8px; }
.mu-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.mu-title { margin: 0 0 10px; }
.mu-asof { font-size: 12px; color: #8e8e93; }
.mu-list { border: 1px solid #ebebed; border-radius: 10px; background: #fff; overflow: hidden; }
.mu-row { display: grid; grid-template-columns: 1fr 72px 30px 72px 1fr; align-items: center; gap: 8px; padding: 12px 16px; border-bottom: 1px solid #f1f1f3; }
.mu-row:last-of-type { border-bottom: none; }
.mu-team { min-width: 0; }
.mu-team.mu-right { text-align: right; }
.mu-name { font-size: 14px; font-weight: 600; color: #2a2a2e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mu-name a { color: inherit; text-decoration: none; }
.mu-name a:hover { text-decoration: underline; }
.mu-meta { font-size: 11.5px; color: #8e8e93; margin-top: 2px; }
.mu-score { text-align: center; font-variant-numeric: tabular-nums; }
.mu-pts { font-size: 18px; font-weight: 700; color: #606C71; line-height: 1.1; }
.mu-proj { font-size: 11.5px; color: #a0a0a6; margin-top: 2px; }
.mu-lead .mu-pts { color: #0D3A66; }
.mu-vs { text-align: center; font-size: 11px; color: #b8b8bc; font-weight: 600; }
.mu-legend { font-size: 11.5px; color: #8e8e93; padding: 8px 16px; background: #fcfcfd; border-top: 1px solid #f1f1f3; }
.mu-st td.rank { color: #8e8e93; }
.mu-st .sub-line { display: block; font-size: 11px; color: #8e8e93; font-weight: 400; }
@media (max-width: 640px) {
  .mu-st th:nth-child(6), .mu-st td:nth-child(6),
  .mu-st th:nth-child(8), .mu-st td:nth-child(8) { display: none; }
}
.mu-kpis { margin-bottom: 26px; }
.mu-kpis .kpi-text a { color: inherit; text-decoration: none; }
.mu-kpis .kpi-sub { font-size: 12px; color: #8e8e93; margin-top: 4px; font-variant-numeric: tabular-nums; }
@media (max-width: 640px) {
  .mu-row { grid-template-columns: 1fr 56px 22px 56px 1fr; padding: 10px 10px; }
  .mu-name { font-size: 12.5px; white-space: normal; }
  .mu-pts { font-size: 15px; }
}

.kpis {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-top: 36px;
}
.kpi {
  padding: 18px 20px;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  background: var(--gray-50);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100px;
}
.kpi .k {
  font-size: 10.5px;
  color: var(--gray-500);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 600;
  line-height: 1.3;
}
.kpi .v {
  font-size: 26px;
  font-weight: 600;
  margin-top: 10px;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.01em;
  color: var(--blue-800);
}

/* --- Tables ------------------------------------------------------------ */
table.roster {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
  font-size: 14px;
  font-variant-numeric: tabular-nums;
}
table.roster th {
  font-size: 10.5px;
  color: var(--gray-500);
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding: 12px 10px;
  border-bottom: 1.5px solid var(--gray-200);
  text-align: left;
}
table.roster th.num { text-align: right; }
table.roster td {
  padding: 12px 10px;
  border-bottom: 1px solid var(--gray-100);
  vertical-align: middle;
}
table.roster td.num { text-align: right; }
table.roster td.player-name { font-weight: 500; color: #000; }
table.roster td.player-name a {
  color: var(--blue-600);
  text-decoration: none;
}
table.roster td.player-name a:hover { text-decoration: underline; }
table.roster td.meta { color: var(--gray-600); font-size: 13px; }
table.roster td.chain { color: var(--gray-600); font-size: 12.5px; }
table.roster td.cost { font-weight: 500; }
table.roster td.rank { color: var(--gray-500); width: 32px; }

table.roster tr.total td {
  border-top: 1.5px solid #000;
  border-bottom: 1.5px solid #000;
  font-weight: 600;
  padding-top: 14px;
  padding-bottom: 14px;
}

/* --- Pills (DRC tier) -------------------------------------------------- */
.pill {
  display: inline-block;
  padding: 2px 11px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
  min-width: 28px;
  text-align: center;
}
.pill.tier-premium { background: #1761A0; color: #fff; }
.pill.tier-mid     { background: var(--blue-200); color: var(--blue-800); }
.pill.tier-value   { background: #fff8e1; color: #8a6a1a; }
.pill.tier-cheap   { background: var(--gray-100); color: var(--gray-600); }
.pill.pill-draft   { background: #e6f6ee; color: #1c7a4a; }
.kpi .v.kpi-text { font-size: 18px; line-height: 1.2; word-break: break-word; }
/* 2026 draft results board */
.drb-legend { display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: center; margin: 0 0 12px; font-size: 12px; color: var(--gray-600); }
.drb-key { display: inline-block; padding: 2px 10px; border-radius: 999px; border: 1px solid #e3e3e6; background: #fff; font-weight: 600; color: #2b2b2e; }
.drb-key-kept { background: #eaf7ef; border-color: #cdeedb; color: #116b3f; }
.drb-scroll { overflow-x: auto; border: 1px solid #ebebed; border-radius: 8px; background: #fff; }
table.drb { border-collapse: separate; border-spacing: 0; min-width: 1500px; width: 100%; font-size: 12px; }
table.drb th { position: sticky; top: 0; z-index: 2; background: #f7f8fa; border-bottom: 1px solid #ebebed; border-right: 1px solid #f2f2f4; padding: 8px 8px; text-align: left; font-weight: 700; font-size: 12px; color: #0D3A66; vertical-align: top; }
table.drb th a { color: inherit; text-decoration: none; display: block; }
table.drb th a:hover { text-decoration: underline; }
table.drb .drb-slot { display: inline-block; min-width: 18px; margin-right: 6px; color: #606C71; font-weight: 600; font-variant-numeric: tabular-nums; }
table.drb .drb-mgr { display: block; font-weight: 400; color: #606C71; font-size: 11px; margin-top: 1px; }
table.drb td { border-bottom: 1px solid #f2f2f4; border-right: 1px solid #f2f2f4; vertical-align: top; padding: 0; }
table.drb td.drb-round, table.drb th.drb-round { position: sticky; left: 0; z-index: 3; background: #f7f8fa; width: 40px; min-width: 40px; padding: 8px; font-weight: 700; color: #606C71; text-align: center; border-right: 1px solid #ebebed; }
table.drb th.drb-round { z-index: 4; }
table.drb td.drb-cell { min-width: 118px; }
.drb-pick { padding: 6px 8px; display: flex; flex-direction: column; gap: 1px; border-bottom: 1px dashed #eee; }
.drb-pick:last-child { border-bottom: none; }
.drb-pick.drb-kept { background: #eaf7ef; }
.drb-num { font-variant-numeric: tabular-nums; font-size: 10.5px; font-weight: 600; color: #606C71; }
.drb-name { font-weight: 600; color: #000; }
.drb-sub { color: #606C71; font-size: 11px; }
.drb-tag { font-size: 10.5px; font-weight: 600; color: #116b3f; margin-top: 2px; }
.drb-tag-live { color: #98a0ad; font-weight: 500; }
.drb-empty { background: #fafafa; }
.drb-none { display: block; padding: 8px; color: #b3b8c2; font-style: italic; font-size: 11px; }
table.roster.power td.rank { font-weight: 600; color: var(--gray-600); }
table.roster.power td.num .sub-line { display: block; color: var(--gray-500); font-size: 11px; font-weight: 400; margin-top: 1px; }
table.roster th.grade-cell, table.roster td.grade-cell { text-align: center; width: 92px; }
.grade {
  display: inline-block; min-width: 34px; padding: 3px 9px; border-radius: 999px;
  font-size: 12.5px; font-weight: 700; letter-spacing: 0.02em; text-align: center;
}
.grade.grade-a { background: #0D3A66; color: #fff; }
.grade.grade-b { background: #1761A0; color: #fff; }
.grade.grade-c { background: var(--blue-200); color: var(--blue-800); }
.grade.grade-d { background: #fff8e1; color: #8a6a1a; }
.grade.grade-f { background: #fbe9e3; color: #982B09; }
.grade.grade-none { background: var(--gray-100); color: var(--gray-600); }
.grade.grade-pending { background: transparent; color: var(--gray-500); font-weight: 500; font-size: 11.5px; border: 1px dashed #d9d9de; }
table.roster td.acq-cell { white-space: nowrap; }
.acq-note { display: block; color: var(--gray-600); font-size: 11.5px; margin-top: 2px; }
table.roster td .muted { color: var(--gray-500); }

.pill.value-major-steal { background: #cdedd9; color: #0e5730; }
.pill.value-steal       { background: #e6f6ee; color: #1c7a4a; }
.pill.value-fair        { background: #f0f0f2; color: #606C71; }
.pill.value-reach       { background: #fdecea; color: #b42318; }
.pill.value-major-reach { background: #fbd9d3; color: #8f1c11; }
.pill.value-overpriced  { background: #fff0e6; color: #b04a00; }

/* --- DRC trajectory chips (Design handoff) --- */
.traj-chips { display: inline-flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.traj-col { display: inline-flex; flex-direction: column; align-items: center; gap: 1px; }
.traj-chip {
  min-width: 20px; text-align: center; border-radius: 4px; padding: 1px 6px;
  font-weight: 700; font-size: 11.5px; font-variant-numeric: tabular-nums;
}
.traj-yr { font-size: 8.5px; color: #b8b8bc; font-weight: 600; }
.traj-draft { background: #0D3A66; color: #fff; }
.traj-tier1 { background: #e7ecfa; color: #0D3A66; }
.traj-tier2 { background: #eef4e2; color: #5b6b16; }
.traj-tier3 { background: #f0f0f2; color: #606C71; }
.traj-tier4 { background: #fbf3e0; color: #8a6a12; }
.traj-none { color: #c8c8cc; }

/* --- Draft player cell + tap-to-expand log (Design handoff) --- */
.draft-player { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
.draft-pos { color: #a0a0a6; font-size: 11px; }
.draft-tag {
  font-size: 9.5px; font-weight: 700; letter-spacing: 0.03em; text-transform: uppercase;
  padding: 1px 6px; border-radius: 4px; white-space: nowrap;
}
.draft-tag.tag-kept { background: #e7ecfa; color: #0D3A66; }
.draft-tag.tag-traded { background: #fbf3e0; color: #8a6a12; }
.draft-log-toggle {
  color: #b0b0b4; font-size: 15px; font-weight: 700; line-height: 1;
  transition: transform 0.15s; display: inline-flex; align-items: center;
  justify-content: center; width: 13px;
}
.draft-log-toggle.open { transform: rotate(90deg); color: var(--blue-600); }
.draft-log-spacer { display: inline-block; width: 13px; }
.draft-table tr.has-log { cursor: pointer; }
.draft-table tr.has-log:hover td { background: #fafbfe; }
.draft-log-detail > td { padding: 0; background: #fafbfe; }
.dlog-wrap { padding: 10px 16px 12px 40px; }
.dlog-header {
  font-size: 10px; letter-spacing: 0.07em; text-transform: uppercase; color: #8e8e93;
  font-weight: 700; margin-bottom: 6px;
}
.dlog-event { display: flex; gap: 12px; padding: 2px 0; font-size: 12px; }
.dlog-event .event-date {
  color: #909096; white-space: nowrap; min-width: 118px; font-variant-numeric: tabular-nums;
}
.dlog-event .event-desc { color: #2a2a2e; }

/* --- Trades tab: summary strip + verdict cards (Design handoff) --- */
.trade-summary {
  display: flex; flex-wrap: wrap; align-items: stretch; margin: 8px 0;
  border: 1px solid var(--gray-200); border-radius: 10px; overflow: hidden; background: #fcfcfd;
}
.ts-cell { padding: 12px 18px; flex: 1; min-width: 140px; }
.ts-cell + .ts-cell { border-left: 1px solid var(--gray-200); }
.ts-label { font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; color: #8e8e93; font-weight: 600; }
.ts-val { font-size: 22px; font-weight: 700; color: var(--blue-800); font-variant-numeric: tabular-nums; margin-top: 2px; }
.trade-note { font-size: 11.5px; color: #8e8e93; margin: 0 0 18px; }
.trade-note b { color: #2a2a2e; }
.trade-card { border: 1px solid var(--gray-200); border-radius: 11px; overflow: hidden; margin-bottom: 12px; background: #fff; }
.trade-card-head {
  display: flex; justify-content: space-between; align-items: center; gap: 10px;
  padding: 11px 15px; border-bottom: 1px solid #f2f2f4;
}
.trade-card-when { min-width: 0; }
.trade-card .trade-date { font-weight: 700; color: var(--blue-800); font-size: 14px; }
.trade-card .trade-vs { color: #8e8e93; font-size: 13px; }
.verdict-chip {
  display: inline-block; white-space: nowrap; font-size: 12px; font-weight: 700;
  letter-spacing: 0.02em; padding: 4px 11px; border-radius: 20px;
}
.verdict-won { background: #e6f6ee; color: #1c7a4a; }
.verdict-lost { background: #fdecea; color: #b42318; }
.verdict-neutral, .verdict-picks { background: #f0f0f2; color: #606C71; }
.verdict-pending { background: #eef2fb; color: #4a5578; }
.trade-cols { display: grid; grid-template-columns: 1fr 1fr; }
.trade-col { padding: 12px 15px; }
.trade-col-gave { border-left: 1px solid #f2f2f4; }
.trade-col-label { font-size: 10px; letter-spacing: 0.07em; text-transform: uppercase; font-weight: 700; margin-bottom: 7px; }
.label-got { color: #1c7a4a; }
.label-gave { color: #b42318; }
.trade-pl { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; padding: 3px 0; }
.trade-pl-name { min-width: 0; }
.pl-name { font-weight: 600; color: #2a2a2e; }
.pl-meta { color: #8e8e93; font-size: 11.5px; }
.trade-pl-since { font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; }
.pl-since-na { color: #b0b0b4; }
.since-pos { color: #1c7a4a; }
.since-neg { color: #b42318; }
.trade-pl-empty { color: #c0c0c4; font-size: 13px; padding: 3px 0; }
.trade-pick-chips { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }
.pick-chip { display: inline-block; border-radius: 5px; padding: 2px 8px; font-size: 11.5px; font-weight: 600; }
.pick-got { background: #e7ecfa; color: var(--blue-800); }
.pick-gave { background: #f0f0f2; color: #606C71; }
.trade-history { border-top: 1px solid #f2f2f4; }
.trade-history > summary {
  padding: 8px 15px; font-size: 11.5px; color: #8e8e93; cursor: pointer; font-weight: 600; list-style: none;
}
.trade-history > summary::-webkit-details-marker { display: none; }
.trade-history[open] > summary { color: var(--blue-600); }
.trade-hist-table { width: calc(100% - 30px); border-collapse: collapse; font-size: 12.5px; font-variant-numeric: tabular-nums; margin: 2px 15px 14px; }
.trade-hist-table th {
  text-align: left; font-size: 9.5px; letter-spacing: 0.06em; text-transform: uppercase;
  color: #b0b0b4; font-weight: 600; padding: 5px 8px;
}
.trade-hist-table th.num, .trade-hist-table td.num { text-align: right; }
.trade-hist-table td { padding: 4px 8px; border-top: 1px solid #f5f5f5; color: #606C71; }
.trade-hist-table td.h-player { color: #2a2a2e; }
.trade-hist-table td.h-since { font-weight: 600; }
.htag {
  display: inline-block; white-space: nowrap; text-transform: uppercase; font-size: 9px;
  font-weight: 700; letter-spacing: 0.04em; padding: 1px 5px; border-radius: 3px;
}
.htag-got { background: #e6f6ee; color: #1c7a4a; }
.htag-gave { background: #fdecea; color: #b42318; }
@media (max-width: 560px) {
  .trade-cols { grid-template-columns: 1fr; }
  .trade-col-gave { border-left: none; border-top: 1px solid #f2f2f4; }
}

/* --- Expandable player history ---------------------------------------- */
.expand-btn {
  background: none;
  border: 1px solid var(--gray-200);
  border-radius: 4px;
  width: 18px;
  height: 18px;
  font-size: 13px;
  font-weight: 600;
  color: var(--gray-600);
  cursor: pointer;
  margin-right: 8px;
  line-height: 1;
  padding: 0;
  display: inline-block;
  vertical-align: middle;
  transition: transform 0.15s ease;
}
.expand-btn:hover { color: var(--blue-600); border-color: var(--blue-400); }
.expand-btn.open  { transform: rotate(90deg); color: var(--blue-600); border-color: var(--blue-600); }

.expand-col { width: 28px; text-align: center; }

tr.history-row > td.history-cell {
  padding: 0;
  background: var(--gray-50);
  border-bottom: 1px solid var(--gray-200);
}
.history-cards {
  display: flex;
  gap: 14px;
  padding: 16px 20px 18px 20px;
  flex-wrap: nowrap;
  overflow-x: auto;
}
.year-card {
  flex: 1 1 0;
  min-width: 180px;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  background: #fff;
  padding: 14px 16px;
}
.year-card.card-empty {
  background: #fafafa;
  border-color: #ececec;
  opacity: 0.65;
}
.year-card .year-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--blue-600);
  margin-bottom: 12px;
}
.year-card.card-empty .year-label { color: var(--gray-500); }
.year-card .year-metric {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 5px 0;
  font-size: 13px;
  border-top: 1px solid var(--gray-100);
}
.year-card .year-metric:first-of-type { border-top: none; padding-top: 0; }
.year-card .m-label {
  color: var(--gray-500);
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.year-card .m-val {
  font-variant-numeric: tabular-nums;
  color: var(--gray-700);
  font-weight: 500;
}

/* --- Tabs (Roster / Drafts / etc.) ----------------------------------- */
.tabs {
  display: flex;
  gap: 24px;
  border-bottom: 1px solid var(--gray-200);
  margin: 40px 0 24px 0;
}
.tab-btn {
  background: none;
  border: none;
  padding: 10px 0;
  font-family: inherit;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: -0.005em;
  color: var(--gray-600);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}
.tab-btn:hover { color: var(--blue-600); }
.tab-btn.active {
  color: var(--blue-800);
  font-weight: 600;
  border-bottom-color: var(--blue-600);
}
.tab-panel[hidden] { display: none; }

/* --- Drafts: collapsible per-year blocks ----------------------------- */
.year-collapsible {
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  margin-bottom: 14px;
  overflow: hidden;
}
.year-collapsible-header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 18px;
  background: #fff;
  border: none;
  font-family: inherit;
  font-size: 14px;
  font-weight: 600;
  color: var(--gray-700);
  cursor: pointer;
  text-align: left;
}
.year-collapsible-header:hover { background: var(--gray-50); }
.year-collapsible .year-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--blue-800);
  letter-spacing: 0.04em;
}
.year-collapsible .year-meta {
  color: var(--gray-500);
  font-size: 12px;
  font-weight: 500;
}
.year-collapsible .year-chev {
  margin-left: auto;
  color: var(--gray-500);
  font-size: 16px;
  transition: transform 0.15s ease;
}
.year-collapsible.open .year-chev { transform: rotate(90deg); color: var(--blue-600); }
.year-collapsible-body {
  display: none;
  padding: 6px 18px 16px;
  border-top: 1px solid var(--gray-100);
  background: var(--gray-50);
}
.year-collapsible.open .year-collapsible-body { display: block; }

.draft-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
  font-variant-numeric: tabular-nums;
  background: #fff;
}
.draft-table th {
  font-size: 10.5px;
  color: var(--gray-500);
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 10px 10px;
  border-bottom: 1px solid var(--gray-200);
  text-align: center;
}
.draft-table td {
  padding: 10px;
  border-bottom: 1px solid var(--gray-200);
}
.draft-table td.num { text-align: right; }
.draft-table td.pick-label {
  color: var(--blue-800);
  font-weight: 600;
  width: 64px;
  text-align: center;
}
.draft-table td.player-name { font-weight: 500; color: #000; }
.draft-table td.meta { color: var(--gray-600); }
.draft-table td.type-code {
  text-align: center;
  font-weight: 600;
  color: var(--blue-800);
}
.draft-table td.trajectory-cell {
  color: var(--gray-700);
  font-size: 12.5px;
  font-variant-numeric: tabular-nums;
}

/* Round-banding leftmost column - subtle Blue 200 with Blue 800 text */
.draft-table td.round-cell {
  background: #eaf4ff;
  color: var(--blue-800);
  font-weight: 600;
  font-size: 13px;
  text-align: center;
  width: 44px;
  border-bottom: 1px solid var(--gray-200);
  border-right: 2px solid var(--blue-200);
  vertical-align: middle;
  letter-spacing: 0.04em;
}
/* Empty-round placeholder row (no pick that round) */
.draft-table tr.round-empty td {
  color: var(--gray-500);
  font-style: italic;
  background: #fafafa;
}

/* Traded-for row highlight: subtle blue tint + left accent */
.draft-table tr.traded-for td:not(.round-cell) {
  background: #f4f9ff !important;
}
.draft-table tr.traded-for td.pick-label {
  border-left: 3px solid var(--blue-400);
  padding-left: 7px;
}

/* Player-name tooltip on hover */
.draft-table td.player-name {
  position: relative;
  overflow: visible;
}
.draft-table .player-name-link {
  cursor: help;
  border-bottom: 1px dashed var(--gray-300);
}
.draft-table .player-name-link:hover {
  border-bottom-color: var(--blue-600);
  color: var(--blue-800);
}
.draft-table .player-tooltip {
  display: none;
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 12px 14px 14px;
  min-width: 320px;
  max-width: 420px;
  z-index: 100;
  font-size: 12px;
  line-height: 1.5;
  text-align: left;
  font-weight: 400;
}
.draft-table td.player-name:hover .player-tooltip { display: block; }
.draft-table .tooltip-header {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--blue-800);
  padding-bottom: 8px;
  margin-bottom: 8px;
  border-bottom: 1px solid var(--gray-200);
}
.draft-table .tooltip-event {
  display: flex;
  gap: 10px;
  padding: 4px 0;
}
.draft-table .tooltip-event .event-date {
  color: var(--gray-500);
  flex: 0 0 80px;
  font-variant-numeric: tabular-nums;
}
.draft-table .tooltip-event .event-desc {
  color: var(--gray-700);
  flex: 1 1 auto;
}

/* Subtle alternating round background bands on data rows */
.draft-table tr.round-2 td:not(.round-cell),
.draft-table tr.round-4 td:not(.round-cell),
.draft-table tr.round-6 td:not(.round-cell),
.draft-table tr.round-8 td:not(.round-cell),
.draft-table tr.round-10 td:not(.round-cell),
.draft-table tr.round-12 td:not(.round-cell),
.draft-table tr.round-14 td:not(.round-cell),
.draft-table tr.round-16 td:not(.round-cell) {
  background: #fafbfc;
}

.empty-note { color: var(--gray-500); font-size: 13px; padding: 8px 0; }

/* Traded-for row highlight */
.draft-table tr.traded-for td:not(.round-cell) { background: #f4f9ff !important; }
.draft-table tr.traded-for td.pick-label {
  border-left: 3px solid var(--blue-400);
  padding-left: 7px;
}

/* Player tooltip */
.draft-table td.player-name { position: relative; overflow: visible; }
.draft-table .player-name-link {
  cursor: help;
  border-bottom: 1px dashed var(--gray-300);
}
.draft-table .player-name-link:hover {
  border-bottom-color: var(--blue-600);
  color: var(--blue-800);
}
.draft-table .player-tooltip {
  display: none;
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 12px 14px 14px;
  min-width: 320px;
  max-width: 420px;
  z-index: 100;
  font-size: 12px;
  line-height: 1.5;
  text-align: left;
  font-weight: 400;
}
.draft-table td.player-name:hover .player-tooltip { display: block; }
.draft-table .tooltip-header {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--blue-800);
  padding-bottom: 8px;
  margin-bottom: 8px;
  border-bottom: 1px solid var(--gray-200);
}
.draft-table .tooltip-event {
  display: flex;
  gap: 10px;
  padding: 4px 0;
}
.draft-table .tooltip-event .event-date {
  color: var(--gray-500);
  flex: 0 0 80px;
  font-variant-numeric: tabular-nums;
}
.draft-table .tooltip-event .event-desc {
  color: var(--gray-700);
  flex: 1 1 auto;
}

/* --- Trades tab -------------------------------------------------------- */
.trade-event {
  border: 1px solid var(--gray-200);
  border-radius: 10px;
  background: #fff;
  padding: 16px 20px;
  margin-bottom: 18px;
}
.trade-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-bottom: 12px;
  margin-bottom: 14px;
  border-bottom: 1px solid var(--gray-200);
}
.trade-date {
  font-size: 13px;
  font-weight: 600;
  color: var(--blue-800);
  letter-spacing: 0.03em;
}
.trade-vs { font-size: 13px; color: var(--gray-600); }
.trade-side { margin-bottom: 12px; }
.trade-side-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--gray-500);
  margin-bottom: 6px;
}
.trade-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  font-variant-numeric: tabular-nums;
  table-layout: fixed;
}
.trade-table col.col-player { width: 38%; }
.trade-table col.col-pos { width: 8%; }
.trade-table col.col-nfl { width: 10%; }
.trade-table col.col-year { width: 14.66%; }
.trade-table th {
  font-size: 10.5px;
  color: var(--gray-500);
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 8px 10px;
  border-bottom: 1px solid var(--gray-200);
  text-align: center;
}
.trade-table th:first-child,
.trade-table th:nth-child(2),
.trade-table th:nth-child(3) { text-align: left; }
.trade-table th.num { text-align: right; }
.trade-table td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--gray-100);
  vertical-align: middle;
}
.trade-table td.player-name { font-weight: 500; }
.trade-table td.meta { color: var(--gray-600); font-size: 12.5px; }
.trade-table td.num { text-align: right; }
.trade-table td.cost { font-weight: 600; color: var(--blue-800); }
.trade-table tr.subtotal-row td {
  background: var(--gray-50);
  font-weight: 600;
  border-top: 1.5px solid var(--gray-200);
  border-bottom: none;
}

/* Points cell with mini-bar */
.pts-cell {
  display: inline-block;
  text-align: right;
  position: relative;
  min-width: 60px;
  padding-bottom: 12px;
}
.pts-cell .pts-full { font-weight: 500; color: var(--gray-700); }
.pts-cell .pts-post-trade {
  display: block;
  font-size: 10px;
  color: var(--gray-500);
  font-style: italic;
}
.mini-bar-track {
  position: absolute;
  bottom: 0;
  left: 0; right: 0;
  height: 7px;
  background: var(--gray-200);
  border-radius: 3px;
  overflow: hidden;
}
.mini-bar-fill {
  height: 100%;
  background: var(--blue-600);
  border-radius: 3px;
}

/* --- Player search section -------------------------------------------- */
.ps-input-wrap {
  margin-bottom: 24px;
  max-width: 560px;
}
.ps-input {
  width: 100%;
  box-sizing: border-box;
  padding: 14px 18px 14px 46px;
  font-family: inherit;
  font-size: 15.5px;
  border: 2px solid #c5c9d2;
  border-radius: 10px;
  background: #fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23606C71' stroke-width='2.4' stroke-linecap='round'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cline x1='16.5' y1='16.5' x2='21' y2='21'/%3E%3C/svg%3E") 14px center / 20px 20px no-repeat;
  color: var(--gray-800);
  box-shadow: 0 2px 8px rgba(13, 58, 102, 0.08);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.ps-input:hover { border-color: #9aa1ad; }
.ps-input::placeholder { color: #82889a; }
.ps-input:focus {
  outline: none;
  border-color: var(--blue-600);
  box-shadow: 0 0 0 3px rgba(23, 97, 160, 0.14), 0 2px 8px rgba(13, 58, 102, 0.08);
}
.ps-input-meta {
  margin-top: 6px;
  font-size: 12px;
  color: var(--gray-500);
}
.ps-empty-state {
  padding: 28px 0;
  color: var(--gray-500);
  font-size: 14px;
  font-style: italic;
}
.ps-results { display: flex; flex-direction: column; gap: 12px; }
.player-card {
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 6px;
  padding: 14px 18px;
}
.player-card-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--gray-100);
  margin-bottom: 10px;
}
.player-card-title { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.player-card-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--blue-800);
}
.player-card-meta {
  font-size: 12px;
  color: var(--gray-600);
  letter-spacing: 0.04em;
}
.ps-owner {
  font-size: 11.5px;
  font-weight: 500;
  color: var(--gray-700);
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  border-radius: 4px;
  padding: 3px 8px;
}
.ps-owner-none { color: var(--gray-500); font-style: italic; }
.player-card-events { display: flex; flex-direction: column; gap: 4px; }
.ps-event {
  display: flex;
  gap: 12px;
  font-size: 13px;
  padding: 3px 0;
}
.ps-event-date {
  flex: 0 0 88px;
  color: var(--gray-500);
  font-variant-numeric: tabular-nums;
}
.ps-event-desc { color: var(--gray-800); }
.ps-event-empty {
  font-size: 13px;
  color: var(--gray-500);
  font-style: italic;
}

/* ---- Three summary cards inside each player-card ---- */
.psum-row-cards {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr;
  gap: 12px;
  margin: 12px 0 18px 0;
}
.psum-card {
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  border-radius: 5px;
  padding: 12px 14px;
}
.psum-card-label {
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gray-500);
  margin-bottom: 8px;
}
.psum-card-hero {
  background: var(--blue-800);
  color: #fff;
  border-color: var(--blue-800);
}
.psum-card-hero .psum-card-label {
  color: rgba(255, 255, 255, 0.75);
}
.psum-big {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}
.psum-big-sub {
  font-size: 12.5px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 2px;
}
.psum-big-meta {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.65);
  margin-top: 6px;
  font-variant-numeric: tabular-nums;
}
/* ---- Two-column DRC | Performance row ---- */
.ps-two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin: 14px 0 18px 0;
}
.ps-side {
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  border-radius: 6px;
  padding: 14px;
}
.ps-side-label {
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gray-500);
  margin-bottom: 12px;
}
.ps-hero {
  border-radius: 5px;
  padding: 14px 16px;
  margin-bottom: 12px;
  color: #fff;
}
.ps-hero-drc { background: var(--blue-800); border-left: 3px solid #E1B523; }
.ps-hero-adp { background: var(--blue-600); }
.ps-hero-big {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.05;
  font-variant-numeric: tabular-nums;
}
.ps-hero-sub {
  font-size: 11.5px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 4px;
}
.ps-side-tiles {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}
.ps-side-tile {
  background: #fff;
  border: 1px solid var(--gray-200);
  border-left: 3px solid var(--gray-400);
  border-radius: 4px;
  padding: 10px 8px;
  text-align: left;
}
.ps-side-val {
  font-size: 16px;
  font-weight: 700;
  color: var(--blue-800);
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
}
.ps-side-sub {
  font-size: 10.5px;
  color: var(--gray-700);
  font-weight: 500;
  margin-top: 3px;
}
.ps-side-yr {
  font-size: 9.5px;
  font-weight: 600;
  letter-spacing: 0.14em;
  color: var(--gray-500);
  margin-top: 6px;
  text-transform: uppercase;
}

/* Weekly fantasy points: three side-by-side weekly bar charts */
.ps-charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}
.ps-chart-col {
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 5px;
  padding: 10px;
}
.ps-chart-wrap {
  background: var(--gray-50);
  border-radius: 3px;
  padding: 4px 2px;
}
.ps-chart-svg {
  display: block;
  width: 100%;
  height: 70px;
}
.ps-chart-labels {
  margin-top: 10px;
  text-align: center;
}
.ps-chart-year {
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gray-500);
}
.ps-chart-stats {
  margin-top: 5px;
  font-size: 12.5px;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 6px;
}
.ps-chart-rank {
  font-weight: 700;
  color: var(--blue-800);
  font-variant-numeric: tabular-nums;
}
.ps-chart-sep { color: var(--gray-400); }
.ps-chart-pts {
  font-weight: 600;
  color: var(--gray-800);
  font-variant-numeric: tabular-nums;
}
.ps-chart-adp {
  font-weight: 500;
  color: var(--gray-700);
  font-variant-numeric: tabular-nums;
}

/* Position-rank neighbor table under each year's chart.
   table-layout: fixed lets the name column absorb all leftover width —
   without it, max-width tricks collapse the name to ~0px on mobile. */
.ps-nb-table {
  width: 100%;
  margin-top: 12px;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 11.5px;
  font-variant-numeric: tabular-nums;
}
.ps-nb-table td {
  padding: 4px 6px;
  border-bottom: 1px solid var(--gray-100);
  vertical-align: middle;
}
.ps-nb-table tr:last-child td { border-bottom: none; }
.ps-nb-rank {
  width: 40px;
  font-weight: 600;
  color: var(--gray-600);
  letter-spacing: 0.02em;
}
.ps-nb-name {
  color: var(--gray-800);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ps-nb-pts {
  text-align: right;
  width: 44px;
  color: var(--gray-700);
}
.ps-nb-table tr.ps-nb-self td {
  background: rgba(23, 97, 160, 0.07);
  color: var(--blue-800);
  font-weight: 700;
}
.ps-nb-table tr.ps-nb-self .ps-nb-pts { color: var(--blue-800); }
.ps-nb-empty {
  margin-top: 10px;
  font-size: 11px;
  color: var(--gray-500);
  font-style: italic;
  text-align: center;
}
.ps-spark-empty {
  font-size: 12px;
  color: var(--gray-500);
  font-style: italic;
  padding: 8px 0 12px 0;
}
.psum-stat-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.psum-stat-val {
  font-size: 20px;
  font-weight: 700;
  color: var(--blue-800);
  font-variant-numeric: tabular-nums;
}
.psum-stat-key {
  font-size: 11px;
  color: var(--gray-500);
  margin-top: 2px;
  letter-spacing: 0.04em;
}

/* ---- Section subdividers within player-card ---- */
.ps-section { margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--gray-100); }
.ps-section-label {
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gray-500);
  margin-bottom: 10px;
}

/* ---- KPI strip: 2023-2026 DRC + current ADP ---- */
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}
.kpi-tile {
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 5px;
  padding: 12px 14px;
  text-align: left;
}
.kpi-tile-historical {
  border-left: 3px solid var(--gray-400);
}
.kpi-tile-current {
  background: rgba(225, 181, 35, 0.06);
  border-color: rgba(225, 181, 35, 0.30);
  border-left: 3px solid #E1B523;
}
.kpi-tile-current .kpi-big { color: #8C6E10; }
.kpi-tile-adp {
  background: var(--gray-50);
  border-left: 3px solid var(--blue-400);
}
.kpi-big {
  font-size: 22px;
  font-weight: 700;
  color: var(--blue-800);
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.01em;
}
.kpi-sub {
  font-size: 11.5px;
  color: var(--gray-700);
  font-weight: 500;
  margin-top: 4px;
}
.kpi-tag {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gray-500);
  margin-top: 6px;
}

/* ---- Ownership lineage timeline ---- */
.lineage-flow {
  display: flex;
  align-items: stretch;
  gap: 8px;
  flex-wrap: wrap;
}
.lineage-node {
  flex: 1 1 180px;
  min-width: 180px;
  background: #fff;
  border: 1px solid var(--gray-200);
  border-left: 3px solid var(--gray-400);
  border-radius: 4px;
  padding: 10px 12px;
}
.lineage-drafted { border-left-color: var(--blue-600); }
.lineage-trade { border-left-color: var(--gold-400, #E1B523); }
.lineage-waiver { border-left-color: var(--gray-500); }
.lineage-free-agent { border-left-color: var(--gray-500); }
.lineage-date {
  font-size: 11px;
  color: var(--gray-500);
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
}
.lineage-manager {
  font-size: 14px;
  font-weight: 600;
  color: var(--blue-800);
  margin-top: 2px;
}
.lineage-method {
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--gray-500);
  margin-top: 6px;
}
.lineage-detail {
  font-size: 12px;
  color: var(--gray-700);
  margin-top: 2px;
}
.lineage-arrow {
  display: flex;
  align-items: center;
  color: var(--gray-400);
  font-size: 18px;
  padding: 0 2px;
}
.lineage-cost {
  display: inline-block;
  margin-top: 8px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #eef4ff;
  color: var(--blue-800);
  font-size: 12px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.lineage-cost-now { background: #e8f6ec; color: #14532d; font-size: 13px; }
.lineage-now { border-left-color: #16a34a; background: #fbfffc; }
.lineage-tag {
  font-size: 10.5px;
  color: var(--gray-500);
  margin-top: 4px;
  letter-spacing: 0.02em;
}
.lineage-break {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 0 6px;
  max-width: 92px;
  text-align: center;
}
.lineage-break-x { color: #b91c1c; font-size: 14px; font-weight: 700; }
.lineage-break-txt {
  font-size: 9.5px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #b91c1c;
}

/* --- Commissioner's Desk ----------------------------------------------- */
.desk-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 28px;
  align-items: start;
}
.desk-rail {
  position: sticky;
  top: 24px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.desk-post-link {
  display: block;
  padding: 10px 14px;
  border-radius: 5px;
  text-decoration: none;
  color: var(--gray-800);
  border-left: 3px solid transparent;
  transition: background 0.12s, border-color 0.12s;
  cursor: pointer;
}
.desk-post-link:hover {
  background: var(--gray-50);
}
.desk-post-link.desk-active {
  background: var(--gray-50);
  border-left-color: var(--blue-600);
}
.desk-post-link-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--blue-800);
  line-height: 1.25;
}
.desk-post-link-date {
  font-size: 11px;
  color: var(--gray-500);
  margin-top: 3px;
  letter-spacing: 0.04em;
}
.desk-content { max-width: 780px; }
.desk-post-header {
  border-bottom: 1px solid var(--gray-200);
  padding-bottom: 18px;
  margin-bottom: 24px;
}
.desk-post-title {
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: var(--blue-800);
  margin: 0 0 6px 0;
  line-height: 1.15;
}
.desk-post-meta {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--gray-500);
}
.desk-post-summary {
  margin-top: 12px;
  font-size: 14px;
  color: var(--gray-700);
  line-height: 1.55;
  font-style: italic;
}
.desk-post-body p {
  font-size: 14.5px;
  line-height: 1.65;
  color: var(--gray-800);
  margin: 0 0 14px 0;
}
.desk-post-body strong { color: var(--blue-800); font-weight: 600; }
.desk-post-body em { color: var(--gray-700); }
.desk-post-body h1.desk-h1 {
  font-size: 22px;
  font-weight: 700;
  color: var(--blue-800);
  margin: 32px 0 12px 0;
  letter-spacing: -0.01em;
}
.desk-post-body h2.desk-h2 {
  font-size: 19px;
  font-weight: 700;
  color: var(--blue-800);
  margin: 30px 0 12px 0;
  letter-spacing: -0.005em;
}
/* Pete's *asterisk-wrapped* section headers render here. Strong visual break,
   no underline (clean look). */
.desk-post-body h3.desk-h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--blue-800);
  margin: 30px 0 12px 0;
  letter-spacing: -0.005em;
  text-transform: none;
}
.desk-post-body h4.desk-h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--gray-700);
  margin: 20px 0 8px 0;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
/* Inline-bold sub-section heads like "*FAAB, FA, and Trade Moves: *". These
   sit between a team-finish header and the prose underneath. Tighter than h3. */
.desk-post-body h4.desk-subhead {
  font-size: 15px;
  font-weight: 700;
  color: var(--gray-800);
  margin: 20px 0 6px 0;
  letter-spacing: -0.003em;
  text-transform: none;
}
/* Inline markdown links in desk posts ([text](https://...)). */
.desk-post-body a.desk-link {
  color: var(--blue-600);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.desk-post-body a.desk-link:hover {
  color: var(--blue-800);
}
/* Team-finish header card: bold name + chips for each labelled stat.
   Used in season wrap-ups (one card per team, in finish order). */
.team-finish-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
  margin: 40px 0 18px 0;
  padding: 14px 18px;
  background: var(--gray-50);
  border-left: 3px solid var(--blue-600);
  border-radius: 5px;
}
.team-finish-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--blue-800);
  margin: 0;
  letter-spacing: -0.01em;
}
.team-finish-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.team-chip {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
  font-size: 11.5px;
  background: #fff;
  border: 1px solid var(--gray-200);
  padding: 4px 10px;
  border-radius: 3px;
}
.team-chip-k {
  font-weight: 600;
  color: var(--gray-500);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 10px;
}
.team-chip-v {
  font-weight: 700;
  color: var(--blue-800);
  font-variant-numeric: tabular-nums;
}
.desk-figure {
  margin: 22px 0;
  padding: 0;
}
.desk-img {
  display: block;
  max-width: 100%;
  height: auto;
  border: 1px solid var(--gray-200);
  border-radius: 5px;
}
.desk-figure figcaption {
  margin-top: 8px;
  font-size: 11.5px;
  color: var(--gray-500);
  font-style: italic;
  text-align: center;
  letter-spacing: 0.02em;
}
.desk-img-missing {
  margin: 16px 0;
  padding: 12px 14px;
  background: var(--gray-50);
  border: 1px dashed var(--gray-300);
  border-radius: 5px;
  font-size: 12.5px;
  color: var(--gray-600);
  font-style: italic;
}
.desk-post-body ul.desk-list, .desk-post-body ol.desk-list {
  margin: 4px 0 16px 0;
  padding-left: 22px;
}
.desk-post-body ul.desk-list li, .desk-post-body ol.desk-list li {
  font-size: 14.5px;
  line-height: 1.55;
  color: var(--gray-800);
  margin-bottom: 6px;
}

/* --- League rules section ---------------------------------------------- */
.rules-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 780px;
}
.rule-block {
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 6px;
  padding: 22px 26px;
}
.rule-block-new {
  border-left: 3px solid #E1B523;
  background: rgba(225, 181, 35, 0.04);
}
.rule-new-pill {
  display: inline-block;
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #8C6E10;
  background: rgba(225, 181, 35, 0.18);
  padding: 4px 10px;
  border-radius: 3px;
  margin-bottom: 12px;
}
.rule-h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--blue-800);
  margin: 0 0 12px 0;
  letter-spacing: -0.01em;
}
.rule-h3 {
  font-size: 13px;
  font-weight: 600;
  color: var(--gray-700);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin: 18px 0 8px 0;
}
.rule-block p {
  font-size: 14px;
  line-height: 1.55;
  color: var(--gray-800);
  margin: 0 0 12px 0;
}
.rule-block p:last-child { margin-bottom: 0; }
.rule-block strong { color: var(--blue-800); font-weight: 600; }
.rule-block em { color: var(--gray-700); }
.rules-list {
  margin: 8px 0 12px 0;
  padding-left: 22px;
}
.rules-list li {
  font-size: 14px;
  line-height: 1.5;
  color: var(--gray-800);
  margin-bottom: 4px;
}
.rules-note {
  font-size: 12.5px !important;
  color: var(--gray-600) !important;
  font-style: italic;
}
.rules-table {
  width: auto;
  margin: 8px 0 12px 0;
  border-collapse: collapse;
  font-size: 13.5px;
  font-variant-numeric: tabular-nums;
}
.rules-table th, .rules-table td {
  padding: 7px 18px 7px 0;
  border-bottom: 1px solid var(--gray-100);
  text-align: left;
}
.rules-table th {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--gray-500);
}
.rules-table td.num, .rules-table th.num { text-align: right; }
.rules-table tbody tr:last-child td { border-bottom: none; }

/* Sub-callout: a newly-passed change inside an otherwise-established rule */
.rule-sub-callout {
  margin-top: 18px;
  padding: 16px 18px;
  background: rgba(225, 181, 35, 0.06);
  border: 1px solid rgba(225, 181, 35, 0.30);
  border-left: 3px solid #E1B523;
  border-radius: 5px;
}
.rule-sub-callout .rule-new-pill { margin-bottom: 10px; }
.rule-sub-callout p { font-size: 13.5px; }

/* Side-by-side old vs. new comparison table */
.rules-table-compare {
  width: 100%;
  margin: 12px 0 10px 0;
}
.rules-table-compare th, .rules-table-compare td {
  padding: 7px 10px;
}
.rules-th-new {
  color: #8C6E10 !important;
}
.rules-td-new {
  background: rgba(225, 181, 35, 0.10);
  font-weight: 600;
  color: #8C6E10;
}

/* --- Last-updated widget: click-to-expand footer stamp -----------------
   CSS-only accordion driven by a hidden checkbox; no JS. Trigger sits
   inline with the source footnote as a subtle right-aligned text link. */
.updated-widget { margin: 4px 0 0; text-align: right; }
.updated-toggle {
  position: absolute; opacity: 0; pointer-events: none;
  width: 0; height: 0; margin: 0;
}
.updated-trigger {
  display: inline-flex; align-items: center; gap: 5px;
  cursor: pointer; user-select: none;
  font-size: 11.5px; color: var(--gray-500);
  padding: 4px 8px; border-radius: 4px;
  font-variant-numeric: tabular-nums;
}
.updated-trigger:hover { background: rgba(0, 0, 0, 0.04); color: var(--gray-700); }
.updated-trigger::after { content: "\25B8"; font-size: 9px; opacity: 0.6; }
.updated-toggle:checked + .updated-trigger::after { content: "\25BE"; }
.updated-toggle:focus-visible + .updated-trigger {
  outline: 2px solid var(--blue-600); outline-offset: 2px;
}
.updated-details {
  display: none;
  text-align: left;
  margin-top: 6px;
  background: #fbfbfd; border: 1px solid var(--gray-200); border-radius: 8px;
  padding: 10px 14px 12px; font-size: 12px; color: var(--gray-700);
  overscroll-behavior: contain;
}
.updated-toggle:checked ~ .updated-details { display: block; }
.updated-details .updated-row {
  display: flex; gap: 10px; align-items: baseline;
  padding: 3px 0;
}
.updated-details .updated-k {
  flex: 0 0 130px;
  font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase;
  font-weight: 600; color: var(--gray-500);
}
.updated-details .updated-v {
  flex: 1 1 auto; min-width: 0; word-break: break-word;
  font-variant-numeric: tabular-nums;
}
.updated-details .updated-log {
  margin-top: 10px;
  border-top: 1px solid var(--gray-100);
  padding-top: 8px;
}
.updated-details .updated-log-h {
  font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase;
  font-weight: 600; color: var(--gray-500); margin-bottom: 4px;
}
.updated-details .updated-log-body {
  margin: 0;
  font-family: "SF Mono", ui-monospace, Menlo, Monaco, Consolas, monospace;
  font-size: 10.5px; color: var(--gray-600);
  white-space: pre-wrap; word-break: break-word; line-height: 1.5;
}
/* Mobile tightening — narrower key column, smaller monospace. */
@media (max-width: 480px) {
  .updated-details .updated-row { flex-wrap: wrap; gap: 2px; }
  .updated-details .updated-k { flex-basis: 100%; font-size: 9.5px; }
  .updated-details .updated-v { font-size: 11.5px; }
  .updated-details .updated-log-body { font-size: 10px; }
}

/* --- Footnote ---------------------------------------------------------- */
.footnote {
  margin-top: 48px;
  padding-top: 18px;
  border-top: 1px solid var(--gray-200);
  font-size: 11.5px;
  color: var(--gray-500);
  font-style: italic;
}


/* Player search: autocomplete suggestions dropdown */
.ps-suggestions {
  max-width: 560px;
  margin-bottom: 18px;
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  max-height: 320px;
  overflow-y: auto;
}
.ps-suggestion {
  display: block;
  padding: 9px 14px;
  text-decoration: none;
  color: var(--gray-800);
  font-size: 14px;
  border-bottom: 1px solid var(--gray-100);
  cursor: pointer;
}
.ps-suggestion:last-child { border-bottom: none; }
.ps-suggestion:hover {
  background: var(--gray-50);
  color: var(--blue-800);
  font-weight: 500;
}


/* ---- Collapsible Teams in sidebar ---- */
.sidebar details.sidebar-teams { margin-top: 4px; }
.sidebar details.sidebar-teams > summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  list-style: none;
  padding: 14px 16px 8px 16px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.55);
}
.sidebar details.sidebar-teams > summary::-webkit-details-marker { display: none; }
.sidebar details.sidebar-teams > summary::after {
  content: "+";
  margin-left: 8px;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.55);
  transition: transform 0.18s ease;
}
.sidebar details.sidebar-teams[open] > summary::after { content: "\2212"; }
.sidebar-team-list { display: flex; flex-direction: column; }

/* ====================================================================== */
/* Stacked sub-line inside name cells (manager under team, pos/NFL under
   player). Hidden on desktop where those have their own columns; shown on
   mobile where the columns are hidden to keep rows to one clean line. */
.sub-line { display: none; }

/* ====================================================================== */
/* Trade analyzer                                                         */
/* ====================================================================== */
.ta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin: 6px 0 20px;
}
.ta-side {
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  border-radius: 5px;
  padding: 14px 16px;
}
.ta-label {
  display: block;
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--gray-600);
  margin-bottom: 6px;
}
.ta-team {
  width: 100%;
  font-family: inherit;
  font-size: 13.5px;
  padding: 8px 10px;
  border: 1px solid var(--gray-200);
  border-radius: 4px;
  background: #fff;
  color: var(--gray-800);
  margin-bottom: 10px;
}
.ta-roster { max-height: 320px; overflow-y: auto; }
.ta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 6px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
}
.ta-row:hover { background: #fff; }
.ta-row input { margin: 0; flex: 0 0 auto; }
.ta-row .ta-nm {
  flex: 1 1 auto;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
  color: var(--gray-800);
}
.ta-row .ta-meta { color: var(--gray-600); font-size: 11.5px; flex: 0 0 auto; }
.ta-row .ta-cost {
  flex: 0 0 auto;
  font-variant-numeric: tabular-nums;
  font-size: 12px;
  font-weight: 600;
  color: var(--blue-800);
  width: 86px;
  text-align: right;
}
.ta-board { margin-top: 12px; border-top: 1px solid var(--gray-200); padding-top: 10px; }
.ta-board summary {
  cursor: pointer; font-size: 12px; font-weight: 600; color: var(--blue-800);
  letter-spacing: 0.02em;
}
.ta-board summary:hover { color: var(--blue-600); }
table.ta-slots {
  width: 100%; border-collapse: collapse; margin-top: 8px;
  font-size: 11.5px; font-variant-numeric: tabular-nums; table-layout: fixed;
}
table.ta-slots td { padding: 4px 6px; border-bottom: 1px solid var(--gray-100); vertical-align: top; }
table.ta-slots td.ta-rd { width: 34px; font-weight: 700; color: var(--gray-600); }
table.ta-slots tr.ta-gone td { background: #faf4f2; }
table.ta-slots tr.ta-gone td.ta-rd { color: var(--red-600, #982B09); text-decoration: line-through; }
.ta-slot-player { font-weight: 600; color: var(--gray-800); }
.ta-slot-note { color: var(--gray-500); font-size: 10.5px; }
.ta-slot-up { color: #AA5200; font-weight: 600; }
.ta-orig-chip {
  display: inline-block; background: #eef3ff; color: var(--blue-800);
  border-radius: 3px; font-size: 10px; font-weight: 600; padding: 0 5px; margin-left: 4px;
}
.ta-legend {
  font-size: 10.5px; color: var(--gray-500); margin: 8px 0 6px; line-height: 1.5;
}
.ta-leg-acq { color: var(--blue-800); background: #eef3ff; border-radius: 3px; padding: 0 4px; }
.ta-leg-gone { color: var(--red-600, #982B09); }
.ta-slotrow {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 3px 0; border-bottom: 1px solid var(--gray-100);
}
.ta-slotrow.ta-gone { background: #faf4f2; border-radius: 3px; }
.ta-slotrow.ta-gone .ta-rd { color: var(--red-600, #982B09); text-decoration: line-through; }
.ta-slotrow .ta-rd {
  flex: 0 0 30px; font-size: 11px; font-weight: 700; color: var(--gray-600);
  padding-top: 4px; font-variant-numeric: tabular-nums;
}
.ta-pills { display: flex; flex-wrap: wrap; gap: 4px; flex: 1 1 auto; }
.ta-pill {
  display: inline-flex; align-items: baseline; gap: 5px;
  border: 1px solid var(--gray-200); border-radius: 4px;
  background: #fff; padding: 3px 8px; font-size: 11.5px; font-weight: 600;
  color: var(--gray-800); line-height: 1.4;
}
.ta-pill em { font-style: normal; font-weight: 600; font-size: 10px; color: var(--blue-800); }
.ta-pill i { font-style: normal; font-size: 10px; color: var(--gray-500); }
.ta-pill.open { border-style: dashed; color: var(--gray-500); font-weight: 500; }
.ta-pill.acq { background: #eef3ff; border-color: #c9d8ff; }
.ta-pill .ta-gl { color: var(--gray-500); font-weight: 700; }
.ta-pill .ta-gl-up { color: #AA5200; }
.ta-goneto { font-size: 11px; color: var(--red-600, #982B09); padding-top: 4px; }
.ta-unkeep {
  margin-top: 8px; font-size: 11.5px; color: var(--red-600, #982B09);
  background: #fbe9e2; border-radius: 4px; padding: 7px 10px; line-height: 1.5;
}
.ta-warnings {
  margin: 16px 0 0; background: #fff8e8; border: 1px solid var(--gold-400);
  border-radius: 5px; padding: 12px 16px;
}
.ta-warnings h3 { font-size: 13px; margin: 0 0 8px; color: #674F00; }
.ta-warnings ul { margin: 0; padding-left: 18px; font-size: 12.5px; color: var(--gray-800); }
.ta-warnings li { margin-bottom: 5px; line-height: 1.5; }
.ta-warn-bad { color: var(--red-600, #982B09); font-weight: 600; }
.ta-picks { margin-top: 12px; border-top: 1px solid var(--gray-200); padding-top: 10px; }
.ta-picks select, .ta-add-pick {
  font-family: inherit;
  font-size: 12.5px;
  padding: 5px 8px;
  border: 1px solid var(--gray-200);
  border-radius: 4px;
  background: #fff;
  color: var(--gray-800);
}
.ta-add-pick { cursor: pointer; font-weight: 600; color: var(--blue-800); }
.ta-add-pick:hover { border-color: var(--blue-600); }
.ta-pick-chips { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px; }
.ta-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 999px;
  padding: 3px 6px 3px 11px;
  font-size: 12px;
  font-weight: 600;
  color: var(--blue-800);
}
.ta-chip button {
  border: none; background: none; cursor: pointer;
  color: var(--gray-500); font-size: 14px; line-height: 1; padding: 0 3px;
}
.ta-chip button:hover { color: var(--gray-800); }
.ta-results { margin-top: 4px; }
.ta-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.ta-recv {
  border: 1px solid var(--gray-200);
  border-radius: 5px;
  padding: 14px 16px;
  background: #fff;
}
.ta-recv h3 { font-size: 14px; margin: 0 0 10px; color: var(--blue-800); }
table.ta-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12.5px;
  font-variant-numeric: tabular-nums;
  table-layout: fixed;
}
table.ta-table th {
  text-align: left;
  font-size: 9.5px;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: var(--gray-600);
  padding: 4px 6px;
  border-bottom: 1px solid var(--gray-200);
}
table.ta-table td { padding: 6px; border-bottom: 1px solid var(--gray-100); }
table.ta-table th.num, table.ta-table td.num { text-align: right; }
table.ta-table td.ta-pname {
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500;
}
table.ta-table td.ta-frozen { font-weight: 700; color: var(--blue-800); }
table.ta-table tr.ta-total td {
  border-top: 1.5px solid #000; border-bottom: none; font-weight: 700;
}
.ta-keepnote { font-size: 10.5px; color: var(--gray-500); display: block; }
.ta-bullets { margin: 14px 0 0; padding: 0 0 0 18px; font-size: 13px; color: var(--gray-800); }
.ta-bullets li { margin-bottom: 6px; line-height: 1.5; }
.ta-cap-up { color: var(--red-600, #982B09); font-weight: 600; }
.ta-cap-down { color: var(--green-600, #6B7D00); font-weight: 600; }
.ta-empty {
  font-size: 13px; color: var(--gray-500); font-style: italic;
  padding: 14px 0;
}
.ta-foot {
  font-size: 11.5px;
  color: var(--gray-500);
  margin-top: 22px;
  line-height: 1.6;
  border-top: 1px solid var(--gray-200);
  padding-top: 12px;
}
/* ---- Trade summary strip: at-a-glance stats card per team.
   Facts-only (no verdict). Two-column grid on desktop, still
   two-column on mobile (cards get denser + smaller type). */
.ta-sum-strip {
  margin-top: 12px;
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 10px;
  padding: 12px 14px 14px;
}
.ta-sum-h {
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--gray-500);
  margin-bottom: 10px;
}
.ta-sum-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.ta-sum-card {
  background: var(--gray-50);
  border: 1px solid var(--gray-100);
  border-radius: 8px;
  padding: 10px 12px;
  min-width: 0;
}
.ta-sum-mgr {
  font-weight: 700;
  font-size: 13.5px;
  color: var(--blue-800);
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ta-sum-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
  font-size: 12.5px;
  padding: 4px 0;
  border-top: 1px solid var(--gray-100);
}
.ta-sum-row:first-of-type { border-top: none; }
.ta-sum-k {
  color: var(--gray-600);
  font-size: 10.5px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-weight: 600;
  flex: 0 0 auto;
}
.ta-sum-v {
  color: var(--gray-800);
  font-variant-numeric: tabular-nums;
  text-align: right;
  min-width: 0;
}
/* Position-net-swing block. Compact facts-only line per team. */
.ta-pos-swing {
  margin-top: 10px;
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 10px;
  padding: 10px 14px 12px;
}
.ta-pos-h {
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--gray-500);
  margin-bottom: 6px;
}
.ta-pos-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  font-size: 12.5px;
  font-variant-numeric: tabular-nums;
}
.ta-pos-mgr {
  display: block;
  font-weight: 600;
  color: var(--blue-800);
  font-size: 11.5px;
  margin-bottom: 3px;
}

/* ====================================================================== */
/* Feedback widget: floating trigger + modal                              */
/* ====================================================================== */
.fb-trigger {
  margin-top: 26px;
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.10);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 999px;
  padding: 10px 16px;
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition: background 0.15s ease;
}
.fb-trigger:hover { background: rgba(255, 255, 255, 0.18); }
.fb-icon { font-size: 14px; line-height: 1; }
.fb-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 110;
}
.fb-overlay[hidden], .fb-modal[hidden] { display: none; }
.fb-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 115;
  width: min(380px, calc(100vw - 36px));
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 6px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.22);
  padding: 18px 20px 16px 20px;
}
.fb-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2px;
}
.fb-modal-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--blue-800);
  margin: 0;
}
.fb-close {
  background: none;
  border: none;
  font-size: 22px;
  line-height: 1;
  color: var(--gray-500);
  cursor: pointer;
  padding: 2px 4px;
}
.fb-close:hover { color: var(--gray-800); }
.fb-modal-sub {
  font-size: 12.5px;
  color: var(--gray-600);
  margin: 0 0 14px 0;
}
.fb-form label.fb-label {
  display: block;
  margin-bottom: 12px;
}
.fb-field-label {
  display: block;
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--gray-600);
  margin-bottom: 4px;
}
.fb-form input[type="text"],
.fb-form textarea {
  width: 100%;
  box-sizing: border-box;
  font-family: inherit;
  font-size: 13.5px;
  color: var(--gray-800);
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 4px;
  padding: 8px 10px;
  resize: vertical;
}
.fb-form input[type="text"]:focus,
.fb-form textarea:focus {
  outline: none;
  border-color: var(--blue-600);
  box-shadow: 0 0 0 2px rgba(23, 97, 160, 0.12);
}
.fb-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 2px;
}
.fb-btn {
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
}
.fb-btn-primary {
  background: var(--blue-600);
  color: #fff;
  border: 1px solid var(--blue-600);
}
.fb-btn-primary:hover { background: var(--blue-800); border-color: var(--blue-800); }
.fb-btn-secondary {
  background: #fff;
  color: var(--gray-700);
  border: 1px solid var(--gray-200);
}
.fb-btn-secondary:hover { border-color: var(--gray-500); }
.fb-modal-foot {
  font-size: 11px;
  color: var(--gray-500);
  font-style: italic;
  margin: 12px 0 0 0;
}

/* ====================================================================== */
/* Mobile responsive layer (<= 720px) */
/* ====================================================================== */
.menu-toggle, .sidebar-tab { display: none; }
.sidebar-backdrop { display: none; }

@media (max-width: 720px) {
  .layout {
    grid-template-columns: 1fr;
    display: block;
  }
  /* Always-visible right-edge tab that re-opens the menu. */
  .sidebar-tab {
    display: flex;
    position: fixed;
    top: 0;
    left: 0;
    width: 30px;
    height: 100vh;
    background: var(--blue-800);
    color: #fff;
    z-index: 95;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    border: none;
    padding: 0;
    font-family: inherit;
  }
  .sidebar-tab span {
    writing-mode: vertical-rl;
    text-orientation: mixed;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    transform: rotate(180deg);
  }
  /* Old top hamburger hidden — replaced by the right tab. */
  .menu-toggle { display: none; }
  /* Sidebar slides in from the RIGHT, not the left. */
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    /* Explicit dvh height (dynamic viewport height) instead of
       top:0 + bottom:0. Mobile Chrome's URL bar & tabs bar collapse and
       re-expand as the user scrolls; vh + bottom:0 both compute against
       the LARGEST viewport, so the sidebar's bottom is hidden under the
       chrome when the bar is expanded. dvh tracks the visible viewport,
       so the sidebar's floor sits above the chrome and the last team
       stays tappable. Fallback for browsers that don't support dvh:
       start with 100vh, then override with 100dvh. */
    height: 100vh;
    height: 100dvh;
    bottom: auto;
    right: auto;
    width: min(280px, 82vw);
    z-index: 100;
    transform: translateX(-100%);
    transition: transform 0.22s ease;
    overflow-y: auto;
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
    /* Clear the iOS home-indicator gesture area + Chrome's bottom chrome
       so the last team in the Teams list isn't visually pinned to the
       edge (or worse, hidden under the chrome). */
    padding-bottom: calc(40px + env(safe-area-inset-bottom, 0px));
    box-shadow: 2px 0 12px rgba(0, 0, 0, 0.2);
  }
  body.sidebar-open .sidebar { transform: translateX(0); }
  .sidebar-backdrop {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.45);
    z-index: 90;
  }
  body.sidebar-open .sidebar-backdrop { display: block; }
  .content {
    padding: 14px 14px 14px 42px;
    margin-left: 0 !important;
  }
  .section-header { padding: 14px 0 18px 0; }
  .section-title { font-size: 22px; line-height: 1.15; }
  .section-sub { font-size: 13px; }
  .ps-two-col { grid-template-columns: 1fr; }
  .ps-charts-row { grid-template-columns: 1fr; }
  .kpi-strip { grid-template-columns: 1fr 1fr; }
  .psum-row-cards { grid-template-columns: 1fr; }
  .desk-layout { grid-template-columns: 1fr; }
  .desk-rail {
    position: static;
    flex-direction: row;
    overflow-x: auto;
    padding-bottom: 8px;
    margin-bottom: 14px;
    border-bottom: 1px solid var(--gray-200);
    gap: 6px;
  }
  .desk-post-link {
    flex: 0 0 auto;
    border-left: none;
    border-bottom: 3px solid transparent;
    padding: 8px 12px;
  }
  .desk-post-link.desk-active {
    border-left: none;
    border-bottom-color: var(--blue-600);
  }
  .desk-content { max-width: 100%; }
  .desk-post-title { font-size: 20px; }
  .trade-table, .draft-table, .player-table { font-size: 11.5px; }
  .rules-grid { max-width: 100%; }
  .rule-block { padding: 16px 18px; }
  .rule-h2 { font-size: 16px; }
  .ps-side-tiles { grid-template-columns: 1fr 1fr 1fr; gap: 6px; }
  .ps-side-tile { padding: 8px 6px; }
  .ps-side-val { font-size: 14px; }
  .ps-hero-big { font-size: 22px; }
  .lineage-flow { flex-direction: column; }
  .lineage-arrow { transform: rotate(90deg); padding: 4px 0; }
  .lineage-node { flex: 1 1 auto; min-width: 0; }
  .ps-nb-table { font-size: 10.5px; }
  .ps-nb-rank { width: 32px; }
  .ps-nb-pts { width: 36px; }
  /* Player search input: make sure border + focus glow stay inside the
     content padding (was getting cut off slightly on the right edge). */
  .ps-input-wrap { max-width: 100%; padding-right: 2px; }
  .ps-input:focus { box-shadow: 0 0 0 2px rgba(23, 97, 160, 0.12); }

  /* Roster/summary tables: shrink padding + font, then hide secondary
     columns PER TABLE TYPE and surface that data as a stacked sub-line
     under the name instead — every row stays one clean line. */
  table.roster { font-size: 12px; }
  table.roster th, table.roster td { padding: 7px 6px; }
  table.roster th { font-size: 9.5px; letter-spacing: 0.08em; }
  /* Standings: hide Manager, Players, Premium → keep #, Team, Total cap.
     Manager shows as a sub-line under the team name. */
  table.standings th:nth-child(3), table.standings td:nth-child(3),
  table.standings th:nth-child(4), table.standings td:nth-child(4),
  table.standings th:nth-child(5), table.standings td:nth-child(5) { display: none; }
  /* Team rosters: hide Pos, NFL, ADP → KEEP DRC, Cost, Value (the data
     that matters on a keeper dashboard). Pos · NFL shows as a sub-line. */
  /* Compact roster (2026-08-30): Slot, Player, Pos, DRC, Cost. On small
     screens hide only Pos (3) — the player sub-line carries pos/team. */
  table.team-roster th:nth-child(3), table.team-roster td:nth-child(3) { display: none; }
  .sub-line {
    display: block;
    font-size: 10.5px;
    font-weight: 400;
    color: var(--gray-600);
    margin-top: 2px;
    letter-spacing: 0.01em;
  }
  td.player-name { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 46vw; }
  /* Small 3-col tables don't need to be horizontal scroll regions. */
  .content table.ps-nb-table { display: table; }
  /* Current-owner chip: never wrap mid-name. */
  .ps-owner { white-space: nowrap; font-size: 10.5px; padding: 3px 6px; }
  /* Trade analyzer: stack the two sides; results tables shrink. */
  .ta-grid, .ta-cols { grid-template-columns: 1fr; gap: 12px; }
  .ta-roster { max-height: 250px; }
  .ta-row { padding: 7px 6px; }
  table.ta-table { font-size: 11px; }
  table.ta-table td, table.ta-table th { padding: 5px 4px; }
  /* Trade summary strip: keep two-column layout even on mobile so both
     teams stay comparable; tighten padding, shrink type. */
  .ta-sum-strip { padding: 10px 10px 12px; }
  .ta-sum-grid { gap: 6px; }
  .ta-sum-card { padding: 8px 9px; }
  .ta-sum-mgr { font-size: 12px; margin-bottom: 6px; }
  .ta-sum-row { font-size: 11.5px; padding: 3px 0; gap: 4px; flex-wrap: wrap; }
  .ta-sum-k { font-size: 9.5px; }
  .ta-sum-v { font-size: 11.5px; text-align: right; }
  .ta-pos-swing { padding: 8px 10px 10px; }
  .ta-pos-grid { grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11.5px; }
  .ta-pos-mgr { font-size: 10.5px; }
  /* Feedback modal: bottom sheet feel on small screens. */
  .fb-modal {
    width: min(380px, calc(100vw - 28px));
    max-height: 72vh;
    overflow-y: auto;
  }

  /* KPI cards: stack 2-up, keep consistent visual height. */
  .kpis { grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 24px; }
  .kpi { padding: 14px; min-height: 86px; }
  .kpi .k { font-size: 9.5px; }
  .kpi .v { font-size: 22px; margin-top: 8px; }
  /* Keep wide tables independently scrollable instead of overflowing the page.
     This lets the page itself stay at viewport width and preserves pinch-to-zoom. */
  .team-section, .tab-panel, section.team-section { max-width: 100%; }
  /* Make every main-content table its own horizontal scroll region. */
  .content table {
    display: block;
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  /* Don't strip overflow off the body/content — that breaks iOS pinch zoom. */
}

@media (max-width: 480px) {
  body { font-size: 13px; }
  .content { padding: 10px 10px 10px 42px; }
  .kpi-strip { grid-template-columns: 1fr 1fr; }
  .section-title { font-size: 20px; }
}

/* ---- Player comparison ----------------------------------------------- */
.pc-top { position:relative; max-width:560px; margin:0 0 16px; }
.pc-sugg { position:absolute; top:100%; left:0; right:0; z-index:40; background:#fff; border:1px solid #d8d8dc; border-radius:10px; margin-top:4px; box-shadow:0 8px 24px rgba(0,0,0,.12); overflow:hidden; }
.pc-sugg-item { display:flex; align-items:center; gap:8px; padding:8px 12px; cursor:pointer; font-size:13px; }
.pc-sugg-item:hover { background:#eef4ff; }
.pc-sugg-item .pc-sugg-meta { color:#8e8e93; font-size:11.5px; flex:none; }
.pc-sugg-item .pc-sugg-owner { margin-left:auto; color:#606C71; font-size:11px; text-align:right; }
.pc-cols { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px; align-items:start; }
.pc-card { background:#fff; border:1px solid #e3e3e6; border-radius:12px; padding:14px 16px; }
.pc-head { display:flex; align-items:baseline; gap:8px; }
.pc-name { font-weight:700; font-size:15.5px; color:#0D3A66; flex:1 1 auto; min-width:0; }
.pc-x { flex:none; border:none; background:none; color:#98a0ad; cursor:pointer; font-size:14px; padding:0 2px; }
.pc-x:hover { color:#b42318; }
.pc-meta { color:#606C71; font-size:12px; margin:2px 0 8px; }
.pc-owner { font-size:12px; color:#2a2a2e; background:#f7f8fa; border:1px solid #ececef; border-radius:8px; padding:5px 9px; margin:0 0 4px; }
.pc-owner b { color:#0D3A66; }
.pc-season { border-top:1px solid #f0f0f2; padding-top:10px; margin-top:10px; }
.pc-yr { font-size:10.5px; letter-spacing:.06em; text-transform:uppercase; color:#8e8e93; font-weight:700; }
.pc-dot { display:inline-block; width:8px; height:8px; border-radius:2px; margin-right:6px; vertical-align:baseline; }
.pc-pts { font-size:20px; font-weight:700; color:#0D3A66; font-variant-numeric:tabular-nums; }
.pc-sub { color:#606C71; font-size:11.5px; margin:1px 0 6px; }
.pc-empty { color:#8e8e93; font-size:12.5px; padding:8px 0 2px; }
.pc-hintcard { border:1px dashed #d8d8dc; border-radius:10px; padding:26px; text-align:center; color:#8e8e93; font-size:13px; grid-column:1/-1; }
.pc-chart { width:100%; height:54px; display:block; }
/* ---- Keeper board ---------------------------------------------------- */
.kb-top { display:flex; gap:14px; align-items:center; flex-wrap:wrap; margin:0 0 14px; }
.kb-top select { font: inherit; padding:7px 10px; border:1px solid #ccc; border-radius:8px; background:#fff; min-width:230px; }
.kb-cap { margin-left:auto; display:flex; gap:10px; align-items:center; }
.kb-cap-box { background:#0D3A66; color:#fff; border-radius:10px; padding:8px 16px; text-align:left; }
.kb-cap-box .kb-cap-num { font-size:20px; font-weight:700; font-variant-numeric: tabular-nums; }
.kb-cap-box .kb-cap-lbl { font-size:11px; color:#81BEF6; letter-spacing:.04em; text-transform:uppercase; }
.kb-btn { font:inherit; font-weight:600; border:1px solid #ccc; background:#fff; border-radius:8px; padding:8px 14px; cursor:pointer; }
.kb-btn:hover { border-color:#1761A0; color:#1761A0; }
.kb-cols { display:grid; grid-template-columns: 340px 1fr; gap:18px; align-items:start; }
.kb-panel { background:#fff; border:1px solid #e3e3e6; border-radius:12px; overflow:hidden; }
.kb-panel-h { padding:10px 14px; background:#f7f8fa; border-bottom:1px solid #e9e9ec; font-weight:700; font-size:13px; }
.kb-panel-h .kb-sub { font-weight:400; color:#606C71; font-size:12px; }
.kb-roster { max-height: 640px; overflow-y:auto; }
.kb-card { display:flex; align-items:center; gap:8px; padding:8px 12px; border-bottom:1px solid #f0f0f2; cursor:pointer; user-select:none; }
.kb-card:last-child { border-bottom:none; }
.kb-card .kb-nm { font-weight:600; font-size:13.5px; flex:1 1 auto; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.kb-card .kb-meta { color:#606C71; font-size:11.5px; flex:none; font-variant-numeric: tabular-nums; }
.kb-card .kb-check { flex:none; width:18px; height:18px; border:2px solid #c5c9d2; border-radius:5px; display:inline-flex; align-items:center; justify-content:center; font-size:12px; color:#fff; }
.kb-card.kb-on .kb-check { background:#1761A0; border-color:#1761A0; }
.kb-card.kb-on { background:#f4f8ff; }
.kb-card.kb-picked { outline:2px solid #1761A0; outline-offset:-2px; background:#eaf1ff; }
.kb-card.kb-chasm-card { background:#fdecea; }
.kb-board .kb-row { display:flex; align-items:center; gap:10px; padding:7px 12px; border-bottom:1px solid #f0f0f2; min-height:38px; }
.kb-board .kb-rnum { flex:none; width:26px; font-weight:700; color:#606C71; font-size:12.5px; text-align:right; }
.kb-slot { flex:1 1 0; border:1.5px dashed #d6d9e0; border-radius:8px; min-height:30px; padding:3px 8px; display:flex; align-items:center; gap:8px; flex-wrap:wrap; font-size:12.5px; background:#fbfbfc; }
.kb-slot.kb-acq { border-style:solid; border-color:#c9b45e; background:#fdfaf0; }
.kb-slot .kb-origin { color:#8a6a12; font-size:10.5px; text-transform:uppercase; letter-spacing:.03em; flex:none; }
.kb-slot.kb-legal { border-color:#1761A0; background:#eef4ff; box-shadow:0 0 0 2px rgba(0,56,255,.12); cursor:pointer; }
.kb-slot.kb-illegal { opacity:.45; }
.kb-slot .kb-seated { font-weight:600; flex:1 1 auto; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.kb-slot .kb-meta { flex:none; font-variant-numeric:tabular-nums; }
.kb-slot .kb-slot-notes { flex:1 1 100%; order:9; color:#98a0ad; font-size:10.5px; line-height:1.3; padding:0 0 1px 2px; margin-top:-2px; }
.kb-slot .kb-flag { flex:none; font-size:10.5px; background:#fff6e0; color:#8a6a12; border-radius:10px; padding:1px 7px; }
.kb-slot .kb-x { flex:none; margin-left:auto; border:none; background:none; color:#98a0ad; cursor:pointer; font-size:13px; padding:0 2px; }
.kb-slot .kb-x:hover { color:#b42318; }
.kb-row.kb-gone { background:#fdf3f2; }
.kb-row.kb-gone .kb-goneto { color:#b42318; font-size:12px; }
.kb-chasm-strip { margin:10px 12px; border-top:1px dashed #f0cfc9; padding-top:10px; }
.kb-chasm-chip { display:inline-block; background:#fdecea; color:#b42318; font-size:11px; font-weight:700; padding:2px 8px; border-radius:20px; margin:0 6px 6px 0; }
.kb-hint { color:#606C71; font-size:12px; margin:10px 0 0; }
/* Pick numbers (lottery order), stacked multi-pick rounds, drag states */
.kb-picknum { flex:none; font-size:10.5px; font-weight:700; color:#606C71; background:#f0f1f4; border-radius:6px; padding:1px 6px; font-variant-numeric:tabular-nums; }
.kb-slot.kb-acq .kb-picknum { background:#f5ecce; color:#8a6a12; }
.kb-picknum-gone { background:#f7dcd8; color:#b42318; }
.kb-row.kb-row-cont { border-top:none; padding-top:2px; }
.kb-rnum-cont { color:#c5c9d2; font-weight:600; }
.kb-gone-slot { border-style:none; background:none; }
.kb-slot[data-dragpid] { cursor:grab; user-select:none; }
.kb-slot[data-dragpid]:active { cursor:grabbing; }
.kb-slot.kb-drop-hot { background:#dbe7ff; border-style:solid; border-color:#1761A0; }
.kb-dragging .kb-roster { opacity:.75; }
.kb-card.kb-unplaced { background:#fff8e6; }
.kb-card.kb-unplaced .kb-check { background:#c9971c; border-color:#c9971c; }
/* Slot-first placement: open picks are tappable */
.kb-slot.kb-open { cursor:pointer; }
.kb-slot.kb-open:hover { border-color:#9aa1ad; background:#f4f6fa; }
.kb-open-hint { color:#b6bcc7; font-size:11.5px; }
.kb-pf-overlay { position:fixed; inset:0; background:rgba(15,18,25,.45); z-index:120; display:flex; align-items:center; justify-content:center; padding:16px; }
.kb-pf { background:#fff; border-radius:14px; max-width:440px; width:100%; padding:16px 18px; box-shadow:0 12px 40px rgba(0,0,0,.25); }
.kb-pf h3 { margin:0 0 10px; font-size:15px; }
.kb-pf-list { max-height:60vh; overflow-y:auto; display:flex; flex-direction:column; gap:6px; }
.kb-pf-item { display:flex; flex-wrap:wrap; align-items:baseline; gap:4px 8px; width:100%; text-align:left; font:inherit; border:1.5px solid #d6d9e0; background:#fbfbfc; border-radius:10px; padding:9px 12px; cursor:pointer; }
.kb-pf-item:hover { border-color:#1761A0; background:#eef4ff; }
.kb-pf-nm { font-weight:700; font-size:13.5px; flex:1 1 auto; min-width:0; }
.kb-pf-pos { color:#606C71; font-weight:400; font-size:12px; }
.kb-pf-meta { flex:none; color:#2a2a2e; font-size:12px; font-variant-numeric:tabular-nums; }
.kb-pf-tag { flex:1 1 100%; color:#8a919c; font-size:10.5px; }
.kb-pf-none { color:#606C71; font-size:12.5px; margin:4px 0 8px; }
.kb-pf-cancel { margin-top:10px; width:100%; }
/* Trade analyzer: pick pills are clickable (add to / remove from trade) */
.ta-pill { cursor:pointer; user-select:none; }
.ta-pill:hover { box-shadow:0 0 0 2px rgba(0,56,255,.15); }
.kb-wait-chip { display:inline-block; background:#fff6e0; color:#8a6a12; font-size:11px; font-weight:700; padding:2px 8px; border-radius:20px; margin:0 6px 6px 0; }
/* ---- 2026 draft board (league-wide) ---------------------------------- */
.db26-top { margin: 0 0 14px; }
.db26-toggle { font-size: 13px; font-weight: 600; color: #2b2b2e; display: flex; align-items: baseline; gap: 8px; cursor: pointer; flex-wrap: wrap; }
.db26-toggle input { transform: translateY(1px); }
.db26-toggle-sub { font-weight: 400; color: #606C71; font-size: 12px; }
.db26-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; align-items: start; }
.db26-round { background: #fff; border: 1px solid #ebebed; border-radius: 8px; overflow: hidden; }
.db26-round-h { display: flex; justify-content: space-between; align-items: baseline; padding: 8px 12px; background: #f7f8fa; border-bottom: 1px solid #ebebed; font-weight: 700; font-size: 13px; color: #0D3A66; }
.db26-cost { font-weight: 600; font-size: 11px; color: #606C71; }
.db26-pick { display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px; padding: 6px 12px; border-bottom: 1px solid #f2f2f4; }
.db26-pick:last-child { border-bottom: none; }
.db26-num { flex: 0 0 44px; font-variant-numeric: tabular-nums; font-weight: 700; font-size: 12px; color: #606C71; }
.db26-team { font-size: 13px; font-weight: 600; display: flex; flex-direction: column; min-width: 0; flex: 1; }
.db26-mgr { font-weight: 400; font-size: 11.5px; color: #606C71; }
.db26-acq { background: #fdfaf0; }
.db26-acq .db26-num { color: #8a6a12; }
.db26-stack { flex-basis: 100%; padding: 2px 0 4px 52px; display: flex; flex-direction: column; gap: 2px; }
.db26-kp { font-size: 12px; font-weight: 600; }
.db26-kp-sub { font-weight: 400; color: #606C71; font-size: 11px; }
.db26-none { font-size: 11px; color: #98a0ad; font-style: italic; }
.db26-used { background: #f2f8f4; }
.db26-seat { flex-basis: 100%; padding: 2px 0 2px 52px; font-size: 12.5px; font-weight: 700; color: #116b3f; }
.db26-seat .db26-kp-sub { font-weight: 400; }
.db26-await { background: #fffaf0; border: 1px solid #f0e3c0; border-radius: 8px; padding: 10px 14px; margin: 0 0 14px; display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 12.5px; }
.db26-await-h { flex-basis: 100%; font-weight: 700; color: #8C6E10; font-size: 12px; letter-spacing: .02em; }
.db26-await-item.db26-chasm { color: #b42318; font-weight: 600; }
.db26-teamsel { font: inherit; font-size: 13px; padding: 3px 8px; border: 1px solid #d9d9de; border-radius: 6px; background: #fff; color: #2b2b2e; margin: 0 2px; }
.slot-col { font-weight: 700; color: #0D3A66; white-space: nowrap; width: 64px; }
tr.slot-empty td.empty-slot { color: #98a0ad; font-style: italic; font-weight: 400; }
tr.group-h td { background: #f7f8fa; font-weight: 700; font-size: 12px; letter-spacing: .06em; text-transform: uppercase; color: #606C71; padding: 6px 12px; border-top: 1px solid #ebebed; }
.pill.kept-pill { background: #e8f5ee; color: #116b3f; font-weight: 700; }
.year-card-2026 { border-color: #c9dfd2; }
.m-val.kept-yes { color: #116b3f; font-weight: 700; }
.m-val.kept-no { color: #98a0ad; }
.roster-note { font-size: 12.5px; color: #606C71; margin: 0 0 10px; }
.bp-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; align-items: start; }
.bp-card { background: #fff; border: 1px solid #ebebed; border-radius: 8px; padding: 14px 16px; }
.bp-card.bp-empty { background: #fafbfc; }
.bp-mgr { margin: 0 0 8px; font-size: 15px; color: #0D3A66; }
.bp-list { margin: 0; padding-left: 20px; display: flex; flex-direction: column; gap: 8px; font-size: 13.5px; }
.bp-none { color: #98a0ad; font-style: italic; font-size: 13px; margin: 0; }
.bp-bold { font-size: 11px; font-weight: 700; border-radius: 10px; padding: 1px 8px; white-space: nowrap; }
.bp-tbd { background: #f2f2f4; color: #606C71; }
.bp-b1 { background: #eef2fb; color: #0D3A66; }
.bp-b2 { background: #fdf6e3; color: #8C6E10; }
.bp-b3 { background: #fdeeee; color: #b42318; }
.bp-oc { font-size: 11px; font-weight: 700; }
.bp-right { color: #116b3f; }
.bp-wrong { color: #b42318; }
.k26-name { font-weight: 600; }
.k26-open { color: #98a0ad; font-style: italic; }
.k26-up { font-size: 11px; color: #8C6E10; font-weight: 600; }
.k26-chasm { color: #b42318; font-weight: 600; font-size: 12.5px; padding: 8px 12px; }

/* Keeper board: slot-occupancy banner */
.kb-slotbar { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 14px; }
.kb-slotbar-inpanel { margin: 10px 14px 2px; }
.kb-slotchip { font-size: 12px; font-weight: 600; color: #606C71; background: #f0f0f2; border-radius: 6px; padding: 4px 10px; white-space: nowrap; }
.kb-slotchip .kb-slotnum { font-variant-numeric: tabular-nums; font-weight: 700; }
.kb-slot-part { background: #e6efff; color: #0D3A66; }
.kb-slot-full { background: #0D3A66; color: #fff; }
.kb-slot-over { background: #fdecea; color: #b42318; }

/* Keeper board: lineup preview (Yahoo slot layout) */
.kb-lineup { margin-top: 16px; }
.kb-lu-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 28px; padding: 10px 14px 14px; }
.kb-lu-colh { font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #606C71; padding: 6px 0 4px; border-bottom: 1px solid #ebebed; }
.kb-lu-row { display: flex; align-items: baseline; gap: 8px; padding: 6px 0; border-bottom: 1px solid #f2f2f4; min-height: 30px; flex-wrap: wrap; }
.kb-lu-slot { flex: 0 0 62px; font-size: 11px; font-weight: 700; color: #0D3A66; background: #e6efff; border-radius: 4px; text-align: center; padding: 2px 0; }
.kb-lu-slot-bn { background: #f0f0f2; color: #606C71; }
.kb-lu-nm { font-weight: 600; font-size: 13px; }
.kb-lu-sub { color: #606C71; font-weight: 400; font-size: 12px; }
.kb-lu-meta { margin-left: auto; color: #606C71; font-size: 11.5px; font-variant-numeric: tabular-nums; }
.kb-lu-open { color: #98a0ad; font-size: 12px; font-style: italic; }
.kb-lu-over { background: #fdf3f2; }
.kb-lu-over .kb-lu-slot { background: #fdecea; color: #b42318; }
@media (max-width: 760px) { .kb-lu-grid { grid-template-columns: 1fr; } }

.kb-print { display:none; }
@media (max-width: 900px) {
  .kb-cols { grid-template-columns: 1fr; }
  .kb-roster { max-height: 320px; }
}
/* Mobile keeper-row stacking: at narrow widths, restructure each seated
   row so the full player name lives on line 1 (no truncation), DRC/$ and
   any flag chips on line 2, and the ACQ chip (if present) on line 3.
   The close X is pinned to the top-right so it stays a clean tap target
   regardless of row height. Desktop layout is untouched. */
@media (max-width: 480px) {
  .kb-board .kb-row {
    align-items: flex-start;
    gap: 6px;
    padding: 7px 8px;
  }
  .kb-board .kb-rnum {
    padding-top: 4px;
  }
  .kb-slot {
    position: relative;
    flex-wrap: wrap;
    row-gap: 3px;
    column-gap: 6px;
    padding: 6px 40px 6px 8px;
    min-height: 34px;
  }
  .kb-slot .kb-seated {
    order: 1;
    flex: 1 1 100%;
    white-space: normal;
    overflow: visible;
    text-overflow: clip;
    line-height: 1.25;
    font-size: 13px;
  }
  .kb-slot .kb-meta {
    order: 2;
    flex: 0 0 auto;
    margin-left: 0;
    font-size: 11px;
  }
  .kb-slot .kb-flag {
    order: 2;
    font-size: 10px;
    padding: 1px 6px;
  }
  .kb-slot .kb-origin {
    order: 3;
    flex: 1 1 100%;
    font-size: 10px;
  }
  .kb-slot .kb-x {
    position: absolute;
    top: 3px;
    right: 4px;
    margin-left: 0;
    padding: 4px 8px;
    font-size: 16px;
    line-height: 1;
  }
}
@media print {
  body.kb-printing .sidebar, body.kb-printing .crumb-bar, body.kb-printing .menu-toggle,
  body.kb-printing .sidebar-tab, body.kb-printing .kb-app,
  body.kb-printing .section-header, body.kb-printing .kb-foot,
  body.kb-printing .fb-trigger, body.kb-printing .fb-modal { display:none !important; }
  body.kb-printing .kb-print th { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  /* Force the print layout to page width. The desktop layout uses a
     280px sidebar + 1fr content grid; hiding the sidebar with display:
     none leaves .content in a 280px auto-placed slot. Collapse the
     grid entirely for print so content flows at full page width. */
  body.kb-printing .layout {
    display: block !important;
    grid-template-columns: none !important;
  }
  body.kb-printing { margin: 0; }
  body.kb-printing .content {
    padding: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
  }
  body.kb-printing #keeper-board { max-width: 100%; width: 100%; padding: 0; margin: 0; }
  body.kb-printing .kb-print { display:block; width: 100%; }
  body.kb-printing #keeper-board { display:block !important; }
  body.kb-printing .kb-print table.kb-print-full { table-layout: fixed; }
}
.kb-print h2 { font-size:18px; margin:0 0 2px; }
.kb-print .kb-print-sub { color:#606C71; font-size:12px; margin:0 0 12px; }
.kb-print table { width:100%; border-collapse:collapse; font-size:12px; }
.kb-print th { text-align:left; padding:5px 8px; background:#0D3A66; color:#fff; font-weight:700; font-size:10.5px; letter-spacing:0.04em; text-transform:uppercase; }
.kb-print td { padding:4px 8px; border-bottom:1px solid #ebebed; vertical-align:top; }
.kb-print .num { text-align:right; font-variant-numeric:tabular-nums; }
.kb-print .kb-print-flag { color:#8a6a12; font-size:10.5px; margin-right:6px; }
.kb-print .kb-print-picknum { color:#98a0ad; font-size:11px; font-weight:400; }
.kb-print .kb-print-chasm { color:#b42318; font-weight:700; }
/* Full-slot export: one row per pick, whether keeper, open, or traded. */
.kb-print .kb-print-full td.num:first-child { font-weight:700; color:#606C71; }
.kb-print .kb-print-name { font-weight:600; }
.kb-print .kb-print-notes { color:#606C71; font-size:10.5px; }
.kb-print .kb-print-note { color:#8e8e93; font-style:italic; font-size:11px; }
.kb-print tr.kb-print-open td { background:#f8faff; }
.kb-print tr.kb-print-open td.num:first-child { color:#1761A0; }
.kb-print tr.kb-print-gone td { background:#fdf3f2; }
.kb-print tr.kb-print-gone td.num:first-child { color:#b42318; text-decoration:line-through; }
.kb-print .kb-print-gone-note { color:#b42318; }
.kb-print .kb-print-chasm-h { font-size:13px; margin:16px 0 6px; color:#b42318; }
.kb-print .kb-print-legend { color:#606C71; font-size:11px; font-weight:400; }
.kb-print .kb-print-legend-item { white-space:nowrap; }
.kb-print .kb-print-legend-key { display:inline-block; padding:0 5px; font-weight:700; font-size:10px; border-radius:3px; margin-right:3px; background:#f0f0f2; color:#606C71; }
.kb-print .kb-print-legend-key.kb-print-legend-open { background:#e6efff; color:#1761A0; }
.kb-print .kb-print-legend-key.kb-print-legend-gone { background:#fdecea; color:#b42318; }

/* --- Off-season trades tab --------------------------------------------- */
.ot-list { display: flex; flex-direction: column; gap: 20px; max-width: 880px; }
.ot-card {
  border: 1px solid var(--gray-200);
  border-radius: 10px;
  background: #fff;
  overflow: hidden;
}
.ot-head {
  display: flex;
  align-items: baseline;
  gap: 14px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--gray-200);
  background: var(--gray-50);
}
.ot-date {
  font-size: 11px;
  font-weight: 600;
  color: var(--gray-600);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  white-space: nowrap;
}
.ot-teams { font-size: 15px; font-weight: 600; }
.ot-swap { color: var(--blue-600); font-weight: 400; padding: 0 2px; }
.ot-sides { display: grid; grid-template-columns: 1fr 1fr; }
.ot-side { padding: 16px 20px 18px; }
.ot-side + .ot-side { border-left: 1px solid var(--gray-200); }
.ot-side-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--gray-600);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.ot-player { padding: 10px 0 12px; }
.ot-player + .ot-player { border-top: 1px solid var(--gray-200); }
.ot-player-top { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.ot-player-name { font-weight: 600; font-size: 14.5px; }
.ot-player-meta { color: var(--gray-500); font-size: 12px; }
.ot-costline {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  margin-top: 8px;
  font-variant-numeric: tabular-nums;
}
.ot-cost-label {
  display: block;
  font-size: 10px;
  font-weight: 600;
  color: var(--gray-500);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 2px;
}
.ot-cost-was { color: var(--gray-600); font-size: 13px; }
.ot-cost-now .pill { font-size: 12px; }
.ot-arrow { color: var(--blue-400); font-size: 15px; padding-bottom: 2px; }
.ot-pick {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
  margin: 10px 8px 0 0;
  padding: 5px 10px;
  border: 1px dashed var(--blue-200);
  border-radius: 6px;
  background: #f4faff;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--blue-800);
}
.ot-pick-orig { font-weight: 400; color: var(--gray-600); font-size: 11.5px; }
.ot-none { color: var(--gray-500); font-size: 13px; padding: 8px 0; }
@media (max-width: 720px) {
  .ot-sides { grid-template-columns: 1fr; }
  .ot-side + .ot-side { border-left: none; border-top: 1px solid var(--gray-200); }
  .ot-head { flex-direction: column; gap: 2px; }
}
"""

JS = r"""
(function() {
  const links = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('.team-section');

  function updateCrumb(targetId) {
    const bar = document.querySelector('.crumb-bar');
    if (!bar) return;
    bar.classList.toggle('at-home', targetId === 'summary');
    const link = document.querySelector('.nav-link[data-target="' + targetId + '"]');
    let label = '';
    if (link) { const c = link.cloneNode(true); c.querySelectorAll('.draft-slot, .manager').forEach(n => n.remove()); label = (c.textContent || '').trim(); }
    const cur = bar.querySelector('.crumb-current');
    if (cur) cur.textContent = label;
  }

  function show(targetId) {
    sections.forEach(s => s.hidden = (s.id !== targetId));
    links.forEach(l => l.classList.toggle('active', l.dataset.target === targetId));
    updateCrumb(targetId);
    window.scrollTo({top: 0, behavior: 'instant'});
  }

  links.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      show(link.dataset.target);
    });
  });

  document.querySelectorAll('a[data-target]').forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      show(a.dataset.target);
    });
  });

  show('summary');

  const brandHome = document.querySelector('.brand-home');
  if (brandHome) brandHome.addEventListener('click', (e) => { e.preventDefault(); show('summary'); });
  document.querySelectorAll('.crumb-back').forEach(b => b.addEventListener('click', (e) => { e.preventDefault(); show('summary'); }));

  document.querySelectorAll('.draft-table tr.has-log').forEach(row => {
    row.addEventListener('click', (e) => {
      if (e.target.closest('a')) return;
      const id = row.dataset.logRow;
      const detail = id ? document.getElementById(id) : null;
      if (!detail) return;
      const chev = row.querySelector('.draft-log-toggle');
      if (detail.hasAttribute('hidden')) { detail.removeAttribute('hidden'); if (chev) chev.classList.add('open'); }
      else { detail.setAttribute('hidden', ''); if (chev) chev.classList.remove('open'); }
    });
  });

  document.querySelectorAll('.expand-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = btn.dataset.target;
      const row = document.getElementById(targetId);
      if (!row) return;
      const opening = row.hasAttribute('hidden');
      if (opening) {
        row.removeAttribute('hidden');
        btn.classList.add('open');
      } else {
        row.setAttribute('hidden', '');
        btn.classList.remove('open');
      }
    });
  });

  document.querySelectorAll('.tabs').forEach(tabsEl => {
    const buttons = tabsEl.querySelectorAll('.tab-btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const targetPanelId = btn.dataset.tab;
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const parentSection = tabsEl.closest('.team-section');
        if (!parentSection) return;
        parentSection.querySelectorAll('.tab-panel').forEach(panel => {
          if (panel.id === targetPanelId) {
            panel.removeAttribute('hidden');
            panel.classList.add('active');
          } else {
            panel.setAttribute('hidden', '');
            panel.classList.remove('active');
          }
        });
      });
    });
  });

  document.querySelectorAll('.year-collapsible-header').forEach(header => {
    header.addEventListener('click', (e) => {
      e.preventDefault();
      const block = header.closest('.year-collapsible');
      if (!block) return;
      block.classList.toggle('open');
    });
  });

  // Commissioner's Desk: switch between posts in the right pane.
  // Uses data-desk-target (not data-target) to avoid being captured by the
  // top-level a[data-target] handler that swaps team-sections.
  // Intentionally does NOT scroll — the user stays at their current scroll
  // position so the section header remains in view.
  document.querySelectorAll('.desk-post-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const target = link.dataset.deskTarget;
      document.querySelectorAll('.desk-post-link').forEach(l => l.classList.toggle('desk-active', l === link));
      document.querySelectorAll('.desk-post').forEach(p => {
        if (p.id === target) p.removeAttribute('hidden');
        else p.setAttribute('hidden', '');
      });
    });
  });

  // Player-search filter
  const psInput = document.getElementById('player-search-input');
  if (psInput) {
    const cards = document.querySelectorAll('#ps-results .player-card');
    const emptyState = document.getElementById('ps-empty');
    const noResults = document.getElementById('ps-no-results');
    const suggestions = document.getElementById('ps-suggestions');
    function hideAllCards() { cards.forEach(c => c.hidden = true); }
    function selectPlayerByCard(card) {
      hideAllCards();
      card.hidden = false;
      suggestions.hidden = true;
      psInput.value = card.dataset.displayName || '';
      if (emptyState) emptyState.hidden = true;
      if (noResults) noResults.hidden = true;
      card.scrollIntoView({ behavior: 'instant', block: 'start' });
    }
    psInput.addEventListener('input', () => {
      const q = psInput.value.trim().toLowerCase();
      hideAllCards();
      if (q.length < 2) {
        suggestions.hidden = true;
        suggestions.innerHTML = '';
        if (emptyState) emptyState.hidden = false;
        if (noResults) noResults.hidden = true;
        return;
      }
      if (emptyState) emptyState.hidden = true;
      // Build matches list (cap at 25 to keep dropdown manageable)
      const matches = [];
      for (const c of cards) {
        if (c.dataset.name.includes(q)) {
          matches.push(c);
          if (matches.length >= 25) break;
        }
      }
      suggestions.innerHTML = '';
      if (matches.length === 0) {
        suggestions.hidden = true;
        if (noResults) noResults.hidden = false;
        return;
      }
      if (noResults) noResults.hidden = true;
      for (const card of matches) {
        const item = document.createElement('a');
        item.className = 'ps-suggestion';
        item.href = '#';
        item.textContent = card.dataset.displayName || card.dataset.name;
        item.addEventListener('click', (e) => {
          e.preventDefault();
          selectPlayerByCard(card);
        });
        suggestions.appendChild(item);
      }
      suggestions.hidden = false;
    });
    // Enter key picks the top suggestion
    psInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const first = suggestions.querySelector('.ps-suggestion');
        if (first) first.click();
      } else if (e.key === 'Escape') {
        suggestions.hidden = true;
        psInput.blur();
      }
    });
    // Reset state if the user navigates to the page
    const psLink = document.querySelector('.nav-link[data-target="player-search"]');
    if (psLink) {
      psLink.addEventListener('click', () => {
        psInput.value = "";
        cards.forEach(c => c.hidden = true);
        if (emptyState) emptyState.hidden = false;
        if (noResults) noResults.hidden = true;
        setTimeout(() => psInput.focus(), 100);
      });
    }
  }

  // Mobile sidebar toggle
  const menuToggle = document.querySelector('.menu-toggle');
  const sidebarTab = document.querySelector('.sidebar-tab');
  if (sidebarTab) {
    sidebarTab.addEventListener('click', () => {
      document.body.classList.toggle('sidebar-open');
    });
  }
  const sidebar = document.querySelector('.sidebar');
  const backdrop = document.querySelector('.sidebar-backdrop');
  function closeSidebar() {
    document.body.classList.remove('sidebar-open');
  }
  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', () => {
      document.body.classList.toggle('sidebar-open');
    });
    if (backdrop) backdrop.addEventListener('click', closeSidebar);
    sidebar.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', closeSidebar);
    });
  }

  // Feedback widget: open/close modal + mailto: submit handler
  const fbTrigger = document.getElementById('fb-trigger');
  const fbOverlay = document.getElementById('fb-overlay');
  const fbModal = document.getElementById('fb-modal');
  const fbClose = document.getElementById('fb-close');
  const fbCancel = document.getElementById('fb-cancel');
  const fbForm = document.getElementById('fb-form');
  function fbOpen() {
    document.body.classList.remove('sidebar-open');   // close the phone drawer first
    if (fbOverlay) fbOverlay.hidden = false;
    if (fbModal) fbModal.hidden = false;
    const nameInput = document.getElementById('fb-name');
    if (nameInput) setTimeout(() => nameInput.focus(), 50);
  }
  function fbCloseModal() {
    if (fbOverlay) fbOverlay.hidden = true;
    if (fbModal) fbModal.hidden = true;
  }
  if (fbTrigger) fbTrigger.addEventListener('click', fbOpen);
  if (fbClose) fbClose.addEventListener('click', fbCloseModal);
  if (fbCancel) fbCancel.addEventListener('click', fbCloseModal);
  if (fbOverlay) fbOverlay.addEventListener('click', fbCloseModal);
  if (fbForm) {
    fbForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = (document.getElementById('fb-name').value || '').trim();
      const message = (document.getElementById('fb-message').value || '').trim();
      if (!name || !message) return;
      const subject = encodeURIComponent('We Graduated site feedback from ' + name);
      const body = encodeURIComponent('From: ' + name + '\n\n' + message + '\n\n---\nSent via the We Graduated site feedback widget.');
      window.location.href = 'mailto:hodorpete@gmail.com?subject=' + subject + '&body=' + body;
      fbCloseModal();
    });
  }
})();

"""

FEEDBACK = """
    <div class="fb-overlay" id="fb-overlay" hidden></div>
    <div class="fb-modal" id="fb-modal" role="dialog" aria-labelledby="fb-title" hidden>
      <header class="fb-modal-header">
        <h2 id="fb-title" class="fb-modal-title">Send feedback to Pete</h2>
        <button class="fb-close" id="fb-close" type="button" aria-label="Close">&times;</button>
      </header>
      <p class="fb-modal-sub">Spotted something wrong? Have a question, suggestion, or rant? Drop it in.</p>
      <form id="fb-form" class="fb-form">
        <label class="fb-label">
          <span class="fb-field-label">Your name</span>
          <input type="text" name="name" id="fb-name" required placeholder="Who's asking?" autocomplete="name">
        </label>
        <label class="fb-label">
          <span class="fb-field-label">Message</span>
          <textarea name="message" id="fb-message" rows="6" required placeholder="What's on your mind?"></textarea>
        </label>
        <div class="fb-actions">
          <button type="button" class="fb-btn fb-btn-secondary" id="fb-cancel">Cancel</button>
          <button type="submit" class="fb-btn fb-btn-primary">Send</button>
        </div>
        <p class="fb-modal-foot">Submitting will open your email app with the message pre-filled. Hit send there to deliver it.</p>
      </form>
    </div>"""
