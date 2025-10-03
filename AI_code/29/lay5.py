# Generate a pure HTML + CSS version (no JS) with an inline SVG chart.
labels = ["112年7月","112年8月","112年9月","112年10月","112年11月","112年12月",
          "114年1月","114年2月","114年3月","114年4月","114年5月","114年6月"]
values = [257,246,229,267,246,270,242,232,237,217,230,210]

# SVG layout parameters
W, H = 960, 360
pad_left, pad_right, pad_top, pad_bottom = 72, 20, 24, 64
chart_w = W - pad_left - pad_right
chart_h = H - pad_top - pad_bottom

# Y-axis scale (approx. screenshot style)
y_min, y_max = 200, 300
y_grid = [200, 230, 260, 290]

# Compute points
def x_pos(i, n=len(values)):
    if n == 1:
        return pad_left + chart_w/2
    return pad_left + i * (chart_w / (n-1))

def y_pos(v):
    # invert y (SVG origin at top-left)
    ratio = (v - y_min) / (y_max - y_min)
    ratio = max(0.0, min(1.0, ratio))
    return pad_top + chart_h * (1 - ratio)

points = [(x_pos(i), y_pos(v)) for i, v in enumerate(values)]
poly_points = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)

# Month label positions
x_labels = [x_pos(i) for i in range(len(labels))]
y_labels = [y_pos(v) for v in values]

# Build SVG elements
grid_lines = "\n".join(
    f'<line x1="{pad_left}" y1="{y_pos(y)}" x2="{W-pad_right}" y2="{y_pos(y)}" class="grid"/>'
    for y in y_grid
)
y_ticks = "\n".join(
    f'<text x="{pad_left-10}" y="{y_pos(y)+4}" class="y-tick" text-anchor="end">{y}</text>'
    for y in y_grid
)
x_tick_elems = "\n".join(
    f'<text x="{x_labels[i]}" y="{H-pad_bottom+24}" class="x-tick" text-anchor="middle">{labels[i]}</text>'
    for i in range(len(labels))
)
point_nodes = "\n".join(
    f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" class="pt"/>' for (x,y) in points
)
point_labels = "\n".join(
    f'<text x="{x:.2f}" y="{y-10:.2f}" class="pt-label" text-anchor="middle">{values[i]}</text>'
    for i, (x,y) in enumerate(points)
)

svg = f"""
<svg viewBox="0 0 {W} {H}" width="100%" height="360" role="img" aria-label="死亡人數折線圖（純 SVG）">
  <desc>全國近12個月交通事故全部死亡人數，純 SVG 呈現。</desc>
  <!-- Plot area border -->
  <rect x="{pad_left}" y="{pad_top}" width="{chart_w}" height="{chart_h}" class="plot"/>
  <!-- Horizontal grid lines -->
  {grid_lines}
  <!-- Axes -->
  <line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{pad_top+chart_h}" class="axis"/>
  <line x1="{pad_left}" y1="{pad_top+chart_h}" x2="{pad_left+chart_w}" y2="{pad_top+chart_h}" class="axis"/>
  <!-- Y ticks -->
  {y_ticks}
  <!-- X ticks (month labels) -->
  {x_tick_elems}
  <!-- Data polyline -->
  <polyline points="{poly_points}" class="line"/>
  <!-- Data points -->
  {point_nodes}
  <!-- Point labels -->
  {point_labels}
  <!-- Legend -->
  <g transform="translate({pad_left+8}, {pad_top+16})">
    <circle cx="0" cy="-5" r="4" class="pt"/>
    <text x="10" y="-2" class="legend">死亡人數</text>
  </g>
</svg>
"""

