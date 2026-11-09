"""
wg_charts.py - inline SVG charts for the We Graduated site. No libraries:
each function returns an SVG/HTML string; one shared tooltip script
(CHART_JS) reads data-tip attributes. Light theme only, like the site.

Color roles (validated: brand blue vs red passes CVD and contrast on white):
  --c-accent  #1761A0  the highlighted / single series (Mike's logo blue)
  --c-neg     #e34948  negative pole (diverging)
  --c-muted   #c5c9d2  background series
  --c-grid    #ebebed  gridlines
Text always uses text tokens, never a series color.
"""

import html

ACCENT, NEG, MUTED, GRID = "#1761A0", "#e34948", "#c5c9d2", "#ebebed"
INK, INK2, INK3 = "#1d1d1f", "#606C71", "#8e8e93"
e = lambda s: html.escape(str(s), quote=True)

CHART_CSS = """
.viz { margin: 8px 0 24px; }
.viz svg { width: 100%; height: auto; display: block; overflow: visible; }
.viz-title { font-size: 13px; font-weight: 600; color: #2a2a2e; margin: 0 0 2px; }
.viz-sub { font-size: 12px; color: #8e8e93; margin: 0 0 10px; }
.viz text { font-family: inherit; }
.viz-pills { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 10px; }
.viz-pill { border: 1px solid #d8d8dc; background: #fff; border-radius: 999px; padding: 3px 10px; font-size: 12px; cursor: pointer; color: #2a2a2e; }
.viz-pill.on { background: #1761A0; border-color: #1761A0; color: #fff; }
.viz .ln { fill: none; stroke: #c5c9d2; stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; transition: stroke .12s; }
.viz .ln.hl { stroke: #1761A0; stroke-width: 2.5; }
.viz .ln-hit { fill: none; stroke: transparent; stroke-width: 12; cursor: pointer; }
.viz .lbl { font-size: 11px; fill: #8e8e93; }
.viz .lbl.hl { fill: #1d1d1f; font-weight: 600; }
.viz-tip { position: fixed; z-index: 50; pointer-events: none; background: #1d1d1f; color: #fff; font-size: 12px; line-height: 1.4;
  padding: 6px 9px; border-radius: 6px; max-width: 260px; opacity: 0; transition: opacity .08s; }
.viz-tip.on { opacity: 1; }
.viz-legend { display: flex; gap: 14px; font-size: 12px; color: #606C71; margin: 4px 0 0; flex-wrap: wrap; }
.viz .dt { fill: #c5c9d2; opacity: .75; cursor: pointer; }
.viz .dt.hl { fill: #1761A0; opacity: 1; stroke: #fff; stroke-width: 1.5; }
.viz-grid2 { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 8px 28px; }
.viz-grid2 > *, .viz { min-width: 0; }
@media (max-width: 860px) { .viz-grid2 { grid-template-columns: minmax(0, 1fr); } }
.viz-legend i { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 5px; vertical-align: -1px; }
/* Phones: a 760-wide chart squeezed to ~340px puts labels at 5px. Keep charts at a
   readable minimum width and let them scroll sideways instead; a fade on the right
   edge says there is more. */
@media (max-width: 720px) {
  .viz-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; margin: 0 -2px; }
  .viz-scroll > svg { min-width: 620px; }
  .viz-scroll.viz-narrow > svg { min-width: 440px; }
  .viz-legend { font-size: 11.5px; gap: 4px 12px; }
  .viz-sub { font-size: 12px; }
  .viz-pills { gap: 5px; }
  .viz-pill { padding: 4px 10px; }
  .viz-tip { max-width: 240px; }
}
.hb { display: flex; flex-direction: column; gap: 3px; margin: 6px 0 4px; font-size: 12.5px; }
.hb-row { display: grid; grid-template-columns: 76px 1fr; align-items: center; gap: 8px; min-height: 22px; cursor: default; border-radius: 4px; }
.hb-wide .hb-row { grid-template-columns: 150px 1fr; }
.hb-row:hover { background: #f5f6f8; }
.hb-row.hb-div { grid-template-columns: 76px 1fr 1fr; gap: 0 8px; }
.hb-lab { text-align: right; color: #1d1d1f; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.hb-track, .hb-half { display: flex; align-items: center; gap: 6px; min-width: 0; }
.hb-neg { flex-direction: row-reverse; border-right: 1px solid #8e8e93; padding-right: 0; min-height: 22px; }
.hb-pos { margin-left: -8px; }
.hb-bar { display: block; height: 14px; border-radius: 0 4px 4px 0; min-width: 1px; }
.hb-neg .hb-bar { border-radius: 4px 0 0 4px; }
.hb-stack { display: flex; height: 14px; }
.hb-seg { display: block; height: 14px; border-right: 1.5px solid #fff; }
.hb-track { gap: 0; }
.hb-track .hb-val { margin-left: 6px; }
.hb-seg:last-of-type { border-right: 0; border-radius: 0 4px 4px 0; }
.hb-val { font-size: 11.5px; color: #606C71; white-space: nowrap; font-variant-numeric: tabular-nums; }
@media (max-width: 720px) { .hb-wide .hb-row { grid-template-columns: 118px 1fr; } .hb { font-size: 12px; } }
.more-right { -webkit-mask-image: linear-gradient(to right, #000 calc(100% - 40px), rgba(0,0,0,.15));
              mask-image: linear-gradient(to right, #000 calc(100% - 40px), rgba(0,0,0,.15)); }
.more-left { -webkit-mask-image: linear-gradient(to left, #000 calc(100% - 40px), rgba(0,0,0,.15));
             mask-image: linear-gradient(to left, #000 calc(100% - 40px), rgba(0,0,0,.15)); }
.more-left.more-right { -webkit-mask-image: linear-gradient(to right, rgba(0,0,0,.15), #000 40px, #000 calc(100% - 40px), rgba(0,0,0,.15));
                        mask-image: linear-gradient(to right, rgba(0,0,0,.15), #000 40px, #000 calc(100% - 40px), rgba(0,0,0,.15)); }
.swipe-hint { display: none; font-size: 11px; color: #8e8e93; margin: 2px 0 0; }
@media (max-width: 720px) { .swipe-hint.on { display: block; } }
"""

CHART_JS = r"""
(function(){
  const tip = document.createElement('div'); tip.className = 'viz-tip'; document.body.appendChild(tip);
  function showTip(ev) {
    const t = ev.target.closest && ev.target.closest('[data-tip]');
    if (!t) { tip.classList.remove('on'); return; }
    tip.innerHTML = t.getAttribute('data-tip');
    tip.classList.add('on');
    const x = Math.max(8, Math.min(ev.clientX + 14, window.innerWidth - tip.offsetWidth - 8));
    let y = ev.clientY + 14;
    if (y + tip.offsetHeight > window.innerHeight - 8) y = Math.max(8, ev.clientY - tip.offsetHeight - 14);
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  document.addEventListener('mousemove', showTip);
  document.addEventListener('click', showTip);          // tap to see a tooltip on phones
  document.addEventListener('scroll', () => tip.classList.remove('on'), true);
  // Wrap every chart's SVG in a sideways scroller (only active on phones), including
  // charts drawn later by the season pickers.
  function wrapCharts(root) {
    (root || document).querySelectorAll('.viz > svg').forEach(sv => {
      const w = document.createElement('div');
      const vb = sv.viewBox && sv.viewBox.baseVal;
      w.className = 'viz-scroll' + (vb && vb.width && vb.width <= 560 ? ' viz-narrow' : '');
      sv.parentNode.insertBefore(w, sv); w.appendChild(sv);
      if (sv.closest('.viz').dataset.end) w.dataset.end = '1';
    });
    (root || document).querySelectorAll('.viz-scroll[data-end]').forEach(w => {
      if (!w.dataset.done && w.offsetParent && w.scrollWidth > w.clientWidth + 4) { w.scrollLeft = w.scrollWidth; w.dataset.done = '1'; }
    });
  }
  // Fade the right edge of anything that scrolls sideways until you reach its end.
  function cue() {
    document.querySelectorAll('.viz-scroll, .content table, .table-scroll').forEach(el => {
      if (!el.offsetParent) return;
      const more = el.scrollWidth > el.clientWidth + 4 && el.scrollLeft + el.clientWidth < el.scrollWidth - 4;
      el.classList.toggle('more-right', more);
      el.classList.toggle('more-left', el.scrollLeft > 4);
      if (el.classList.contains('viz-scroll')) {
        let h = el.nextElementSibling;
        if (!h || !h.classList.contains('swipe-hint')) { h = document.createElement('div'); h.className = 'swipe-hint'; h.textContent = 'Swipe sideways to see the whole chart'; el.after(h); }
        h.classList.toggle('on', el.scrollWidth > el.clientWidth + 4);
      }
    });
  }
  window.wgCharts = { wrap: wrapCharts, cue: cue };
  wrapCharts();
  document.addEventListener('scroll', ev => { if (ev.target.classList) { const el = ev.target;
    if (el.matches('.viz-scroll, .content table, .table-scroll')) { el.classList.toggle('more-right', el.scrollLeft + el.clientWidth < el.scrollWidth - 4); el.classList.toggle('more-left', el.scrollLeft > 4); } } }, true);
  ['click', 'change'].forEach(evn => document.addEventListener(evn, () => setTimeout(() => { wrapCharts(); cue(); }, 60)));
  window.addEventListener('resize', cue);
  setTimeout(() => { wrapCharts(); cue(); }, 100);
  // multi-line highlight: pills + hovering a line
  document.querySelectorAll('.viz[data-hl]').forEach(v => {
    const set = m => {
      v.querySelectorAll('[data-m]').forEach(el => el.classList.toggle('hl', el.dataset.m === m));
      v.querySelectorAll('.ln.hl').forEach(el => el.parentNode.insertBefore(el, v.querySelector('.ln-hit')));
      v.querySelectorAll('.dt.hl').forEach(el => el.parentNode.appendChild(el));
      v.querySelectorAll('.viz-pill').forEach(p => p.classList.toggle('on', p.dataset.m === m));
      v.dataset.cur = m;
    };
    set(v.dataset.hl);
    v.querySelectorAll('.viz-pill').forEach(p => p.addEventListener('click', () => set(p.dataset.m)));
    v.querySelectorAll('[data-hm]').forEach(h => {
      h.addEventListener('mouseenter', () => set(h.dataset.hm));
      h.addEventListener('click', () => set(h.dataset.hm));
    });
  });
})();
"""


def _wrap(svg, title, sub="", extra="", attrs=""):
    t = f'<div class="viz-title">{e(title)}</div>' if title else ""
    s = f'<div class="viz-sub">{e(sub)}</div>' if sub else ""
    return f'<div class="viz"{attrs}>{t}{s}{extra}{svg}</div>'