html = f"""<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>道安總動員 — 趨勢分析（純 HTML+CSS，無 JS）</title>
  <!--
    本檔為「無 JavaScript」版本：
    - 圖表使用 inline SVG 靜態繪製。
    - 主題切換採 CSS :checked sibling hack（無 JS）。
    - 版面設計與色彩接近你的截圖。
  -->
  <style>
    /* ========== Base & Theme Variables ========== */
    :root {{
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #131a2a;
      --muted: #66718a;
      --brand: #3a7afe;
      --chip-bg: #f1f4fb;
      --chip-ink: #24324a;
      --bd: #e7ecf7;
      --shadow: 0 10px 30px rgba(17,24,39,.06);
      --r: 14px;
      --mh: 56px;
      --line: #f59e0b;
      --line-dim: #f8c56f;
    }}
    /* prefers-color-scheme for auto dark if不手動切換 */
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #0b1220;
        --panel: #10182a;
        --ink: #dfe7ff;
        --muted: #9fb0d2;
        --brand: #60a5fa;
        --chip-bg: #102038;
        --chip-ink: #cfe3ff;
        --bd: #1d2a46;
        --line: #f59e0b;
        --line-dim: #b0894f;
      }}
    }}
    /* Checkbox-driven theme override (no JS) */
    #theme:checked ~ .page {{
      --bg: #0b1220;
      --panel: #10182a;
      --ink: #dfe7ff;
      --muted: #9fb0d2;
      --brand: #60a5fa;
      --chip-bg: #102038;
      --chip-ink: #cfe3ff;
      --bd: #1d2a46;
      --line: #f59e0b;
      --line-dim: #b0894f;
    }}

    /* ========== Global ========== */
    html, body {{
      margin: 0; padding: 0; height: 100%;
    }}
    body {{
      background: var(--bg);
      color: var(--ink);
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", Helvetica, Arial;
      line-height: 1.6;
    }}
    .page {{
      min-height: 100vh;
      display: grid;
      grid-template-rows: auto auto 1fr auto;
    }}

    /* ========== Header ========== */
    .site-header {{
      position: sticky; top: 0; z-index: 20;
      background: var(--panel);
      border-bottom: 1px solid var(--bd);
    }}
    .header-inner {{
      max-width: 1100px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: auto 1fr auto;
      align-items: center;
      gap: 16px;
      height: var(--mh);
      padding: 0 16px;
    }}
    .logo {{
      display: inline-grid; grid-auto-flow: column; align-items: center; gap: 10px;
      text-decoration: none; color: inherit;
    }}
    .logo-badge {{
      width: 34px; height: 34px; border-radius: 50%;
      display: grid; place-items: center; color: #fff; font-weight: 700;
      background: radial-gradient(circle at 30% 30%, #ffb703, #fb7185);
      box-shadow: var(--shadow);
    }}
    .title {{ font-weight: 800; letter-spacing: .02em; }}
    .sub {{ font-size: 12px; color: var(--muted); }}

    /* ========== Pills (tabs) ========== */
    .pillbar {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
    .pill {{
      display: inline-flex; align-items: center; gap: 6px;
      padding: 8px 14px; border-radius: 999px; font-size: 13px;
      border: 1px solid var(--bd); background: #fff; color: #152033;
      text-decoration: none;
    }}
    .pill.active {{ background: #e7efff; color: #0f2c7a; border-color: #cfe0ff; }}

    /* ========== Theme Toggle (CSS only) ========== */
    .toggle-wrap {{ display: flex; gap: 8px; align-items: center; }}
    .toggle {{ display: inline-flex; gap: 8px; align-items: center; padding: 8px 12px;
              border: 1px solid var(--bd); background: #fff; border-radius: 10px; font-size: 12px; }}
    .toggle::before {{ content: "🌓"; }}
    /* show state text */
    #theme:not(:checked) ~ .page .toggle span::after {{ content: "  淺色模式"; color: var(--muted); }}
    #theme:checked ~ .page .toggle span::after {{ content: "  深色模式"; color: var(--muted); }}

    /* ========== Ticker ========== */
    .ticker {{ background: linear-gradient(90deg,#f9fbff,#fff); border-bottom: 1px solid var(--bd); }}
    .ticker-inner {{ max-width: 1100px; margin: 0 auto; padding: 10px 16px; display: flex; gap: 10px; flex-wrap: wrap; }}
    .tag {{ padding: 4px 8px; border-radius: 999px; background: var(--chip-bg); color: var(--chip-ink); border: 1px solid var(--bd); }}
    .tag.strong {{ background: #e6fff7; color: #065f46; border-color: #b7f7e0; }}
    .tag.warn {{ background: #fff2f5; color: #9f1239; border-color: #ffd7e1; }}

    /* ========== Container & Panels ========== */
    .container {{ max-width: 1100px; margin: 24px auto; padding: 0 16px 48px; display: grid; gap: 20px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--bd); border-radius: var(--r); box-shadow: var(--shadow); overflow: hidden; }}
    .panel-head {{ display: grid; grid-template-columns: 1fr auto; gap: 12px; padding: 14px 16px; border-bottom: 1px solid var(--bd); background: #fbfdff; }}
    .panel-title {{ font-weight: 700; letter-spacing: .02em; }}
    .filters {{ display: inline-flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
    .select {{ appearance: none; background: #fff; color: var(--ink); padding: 8px 12px; border-radius: 10px; border: 1px solid var(--bd); font-size: 13px; }}
    .panel-body {{ padding: 12px 12px 18px; }}
    .legend-text {{ font-size: 12px; color: var(--muted); padding: 6px 10px 2px 10px; }}

    /* ========== SVG Chart Styling ========== */
    .chart-wrap {{ border: 1px dashed var(--bd); border-radius: 10px; background: #fff; overflow: hidden; }}
    svg .plot {{ fill: #fff; stroke: var(--bd); }}
    svg .grid {{ stroke: var(--bd); stroke-dasharray: 3 5; }}
    svg .axis {{ stroke: var(--bd); }}
    svg .line {{ fill: none; stroke: var(--line); stroke-width: 2; }}
    svg .pt {{ fill: var(--line); stroke: #fff; stroke-width: 1.5; }}
    svg .pt-label {{ font: 12px/1.2 system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans TC"; fill: var(--ink); }}
    svg .x-tick, svg .y-tick, svg .legend {{ font: 12px/1.2 system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans TC"; fill: var(--muted); }}

    /* ========== Footer ========== */
    footer {{ border-top: 1px solid var(--bd); background: #fff; padding: 24px 16px; color: var(--muted); }}
    .footer-inner {{ max-width: 1100px; margin: 0 auto; display: grid; gap: 6px; }}
  </style>
</head>
<body>
  <!-- Checkbox for CSS-only theme toggle -->
  <input type="checkbox" id="theme" hidden />
  <div class="page">
    <header class="site-header">
      <div class="header-inner">
        <a class="logo" href="#">
          <span class="logo-badge">交</span>
          <div>
            <div class="title">道安總動員</div>
            <div class="sub">示範 | 趨勢分析（無 JS）</div>
          </div>
        </a>
        <nav class="pillbar" aria-label="次級導覽">
          <a class="pill" href="#">📈 主題分析</a>
          <a class="pill" href="#">📊 統計快覽</a>
          <a class="pill" href="#">🗺️ 縣市鄉鎮與圖層</a>
          <a class="pill active" href="#">📉 趨勢分析</a>
          <a class="pill" href="#">🔥 事件熱點</a>
          <a class="pill" href="#">🏫 學校周邊熱點</a>
        </nav>
        <label class="toggle" for="theme" title="CSS-only 主題切換"><span></span></label>
      </div>
    </header>

    <div class="ticker">
      <div class="ticker-inner">
        <span class="tag strong">1–6月死亡 1,368人（每日 7.6人）</span>
        <span class="tag">機車騎士死亡 831人</span>
        <span class="tag">高齡者死亡 581人</span>
        <span class="tag">路口事故死亡 589人</span>
        <span class="tag">酒駕事故死亡 67人</span>
        <span class="tag warn">路口慢看停</span>
      </div>
    </div>

    <main class="container">
      <section class="panel" aria-labelledby="chartTitle">
        <div class="panel-head">
          <div id="chartTitle" class="panel-title">
            全國近12個月交通事故全部死亡人數
            <span style="font-size:12px; color:var(--muted);">（純 SVG 靜態圖，無 JS）</span>
          </div>
          <div class="filters" aria-label="篩選器（示範）">
            <label for="area" style="font-size:12px; color:var(--muted);">請選擇</label>
            <select id="area" class="select" disabled>
              <option selected>全國</option>
              <option>北部</option><option>中部</option><option>南部</option><option>東部</option>
            </select>
            <select class="select" disabled>
              <option selected>全部</option><option>市區</option><option>非市區</option>
            </select>
            <select class="select" disabled>
              <option selected>死亡人數</option><option>受傷人數</option><option>事故件數</option>
            </select>
          </div>
        </div>
        <div class="panel-body">
          <div class="legend-text">● 死亡人數</div>
          <div class="chart-wrap">
            {svg}
          </div>
          <div style="height:8px;"></div>
          <div style="font-size:12px; color:var(--muted);">
            112年 → 114年（1–6月）為示意初估值。此頁為練習示範，請以官方資料為準。
            如需列印，請使用瀏覽器 <b>Ctrl/Cmd + P</b>；如需下載圖，請以「另存圖片」方式取得。
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head"><div class="panel-title">圖表說明與注意事項</div></div>
        <div class="panel-body">
          <ul>
            <li>本頁所有互動元素均停用，以符合「無 JavaScript」的需求。</li>
            <li>折線圖以 <span style="font-family:monospace;">SVG</span> 繪製，點位與數值皆以向量標註，放大不失真。</li>
            <li>主題切換採用 CSS <span style="font-family:monospace;">:checked</span> sibling 技巧，不依賴任何 JS。</li>
            <li>若日後要恢復互動（下載、列印、切換資料），可再加入精簡 JS 或以伺服端預先產出多版本 SVG。</li>
          </ul>
        </div>
      </section>
    </main>

    <footer>
      <div class="footer-inner">
        <div style="font-size:12px;">資料來源（示意）：交通部道安資料開放平台。頁面版型為教學示範。</div>
        <div style="font-size:12px;">© 2025 Demo. All rights reserved.</div>
      </div>
    </footer>
  </div>
</body>
</html>
"""
out = "/mnt/data/road-safety-trend-nojs.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
out