def _nice_max(v, step):
    return max(step, int((v + step - 1) // step * step))


def multi_line(series, xs, title, sub, ylabel_fmt="{:g}", default=None, step=None):
    """series: {name: [y or None per x]}. Gray lines; one highlighted (pills + hover)."""
    W, H, L, R, T, B = 760, 340, 40, 70, 12, 28
    ymax_raw = max(v for ys in series.values() for v in ys if v is not None)
    step = step or (25 if ymax_raw > 100 else 10 if ymax_raw > 30 else 5)
    ymax = _nice_max(ymax_raw, step)
    px = lambda i: L + i * (W - L - R) / max(len(xs) - 1, 1)
    py = lambda v: T + (H - T - B) * (1 - v / ymax)
    g = "".join(f'<line x1="{L}" x2="{W - R}" y1="{py(v):.1f}" y2="{py(v):.1f}" stroke="{GRID}" stroke-width="1"/>'
                f'<text x="{L - 6}" y="{py(v) + 4:.1f}" text-anchor="end" font-size="11" fill="{INK3}">{ylabel_fmt.format(v)}</text>'
                for v in range(0, ymax + 1, step))
    g += "".join(f'<text x="{px(i):.1f}" y="{H - 8}" text-anchor="middle" font-size="11" fill="{INK3}">{e(x)}</text>'
                 for i, x in enumerate(xs) if len(xs) < 12 or i % 2 == 0 or i == len(xs) - 1)
    lines = hits = labels = dots = ""
    order = sorted(series, key=lambda n: (series[n][-1] or 0))
    for name in order:
        ys = series[name]
        pts = [(px(i), py(v), xs[i], v) for i, v in enumerate(ys) if v is not None]
        if not pts:
            continue
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in pts)
        lines += f'<path class="ln" data-m="{e(name)}" d="{d}"/>'
        tipd = f'<b>{e(name)}</b><br>' + " &middot; ".join(f"{xx}: {ylabel_fmt.format(vv)}" for _, _, xx, vv in pts[-4:])
        hits += f'<path class="ln-hit" data-hm="{e(name)}" data-tip="{e(tipd)}" d="{d}"/>'
        x, y = pts[-1][0], pts[-1][1]
        labels += f'<text class="lbl" data-m="{e(name)}" x="{x + 6:.1f}" y="{y + 4:.1f}">{e(name)}</text>'
    # nudge end labels apart (simple greedy, bottom-up)
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}">{g}{lines}{hits}'
           f'<g class="end-labels">{_declutter(labels)}</g></svg>')
    pills = '<div class="viz-pills">' + "".join(
        f'<button type="button" class="viz-pill" data-m="{e(n)}">{e(n)}</button>' for n in sorted(series)) + "</div>"
    return _wrap(svg, title, sub, pills, f' data-hl="{e(default or order[-1])}"')


def _declutter(labels_svg, gap=12):
    import re
    items = re.findall(r'(<text class="lbl" data-m="[^"]*" x="([\d.]+)" y="([\d.]+)">[^<]*</text>)', labels_svg)
    items = sorted(((float(y), full, x) for full, x, y in items), key=lambda t: t[0])
    out, last = [], -1e9
    for y, full, x in items:
        ny = max(y, last + gap)
        out.append(full.replace(f'y="{y:.1f}"', f'y="{ny:.1f}"', 1) if f'y="{y:.1f}"' in full else full)
        last = ny
    return "".join(out)


def scatter_luck(points, title, sub):
    """points: [(name, expected, actual)]. Diagonal = fair."""
    W, H, L, R, T, B = 560, 400, 40, 20, 12, 40
    vmax = max(max(p[1], p[2]) for p in points) + 1
    vmax = int(vmax + 0.999)
    px = lambda v: L + (W - L - R) * v / vmax
    py = lambda v: T + (H - T - B) * (1 - v / vmax)
    g = ""
    for v in range(0, vmax + 1, 1 if vmax <= 10 else 2):
        g += (f'<line x1="{L}" x2="{W - R}" y1="{py(v):.1f}" y2="{py(v):.1f}" stroke="{GRID}"/>'
              f'<text x="{L - 6}" y="{py(v) + 4:.1f}" text-anchor="end" font-size="11" fill="{INK3}">{v}</text>'
              f'<text x="{px(v):.1f}" y="{H - 22}" text-anchor="middle" font-size="11" fill="{INK3}">{v}</text>')
    g += f'<line x1="{px(0)}" y1="{py(0)}" x2="{px(vmax)}" y2="{py(vmax)}" stroke="{INK3}" stroke-width="1"/>'
    g += (f'<text x="{px(vmax * 0.18):.1f}" y="{py(vmax * 0.92):.1f}" font-size="11" fill="{INK2}">Luckier: more wins than scores earned</text>'
          f'<text x="{px(vmax * 0.98):.1f}" y="{py(vmax * 0.06):.1f}" text-anchor="end" font-size="11" fill="{INK2}">Unluckier</text>'
          f'<text x="{(L + W - R) / 2}" y="{H - 4}" text-anchor="middle" font-size="11" fill="{INK2}">Expected wins</text>'
          f'<text x="12" y="{(T + H - B) / 2}" font-size="11" fill="{INK2}" transform="rotate(-90 12 {(T + H - B) / 2})" text-anchor="middle">Actual wins</text>')
    dots = labels = ""
    placed = []
    for name, xw, w in sorted(points, key=lambda p: p[1]):
        x, y = px(xw), py(w)
        d = w - xw
        col = ACCENT if d >= 0 else NEG
        tipd = f"<b>{e(name)}</b><br>{w:g} wins, {xw:.1f} expected ({d:+.1f})"
        dots += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{col}" stroke="#fff" stroke-width="2" data-tip="{e(tipd)}"/>'
                 f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="transparent" data-tip="{e(tipd)}"/>')
        ly = y - 10
        while any(abs(ly - py_) < 12 and abs(x - px_) < 46 for px_, py_ in placed):
            ly -= 12
        placed.append((x, ly))
        labels += f'<text x="{x:.1f}" y="{ly:.1f}" text-anchor="middle" font-size="11" fill="{INK}">{e(name)}</text>'
    svg = f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}">{g}{dots}{labels}</svg>'
    leg = (f'<div class="viz-legend"><span><i style="background:{ACCENT}"></i>Won more than expected</span>'
           f'<span><i style="background:{NEG}"></i>Won fewer than expected</span></div>')
    return _wrap(svg + leg, title, sub)


def diverging_bars(rows, title, sub, fmt="{:+.1f}", tips=None):
    """rows: [(label, value)] sorted as given. HTML bars either side of zero,
    so labels stay at real font size on any screen width."""
    vmax = max((abs(v) for _, v in rows), default=1) or 1
    out = ""
    for i, (lab, v) in enumerate(rows):
        f = abs(v) / vmax
        tipd = tips[i] if tips else f"<b>{e(lab)}</b><br>{fmt.format(v)}"
        bar = f'<span class="hb-bar" style="width:calc((100% - 46px) * {f:.4f});background:{ACCENT if v >= 0 else NEG}"></span><span class="hb-val">{fmt.format(v)}</span>'
        neg, pos = ("", bar) if v >= 0 else (bar, "")
        out += (f'<div class="hb-row hb-div" data-tip="{e(tipd)}"><span class="hb-lab">{e(lab)}</span>'
                f'<span class="hb-half hb-neg">{neg}</span><span class="hb-half hb-pos">{pos}</span></div>')
    return _wrap(f'<div class="hb" role="img" aria-label="{e(title)}">{out}</div>', title, sub)


def _hbar(x, y, w, h, col, right=True):
    """Horizontal bar, 4px rounded data end, square at the baseline."""
    r = min(4, w / 2, h / 2)
    if right:
        d = (f"M{x:.1f},{y:.1f} h{w - r:.1f} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r:.1f} a{r},{r} 0 0 1 -{r},{r} "
             f"h-{w - r:.1f} z")
    else:
        d = (f"M{x + w:.1f},{y:.1f} h-{w - r:.1f} a{r},{r} 0 0 0 -{r},{r} v{h - 2 * r:.1f} a{r},{r} 0 0 0 {r},{r} "
             f"h{w - r:.1f} z")
    return f'<path d="{d}" fill="{col}"/>'


def _mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def heatmap(rows, cols, title, sub, cell_fmt="{:,.0f}"):
    """rows: [(label, {col: (value, pct_vs_avg)})]. Diverging fill on pct (blue above, red below, gray mid)."""
    cw, rh, L, T = 78, 30, 86, 26
    W = L + cw * len(cols) + 4
    H = T + rh * len(rows) + 4
    mid = "#f0efec"
    out = "".join(f'<text x="{L + cw * j + cw / 2}" y="16" text-anchor="middle" font-size="11" fill="{INK3}">{e(c)}</text>'
                  for j, c in enumerate(cols))
    for i, (lab, vals) in enumerate(rows):
        y = T + i * rh
        out += f'<text x="{L - 8}" y="{y + 19}" text-anchor="end" font-size="12" fill="{INK}">{e(lab)}</text>'
        for j, c in enumerate(cols):
            v, p = vals.get(c, (0, 0))
            t = max(-1, min(1, p / 0.35))   # +-35% vs average = full color
            fill = _mix(mid, "#86b6ef", t) if t >= 0 else _mix(mid, "#f2a3a3", -t)
            tipd = f"<b>{e(lab)}, {e(c)}</b><br>{cell_fmt.format(v)} pts ({p:+.0%} vs avg)"
            out += (f'<rect x="{L + cw * j + 1}" y="{y + 1}" width="{cw - 2}" height="{rh - 2}" rx="3" fill="{fill}" data-tip="{e(tipd)}"/>'
                    f'<text x="{L + cw * j + cw / 2}" y="{y + 19}" text-anchor="middle" font-size="11.5" fill="{INK}" pointer-events="none">{cell_fmt.format(v)}</text>')
    leg = (f'<div class="viz-legend"><span><i style="background:#86b6ef"></i>Above league average</span>'
           f'<span><i style="background:{mid};border:1px solid #ddd"></i>About average</span>'
           f'<span><i style="background:#f2a3a3"></i>Below league average</span></div>')
    return _wrap(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}">{out}</svg>' + leg, title, sub)


def timeline(rows, years, title, sub):
    """rows: [(label, start, end, active, tip)]. One bar per row across years."""
    rh, L, R, T = 24, 200, 16, 22
    W = 760
    H = T + rh * len(rows) + 6
    span = years[-1] - years[0] + 1
    cw = (W - L - R) / span
    px = lambda yr: L + (yr - years[0]) * cw
    out = ""
    for yr in years:
        if (yr - years[0]) % 2 == 0 or yr == years[-1]:
            out += f'<text x="{px(yr) + cw / 2:.1f}" y="14" text-anchor="middle" font-size="11" fill="{INK3}">{str(yr)[2:]}</text>'
        out += f'<line x1="{px(yr):.1f}" x2="{px(yr):.1f}" y1="{T}" y2="{H}" stroke="{GRID}"/>'
    for i, (lab, s, en, active, tipd) in enumerate(rows):
        y = T + i * rh
        x, w = px(s) + 1, (en - s + 1) * cw - 2
        col = ACCENT if active else "#86b6ef"
        out += (f'<text x="{L - 8}" y="{y + 16}" text-anchor="end" font-size="12" fill="{INK}">{e(lab)}</text>'
                f'<g data-tip="{e(tipd)}">{_hbar(x, y + 5, w, 14, col)}<rect x="{L}" y="{y}" width="{W - L - R}" height="{rh}" fill="transparent"/></g>')
    leg = (f'<div class="viz-legend"><span><i style="background:{ACCENT}"></i>Still being kept ({years[-1]})</span>'
           f'<span><i style="background:#86b6ef"></i>Streak ended</span></div>')
    return _wrap(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}">{out}</svg>' + leg, title, sub)


def finish_line(points, n_teams, title, sub):
    """points: [(year, finish or None, note)]. Rank 1 at top."""
    W, H, L, R, T, B = 640, 210, 34, 16, 14, 26
    xs = [p[0] for p in points]
    px = lambda i: L + i * (W - L - R) / max(len(xs) - 1, 1)
    py = lambda r: T + (H - T - B) * (r - 1) / (n_teams - 1)
    g = ""
    for r in (1, 4, 6, 9, 12):
        g += (f'<line x1="{L}" x2="{W - R}" y1="{py(r):.1f}" y2="{py(r):.1f}" stroke="{GRID}"/>'
              f'<text x="{L - 6}" y="{py(r) + 4:.1f}" text-anchor="end" font-size="11" fill="{INK3}">{r}</text>')
    g += f'<rect x="{L}" y="{py(1) - 4:.1f}" width="{W - L - R}" height="{py(6) - py(1) + 8:.1f}" fill="#1761A0" opacity="0.05"/>'
    g += f'<text x="{W - R}" y="{py(6) + 16:.1f}" text-anchor="end" font-size="10.5" fill="{INK3}">playoff line</text>'
    g += "".join(f'<text x="{px(i):.1f}" y="{H - 6}" text-anchor="middle" font-size="11" fill="{INK3}">{str(x)[2:]}</text>'
                 for i, x in enumerate(xs))
    pts = [(px(i), py(r), x, r, note) for i, (x, r, note) in enumerate(points) if r]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y, *_ in pts) if pts else ""
    line = f'<path d="{d}" fill="none" stroke="{ACCENT}" stroke-width="2" stroke-linejoin="round"/>' if pts else ""
    dots = ""
    for x, y, yr, r, note in pts:
        tipd = f"<b>{yr}</b>: finished {r}" + (f" &middot; {e(note)}" if note else "")
        dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{6 if r == 1 else 4.5}" fill="{ACCENT}" stroke="#fff" stroke-width="2" data-tip="{e(tipd)}"/>'
        if r == 1:
            dots += f'<text x="{x:.1f}" y="{y - 10:.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{INK}">Champ</text>'
    return _wrap(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}">{g}{line}{dots}</svg>', title, sub)


# ----------------------------------------------------------- added 2026-11-09
BLUES = ["#0D3A66", "#2f78c0", "#7fb2e8", "#c9e0f7"]   # ordinal ramp, darkest = best


def _vbar(x, y0, w, h, col, up=True):
    """Vertical bar with 4px rounded data end, square at the baseline."""
    h = max(h, 0.5)
    r = min(4, w / 2, h / 2)
    if up:
        d = f"M{x:.1f},{y0:.1f} v-{h - r:.1f} a{r},{r} 0 0 1 {r},-{r} h{w - 2 * r:.1f} a{r},{r} 0 0 1 {r},{r} v{h - r:.1f} z"
    else:
        d = f"M{x:.1f},{y0:.1f} v{h - r:.1f} a{r},{r} 0 0 0 {r},{r} h{w - 2 * r:.1f} a{r},{r} 0 0 0 {r},-{r} v-{h - r:.1f} z"
    return f'<path d="{d}" fill="{col}"/>'


def _ticks(lo, hi, n=5):
    span = hi - lo or 1
    raw = span / n
    mag = 10 ** len(str(int(raw))) / 10 if raw >= 1 else 0.1
    step = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw), default=mag * 10)
    v = (lo // step) * step
    out = [round(v, 6)]
    while out[-1] < hi - 1e-9:
        v += step
        out.append(round(v, 6))
    return out


def vbars(cats, vals, title, sub, fmt="{:,.0f}", tips=None, colors=None, ref=None, height=240, label_every=1, show_vals=None, W=760):
    """Vertical columns. Negative values hang below zero in NEG. ref=(label, value) draws a dashed line."""
    H, Lm, R, T, B = height, 44, 12, 14, 26
    lo, hi = min(0, min(vals)), max(0, max(vals))
    if ref:
        hi = max(hi, ref[1]); lo = min(lo, ref[1])
    ticks = _ticks(lo, hi)
    lo, hi = min(lo, ticks[0]), max(hi, ticks[-1])
    py = lambda v: T + (H - T - B) * (hi - v) / ((hi - lo) or 1)
    n = len(cats)
    slot = (W - Lm - R) / n
    bw = min(46, slot * 0.68)
    show_vals = (n <= 16) if show_vals is None else show_vals
    out = "".join(f'<line x1="{Lm}" x2="{W - R}" y1="{py(t):.1f}" y2="{py(t):.1f}" stroke="{GRID}"/>'
                  f'<text x="{Lm - 6}" y="{py(t) + 4:.1f}" text-anchor="end" font-size="11" fill="{INK3}">{fmt.format(t)}</text>'
                  for t in ticks)
    for i, (c, v) in enumerate(zip(cats, vals)):
        x = Lm + slot * i + (slot - bw) / 2
        col = (colors[i] if colors else (ACCENT if v >= 0 else NEG))
        y0 = py(0)
        bar = _vbar(x, y0, bw, abs(py(v) - y0), col, up=v >= 0)
        tipd = tips[i] if tips else f"<b>{e(c)}</b><br>{fmt.format(v)}"
        out += f'<g data-tip="{e(tipd)}">{bar}<rect x="{Lm + slot * i:.1f}" y="{T}" width="{slot:.1f}" height="{H - T - B}" fill="transparent"/></g>'
        if show_vals and (W > 600 or n <= 12):
            ty = py(v) - 5 if v >= 0 else py(v) + 13
            out += f'<text x="{x + bw / 2:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="10.5" fill="{INK2}" pointer-events="none">{fmt.format(v)}</text>'
        if i % label_every == 0 or i == n - 1:
            out += f'<text x="{x + bw / 2:.1f}" y="{H - 8}" text-anchor="middle" font-size="11" fill="{INK3}">{e(c)}</text>'
    out += f'<line x1="{Lm}" x2="{W - R}" y1="{py(0):.1f}" y2="{py(0):.1f}" stroke="{INK3}"/>'
    if ref:
        out += (f'<line x1="{Lm}" x2="{W - R}" y1="{py(ref[1]):.1f}" y2="{py(ref[1]):.1f}" stroke="{INK}" stroke-dasharray="4 3"/>'
                f'<text x="{W - R}" y="{py(ref[1]) - 5:.1f}" text-anchor="end" font-size="10.5" fill="{INK}">{e(ref[0])}</text>')
    return _wrap(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}">{out}</svg>', title, sub)


def hbars(rows, title, sub, fmt="{:,.0f}", color=ACCENT, lw=None, W=None):
    """rows: [(label, value, tip or None)] in display order, values >= 0. HTML bars."""
    vmax = max((v for _, v, _ in rows), default=1) or 1
    out = ""
    for lab, v, tip in rows:
        tipd = tip or f"<b>{e(lab)}</b><br>{fmt.format(v)}"
        out += (f'<div class="hb-row" data-tip="{e(tipd)}"><span class="hb-lab">{e(lab)}</span><span class="hb-track">'
                f'<span class="hb-bar" style="width:calc((100% - 52px) * {v / vmax:.4f});background:{color}"></span>'
                f'<span class="hb-val">{fmt.format(v)}</span></span></div>')
    wide = " hb-wide" if max((len(str(r[0])) for r in rows), default=0) > 9 else ""
    return _wrap(f'<div class="hb{wide}" role="img" aria-label="{e(title)}">{out}</div>', title, sub)


def stacked_hbars(rows, segs, title, sub, lw=None, W=None, show_total=True):
    """rows: [(label, [v per seg], tip)]; segs: [(name, color)]. HTML stacked bars."""
    vmax = max((sum(v) for _, v, _ in rows), default=1) or 1
    out = ""
    for lab, vs, tip in rows:
        parts = "".join(f'<span class="hb-seg" style="width:calc((100% - 44px) * {v / vmax:.4f});background:{segs[j][1]}"></span>'
                        for j, v in enumerate(vs) if v)
        tot = f'<span class="hb-val">{sum(vs):g}</span>' if show_total else ""
        out += (f'<div class="hb-row" data-tip="{e(tip)}"><span class="hb-lab">{e(lab)}</span><span class="hb-track">'
                f'{parts}{tot}</span></div>')
    leg = '<div class="viz-legend">' + "".join(f'<span><i style="background:{c}"></i>{e(n)}</span>' for n, c in segs) + "</div>"
    return _wrap(f'<div class="hb" role="img" aria-label="{e(title)}">{out}</div>' + leg, title, sub)


def stacked_vbars(cats, segs, title, sub, height=230, label_every=1, W=760):
    """segs: [(name, color, [v per cat])]. Stacked columns, legend below."""
    H, Lm, R, T, B = height, 40, 12, 14, 26
    tot = [sum(s[2][i] for s in segs) for i in range(len(cats))]
    ticks = _ticks(0, max(tot) or 1)
    hi = ticks[-1]
    py = lambda v: T + (H - T - B) * (hi - v) / hi
    n = len(cats)
    slot = (W - Lm - R) / n
    bw = min(40, slot * 0.66)
    out = "".join(f'<line x1="{Lm}" x2="{W - R}" y1="{py(t):.1f}" y2="{py(t):.1f}" stroke="{GRID}"/>'
                  f'<text x="{Lm - 6}" y="{py(t) + 4:.1f}" text-anchor="end" font-size="11" fill="{INK3}">{t:g}</text>' for t in ticks)
    for i, c in enumerate(cats):
        x = Lm + slot * i + (slot - bw) / 2
        y = py(0)
        parts = [(nm, col, vs[i]) for nm, col, vs in segs if vs[i]]
        tipd = f"<b>{e(c)}</b><br>" + "<br>".join(f"{e(nm)}: {v:g}" for nm, _, v in parts) + (f"<br>Total: {tot[i]:g}" if len(parts) > 1 else "")
        g = ""
        for k, (nm, col, v) in enumerate(parts):
            h = y - py(v) if False else (H - T - B) * v / hi
            if k == len(parts) - 1:
                g += _vbar(x, y, bw, h, col)
            else:
                g += f'<rect x="{x:.1f}" y="{y - h:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{col}"/>'
                g += f'<line x1="{x:.1f}" x2="{x + bw:.1f}" y1="{y - h:.1f}" y2="{y - h:.1f}" stroke="#fff" stroke-width="1.5"/>'
            y -= h
        out += f'<g data-tip="{e(tipd)}">{g}<rect x="{Lm + slot * i:.1f}" y="{T}" width="{slot:.1f}" height="{H - T - B}" fill="transparent"/></g>'
        if tot[i] and n <= (20 if W > 600 else 12):
            out += f'<text x="{x + bw / 2:.1f}" y="{y - 5:.1f}" text-anchor="middle" font-size="10.5" fill="{INK2}" pointer-events="none">{tot[i]:g}</text>'
        if i % label_every == 0 or i == n - 1:
            out += f'<text x="{x + bw / 2:.1f}" y="{H - 8}" text-anchor="middle" font-size="11" fill="{INK3}">{e(c)}</text>'
    out += f'<line x1="{Lm}" x2="{W - R}" y1="{py(0):.1f}" y2="{py(0):.1f}" stroke="{INK3}"/>'
    leg = '<div class="viz-legend">' + "".join(f'<span><i style="background:{c}"></i>{e(nm)}</span>' for nm, c, _ in segs) + "</div>"
    return _wrap(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}">{out}</svg>' + leg, title, sub)


def band_line(xs, mid, lo, hi, title, sub, fmt="{:.1f}", lo_tip=None, hi_tip=None, mid_name="League average"):
    """Line (mid) inside a shaded lo..hi band. lo_tip/hi_tip: per-x tooltip text for the extremes."""
    W, H, Lm, R, T, B = 760, 280, 44, 16, 14, 26
    ticks = _ticks(0, max(hi))
    top = ticks[-1]
    px = lambda i: Lm + i * (W - Lm - R) / max(len(xs) - 1, 1)
    py = lambda v: T + (H - T - B) * (1 - v / top)
    out = "".join(f'<line x1="{Lm}" x2="{W - R}" y1="{py(t):.1f}" y2="{py(t):.1f}" stroke="{GRID}"/>'
                  f'<text x="{Lm - 6}" y="{py(t) + 4:.1f}" text-anchor="end" font-size="11" fill="{INK3}">{t:g}</text>' for t in ticks)
    out += "".join(f'<text x="{px(i):.1f}" y="{H - 8}" text-anchor="middle" font-size="11" fill="{INK3}">{e(str(x)[2:] if isinstance(x, int) else x)}</text>'
                   for i, x in enumerate(xs))
    band = "M" + " L".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(hi)) + " L" + \
           " L".join(f"{px(i):.1f},{py(v):.1f}" for i, v in reversed(list(enumerate(lo)))) + " Z"
    out += f'<path d="{band}" fill="{ACCENT}" opacity="0.10"/>'
    out += f'<path d="M{" L".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(mid))}" fill="none" stroke="{ACCENT}" stroke-width="2.5" stroke-linejoin="round"/>'
    for i, x in enumerate(xs):
        out += (f'<circle cx="{px(i):.1f}" cy="{py(hi[i]):.1f}" r="3.5" fill="{ACCENT}" data-tip="{e(hi_tip[i] if hi_tip else fmt.format(hi[i]))}"/>'
                f'<circle cx="{px(i):.1f}" cy="{py(lo[i]):.1f}" r="3.5" fill="{NEG}" data-tip="{e(lo_tip[i] if lo_tip else fmt.format(lo[i]))}"/>'
                f'<circle cx="{px(i):.1f}" cy="{py(mid[i]):.1f}" r="3" fill="#fff" stroke="{ACCENT}" stroke-width="2" '
                f'data-tip="{e(f"<b>{x}</b><br>{mid_name}: {fmt.format(mid[i])}")}"/>')
    leg = (f'<div class="viz-legend"><span><i style="background:{ACCENT}"></i>Season high / {e(mid_name.lower())}</span>'
           f'<span><i style="background:{NEG}"></i>Season low</span><span><i style="background:{ACCENT};opacity:.15"></i>Range</span></div>')
    return _wrap(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}">{out}</svg>' + leg, title, sub)


def strip(cols, title, sub, default=None, fmt="{:.1f}"):
    """cols: [(xlabel, [(name, value, tip)])]. One dot per value, median tick per column.
    Pills highlight one name across columns."""
    W, H, Lm, R, T, B = 760, 300, 44, 12, 14, 26
    allv = [v for _, pts in cols for _, v, _ in pts]
    ticks = _ticks(min(0, min(allv)), max(allv))
    lo, hi = ticks[0], ticks[-1]
    py = lambda v: T + (H - T - B) * (hi - v) / ((hi - lo) or 1)
    slot = (W - Lm - R) / len(cols)
    out = "".join(f'<line x1="{Lm}" x2="{W - R}" y1="{py(t):.1f}" y2="{py(t):.1f}" stroke="{GRID}"/>'
                  f'<text x="{Lm - 6}" y="{py(t) + 4:.1f}" text-anchor="end" font-size="11" fill="{INK3}">{t:g}</text>' for t in ticks)
    dots = ""
    names = set()
    for i, (lab, pts) in enumerate(cols):
        cx = Lm + slot * (i + 0.5)
        vs = sorted(v for _, v, _ in pts)
        med = (vs[len(vs) // 2] + vs[(len(vs) - 1) // 2]) / 2
        out += (f'<line x1="{cx - slot * 0.32:.1f}" x2="{cx + slot * 0.32:.1f}" y1="{py(med):.1f}" y2="{py(med):.1f}" stroke="{INK}" stroke-width="2" '
                f'data-tip="{e(f"<b>{lab}</b><br>Median {fmt.format(med)}")}"/>'
                f'<text x="{cx:.1f}" y="{H - 8}" text-anchor="middle" font-size="11" fill="{INK3}">{e(lab)}</text>')
        for k, (nm, v, tip) in enumerate(sorted(pts, key=lambda p: p[1])):
            jitter = ((k % 3) - 1) * min(5, slot * 0.12)
            names.add(nm)
            dots += f'<circle class="dt" data-m="{e(nm)}" data-hm="{e(nm)}" cx="{cx + jitter:.1f}" cy="{py(v):.1f}" r="4.5" data-tip="{e(tip)}"/>'
    pills = '<div class="viz-pills">' + "".join(f'<button type="button" class="viz-pill" data-m="{e(n)}">{e(n)}</button>' for n in sorted(names)) + "</div>"
    leg = (f'<div class="viz-legend"><span><i style="background:{ACCENT}"></i>Selected manager</span>'
           f'<span><i style="background:{MUTED}"></i>Everyone else</span><span><i style="background:{INK};height:2px;vertical-align:3px"></i>Weekly median</span></div>')
    return _wrap(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}">{out}<g>{dots}</g></svg>' + leg, title, sub, pills,
                 f' data-hl="{e(default or sorted(names)[0])}"')


def sparkline(vals, w=120, h=28, col=ACCENT):
    if not vals:
        return ""
    hi = max(vals) or 1
    px = lambda i: 2 + i * (w - 4) / max(len(vals) - 1, 1)
    py = lambda v: h - 3 - (h - 6) * v / hi
    d = "M" + " L".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(vals))
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true"><path d="{d}" fill="none" stroke="{col}" stroke-width="1.6"/>'
            f'<circle cx="{px(len(vals) - 1):.1f}" cy="{py(vals[-1]):.1f}" r="2.2" fill="{col}"/></svg>')


def scatter_xy(points, title, sub, xlabel, ylabel, xfmt="{:g}", yfmt="{:g}", line=None, zero_line=True, W=760, H=360, labels=True):
    """points: [(x, y, label, tip, color)]. line=(a, b, x0, x1, label) draws y = a + b x."""
    Lm, R, T, B = 52, 20, 14, 40
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    xt = _ticks(min(0, min(xs)), max(xs)); yt = _ticks(min(0, min(ys)), max(ys))
    x0, x1, y0, y1 = xt[0], xt[-1], yt[0], yt[-1]
    px = lambda v: Lm + (W - Lm - R) * (v - x0) / ((x1 - x0) or 1)
    py = lambda v: T + (H - T - B) * (y1 - v) / ((y1 - y0) or 1)
    out = "".join(f'<line x1="{Lm}" x2="{W - R}" y1="{py(t):.1f}" y2="{py(t):.1f}" stroke="{GRID}"/>'
                  f'<text x="{Lm - 6}" y="{py(t) + 4:.1f}" text-anchor="end" font-size="11" fill="{INK3}">{yfmt.format(t)}</text>' for t in yt)
    out += "".join(f'<text x="{px(t):.1f}" y="{H - 22}" text-anchor="middle" font-size="11" fill="{INK3}">{xfmt.format(t)}</text>' for t in xt)
    if zero_line and y0 < 0 < y1:
        out += f'<line x1="{Lm}" x2="{W - R}" y1="{py(0):.1f}" y2="{py(0):.1f}" stroke="{INK3}"/>'
    out += (f'<text x="{(Lm + W - R) / 2}" y="{H - 4}" text-anchor="middle" font-size="11" fill="{INK2}">{e(xlabel)}</text>'
            f'<text x="12" y="{(T + H - B) / 2}" font-size="11" fill="{INK2}" transform="rotate(-90 12 {(T + H - B) / 2})" text-anchor="middle">{e(ylabel)}</text>')
    if line:
        a, b, lx0, lx1, ltxt = line
        out += (f'<line x1="{px(lx0):.1f}" y1="{py(a + b * lx0):.1f}" x2="{px(lx1):.1f}" y2="{py(a + b * lx1):.1f}" stroke="{INK}" stroke-dasharray="5 4" stroke-width="1.5"/>'
                f'<text x="{px(lx1):.1f}" y="{py(a + b * lx1) - 6:.1f}" text-anchor="end" font-size="10.5" fill="{INK}">{e(ltxt)}</text>')
    dots = labs = ""
    placed = []
    for x, y, lab, tip, col in points:
        cx, cy = px(x), py(y)
        dots += (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5.5" fill="{col}" stroke="#fff" stroke-width="1.5" data-tip="{e(tip)}"/>'
                 f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="11" fill="transparent" data-tip="{e(tip)}"/>')
        if labels and lab:
            ly = cy - 9
            while any(abs(ly - qy) < 12 and abs(cx - qx) < 44 for qx, qy in placed):
                ly -= 11
            placed.append((cx, ly))
            labs += f'<text x="{cx:.1f}" y="{ly:.1f}" text-anchor="middle" font-size="11" fill="{INK}" pointer-events="none">{e(lab)}</text>'
    return _wrap(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}">{out}{dots}{labs}</svg>', title, sub)


# ---- phones: time-series charts open scrolled to the latest season/week ----
def _end(html):
    return html.replace('<div class="viz"', '<div class="viz" data-end="1"', 1)


def _yearish(cats):
    return len(cats) >= 8 and all(str(c).isdigit() and len(str(c)) in (2, 4) for c in cats)


for _name in ("multi_line", "strip", "band_line", "finish_line"):
    _f = globals()[_name]
    globals()[_name] = (lambda f: (lambda *a, **k: _end(f(*a, **k))))(_f)

_vbars0, _svbars0 = vbars, stacked_vbars
def vbars(cats, *a, **k):
    h = _vbars0(cats, *a, **k)
    return _end(h) if _yearish(cats) else h
def stacked_vbars(cats, *a, **k):
    h = _svbars0(cats, *a, **k)
    return _end(h) if _yearish(cats) else h
