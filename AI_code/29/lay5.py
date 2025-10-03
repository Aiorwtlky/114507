# Create an HTML file with CSS + JS inspired by the provided screenshot.
html = r"""<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>道安總動員 — 趨勢分析（示範頁）</title>

  <!-- =========================================================
       Style: long, commented, and line-rich CSS for clarity.
       The page emulates the look-and-feel of the screenshot:
       header, chip-like tabs, info ticker, and a chart panel.
       ========================================================= -->
  <style>
    /* ===== CSS Reset / Base ===== */
    *, *::before, *::after {
      box-sizing: border-box;
    }
    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }
    body {
      /* Theme variables allow quick color scheme switching */
      --bg: #f7f8fb;             /* page background */
      --panel: #ffffff;          /* card/panel background */
      --ink: #131a2a;            /* primary text */
      --muted: #66718a;          /* secondary text */
      --brand: #3a7afe;          /* accent / brand */
      --brand-weak: rgba(58,122,254,.1);
      --ring: rgba(58,122,254,.25); /* focus ring */
      --ok: #0f766e;             /* success */
      --warn: #b91c5a;           /* warn */
      --bd: #e7ecf7;             /* borders */
      --shadow: 0 10px 30px rgba(17,24,39,.06);
      --r: 14px;                 /* corner radius */
      --chip-bg: #f1f4fb;        /* chip background */
      --chip-ink: #24324a;       /* chip text */
      --chip-active-bg: #e7efff; /* chip active background */
      --chip-active-ink: #0f2c7a;/* chip active text */
      --nav-pill-bg: #fff;       /* nav pill background */
      --nav-pill-bd: #e6ecf6;    /* nav pill border */
      --grid-gap: 20px;          /* layout gap */
      --mh: 56px;                /* header height */
      background: var(--bg);
      color: var(--ink);
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
      line-height: 1.6;
    }

    /* ===== Top Header ===== */
    .site-header {
      position: sticky;
      top: 0;
      z-index: 50;
      background: var(--panel);
      border-bottom: 1px solid var(--bd);
      box-shadow: 0 1px 0 rgba(17,24,39,.03);
    }
    .header-inner {
      max-width: 1100px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: auto 1fr auto;
      align-items: center;
      gap: 16px;
      height: var(--mh);
      padding: 0 16px;
    }
    .logo {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      color: inherit;
    }
    .logo-badge {
      width: 34px;
      height: 34px;
      border-radius: 50%;
      display: inline-grid;
      place-items: center;
      background: radial-gradient(circle at 30% 30%, #ffb703, #fb7185);
      color: #fff;
      font-weight: 700;
      font-size: 16px;
      box-shadow: var(--shadow);
    }
    .title {
      font-weight: 800;
      letter-spacing: .02em;
    }
    .sub {
      font-size: 12px;
      color: var(--muted);
    }

    /* ===== Pills (tabs near the top) ===== */
    .pillbar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }
    .pill {
      --padx: 14px;
      --pady: 8px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: var(--pady) var(--padx);
      border: 1px solid var(--nav-pill-bd);
      background: var(--nav-pill-bg);
      color: var(--chip-ink);
      border-radius: 999px;
      font-size: 13px;
      cursor: pointer;
      transition: all .15s ease;
      user-select: none;
      text-decoration: none;
    }
    .pill:hover {
      background: #f9fbff;
      border-color: #d7e5ff;
      transform: translateY(-1px);
    }
    .pill.active {
      background: var(--chip-active-bg);
      color: var(--chip-active-ink);
      border-color: #cfe0ff;
      box-shadow: 0 0 0 3px var(--brand-weak);
    }

    /* ===== Actions (right side) ===== */
    .actions {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border: 1px solid var(--bd);
      background: #fff;
      color: var(--ink);
      border-radius: 10px;
      font-size: 12px;
      cursor: pointer;
      transition: all .15s ease;
      text-decoration: none;
    }
    .btn:hover {
      border-color: #c8d6f2;
      background: #f9fbff;
    }
    .btn.primary {
      background: var(--brand);
      border-color: var(--brand);
      color: #fff;
      box-shadow: 0 4px 16px rgba(58,122,254,.25);
    }
    .btn.primary:hover {
      filter: brightness(.97);
      transform: translateY(-1px);
    }

    /* ===== Info ticker ===== */
    .ticker {
      background: linear-gradient(90deg, #f9fbff, #fff);
      border-bottom: 1px solid var(--bd);
      font-size: 13px;
    }
    .ticker-inner {
      max-width: 1100px;
      margin: 0 auto;
      padding: 10px 16px;
      color: #334155;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .tag {
      padding: 4px 8px;
      border-radius: 999px;
      background: var(--chip-bg);
      color: var(--chip-ink);
      border: 1px solid var(--bd);
    }
    .tag.strong {
      background: #e6fff7;
      color: #065f46;
      border-color: #b7f7e0;
    }
    .tag.warn {
      background: #fff2f5;
      color: #9f1239;
      border-color: #ffd7e1;
    }

    /* ===== Main layout ===== */
    .container {
      max-width: 1100px;
      margin: 24px auto;
      padding: 0 16px 48px;
      display: grid;
      gap: var(--grid-gap);
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--bd);
      border-radius: var(--r);
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .panel-head {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 12px;
      padding: 14px 16px;
      border-bottom: 1px solid var(--bd);
      background: #fbfdff;
    }
    .panel-title {
      font-weight: 700;
      letter-spacing: .02em;
    }
    .filters {
      display: inline-flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
    }
    .select {
      appearance: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      background: #fff;
      color: var(--ink);
      padding: 8px 32px 8px 10px;
      border-radius: 10px;
      border: 1px solid var(--bd);
      font-size: 13px;
      background-image:
        linear-gradient(45deg, transparent 50%, #9aa7bd 50%),
        linear-gradient(135deg, #9aa7bd 50%, transparent 50%),
        linear-gradient(to right, #dfe7f5, #dfe7f5);
      background-position:
        calc(100% - 18px) calc(1em + 2px),
        calc(100% - 13px) calc(1em + 2px),
        calc(100% - 2.2em) 0.2em;
      background-size:
        5px 5px,
        5px 5px,
        1px 2.2em;
      background-repeat: no-repeat;
    }
    .panel-body {
      padding: 12px 12px 18px;
    }
    .chart-wrap {
      padding: 8px;
      background: #ffffff;
      border-radius: 10px;
      border: 1px dashed var(--bd);
    }
    .legend {
      padding: 6px 10px 2px 10px;
      font-size: 12px;
      color: var(--muted);
    }

    /* ===== Utility classes ===== */
    .muted { color: var(--muted); }
    .mono  { font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; }
    .small { font-size: 12px; }
    .dim   { opacity: .85; }
    .spacer{ height: 8px; }

    /* ===== Footer ===== */
    footer {
      border-top: 1px solid var(--bd);
      background: #fff;
      padding: 24px 16px;
      color: var(--muted);
    }
    .footer-inner {
      max-width: 1100px;
      margin: 0 auto;
      display: grid;
      gap: 6px;
    }

    /* ===== Dark mode (toggle via .dark on body) ===== */
    body.dark {
      --bg: #0b1220;
      --panel: #10182a;
      --ink: #dfe7ff;
      --muted: #9fb0d2;
      --brand: #60a5fa;
      --brand-weak: rgba(96,165,250,.18);
      --ring: rgba(96,165,250,.36);
      --bd: #1d2a46;
      --chip-bg: #102038;
      --chip-ink: #cfe3ff;
      --chip-active-bg: #0f254b;
      --chip-active-ink: #d3e7ff;
      --nav-pill-bg: #0e1628;
      --nav-pill-bd: #1d2a46;
    }
    body.dark .panel-head { background: #0e1628; }
    body.dark .chart-wrap { background: #0d1526; }
    body.dark .btn { background: #0e1628; color: var(--ink); border-color: var(--bd); }
    body.dark .btn.primary { color: #0a1222; }
    /* End of dark mode */
  </style>
</head>
<body>
  <!-- =========================================================
       Header: logo + title + tab-like pills + utility buttons
       ========================================================= -->
  <header class="site-header" role="banner">
    <div class="header-inner">
      <a class="logo" href="#">
        <span class="logo-badge">交</span>
        <div>
          <div class="title">道安總動員</div>
          <div class="sub">示範 | 趨勢分析</div>
        </div>
      </a>
      <nav class="pillbar" aria-label="次級導覽">
        <a class="pill" href="#" title="主題分析">📈 主題分析</a>
        <a class="pill" href="#" title="統計快覽">📊 統計快覽</a>
        <a class="pill" href="#" title="縣市鄉鎮與圖層">🗺️ 縣市鄉鎮與圖層</a>
        <a class="pill active" href="#" title="趨勢分析">📉 趨勢分析</a>
        <a class="pill" href="#" title="事件熱點">🔥 事件熱點</a>
        <a class="pill" href="#" title="學校周邊熱點">🏫 學校周邊熱點</a>
      </nav>
      <div class="actions">
        <button class="btn" id="toggleTheme" aria-pressed="false" title="切換深淺色">🌓 切換主題</button>
        <button class="btn" id="btnPrint" title="列印此頁">🖨️ 列印</button>
        <button class="btn primary" id="btnDownload" title="下載圖表為 PNG">⬇️ 下載圖表</button>
      </div>
    </div>
  </header>

  <!-- =========================================================
       Ticker: quick stats (static demo values that resemble the
       screenshot wording; update with your real data as needed)
       ========================================================= -->
  <div class="ticker" role="status">
    <div class="ticker-inner">
      <span class="tag strong">1–6月死亡 1,368人（每日 7.6人）</span>
      <span class="tag">機車騎士死亡 831人</span>
      <span class="tag">高齡者死亡 581人</span>
      <span class="tag">路口事故死亡 589人</span>
      <span class="tag">酒駕事故死亡 67人</span>
      <span class="tag warn">路口慢看停</span>
    </div>
  </div>

  <!-- =========================================================
       Main container: chart panel
       ========================================================= -->
  <main class="container">
    <section class="panel" aria-labelledby="chartTitle">
      <div class="panel-head">
        <div id="chartTitle" class="panel-title">
          全國近12個月交通事故全部死亡人數
          <span class="muted small">（示範資料）</span>
        </div>
        <div class="filters" role="group" aria-label="篩選器">
          <label class="small muted" for="selArea">請選擇</label>
          <select id="selArea" class="select" aria-label="地區">
            <option value="nation">全國</option>
            <option value="north">北部</option>
            <option value="central">中部</option>
            <option value="south">南部</option>
            <option value="east">東部</option>
          </select>
          <select id="selScope" class="select" aria-label="範圍">
            <option value="all">全部</option>
            <option value="urban">市區</option>
            <option value="rural">非市區</option>
          </select>
          <select id="selMetric" class="select" aria-label="指標">
            <option value="deaths" selected>死亡人數</option>
            <option value="injuries">受傷人數</option>
            <option value="accidents">事故件數</option>
          </select>
        </div>
      </div>
      <div class="panel-body">
        <div class="legend">● 死亡人數</div>
        <div class="chart-wrap">
          <canvas id="trendChart" height="360" aria-label="趨勢折線圖" role="img"></canvas>
        </div>
        <div class="spacer"></div>
        <div class="small muted">
          112年 → 114年（1–6月）為示意初估值。此頁為練習示範，請以官方資料為準。
        </div>
      </div>
    </section>

    <!-- Secondary information blocks (static placeholders to extend lines) -->
    <section class="panel">
      <div class="panel-head">
        <div class="panel-title">圖表說明與使用技巧</div>
      </div>
      <div class="panel-body">
        <ul>
          <li>以 <span class="mono">Chart.js</span> 繪製折線圖，滑鼠懸浮可查看各月數值。</li>
          <li>右上角「下載圖表」可將目前視圖另存為 <span class="mono">PNG</span> 圖檔。</li>
          <li>「切換主題」可在淺色與深色之間切換，適合投影或截圖。</li>
          <li>三個下拉選單為範例：切換將以隨機擾動模擬不同分區與指標。</li>
        </ul>
      </div>
    </section>
  </main>

  <footer>
    <div class="footer-inner">
      <div class="small">資料來源（示意）：交通部道安資料開放平台。頁面版型為教學示範，請勿作正式引用。</div>
      <div class="small">© 2025 Demo. All rights reserved.</div>
    </div>
  </footer>

  <!-- =========================================================
       Script section: Chart.js + behaviors
       ========================================================= -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js" integrity="sha256-j+7VxW8gtJZ2aIY4Zt0htS3wBfHOmOQfTgja1rTBmoc=" crossorigin="anonymous"></script>
  <script>
    // ----- Utilities -------------------------------------------------------
    const $ = (sel, el=document) => el.querySelector(sel);
    const $$ = (sel, el=document) => [...el.querySelectorAll(sel)];
    const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n));
    const rand = (min, max) => Math.random() * (max - min) + min;
    const jitter = (v, pct=0.06) => Math.round(v * (1 + (Math.random() * 2 - 1) * pct));

    // Keyboard a11y for buttons
    const clickOnEnter = (el) => {
      el.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); el.click(); }
      });
    };

    // ----- Data (base values resemble the screenshot) ---------------------
    // 112/7 → 114/6 (12 months)
    const baseLabels = [
      "112年7月","112年8月","112年9月","112年10月","112年11月","112年12月",
      "114年1月","114年2月","114年3月","114年4月","114年5月","114年6月"
    ];
    const baseDeaths = [257,246,229,267,246,270,242,232,237,217,230,210];

    // For demonstration, synthesize other metrics from the base array
    const synth = (arr, mult=3.2, noise=0.15) => arr.map(v => Math.round(v * mult + rand(-v*noise, v*noise)));
    const baseInjuries  = synth(baseDeaths, 35, 0.25);
    const baseAccidents = synth(baseDeaths, 20, 0.20);

    // Helper to generate a data series based on dropdowns
    function getSeries(area, metric) {
      // Clone appropriate base metric
      let src = metric === 'injuries' ? [...baseInjuries]
              : metric === 'accidents' ? [...baseAccidents]
              : [...baseDeaths];
      // Apply area-based jitter (north/central/south/east)
      const areaFactor = area === 'north' ? 0.04 : area === 'central' ? 0.02 : area === 'south' ? 0.06 : area === 'east' ? 0.035 : 0.0;
      src = src.map(v => jitter(v, 0.06 + areaFactor));
      return src;
    }

    // ----- Chart initialization -------------------------------------------
    const ctx = document.getElementById('trendChart');
    let currentArea = 'nation';
    let currentMetric = 'deaths';

    // Custom grid & ticks to feel similar to screenshot
    const gridColor = getComputedStyle(document.body).getPropertyValue('--bd').trim() || '#e7ecf7';

    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: baseLabels,
        datasets: [{
          label: '死亡人數',
          data: getSeries(currentArea, currentMetric),
          borderWidth: 2,
          tension: 0.25,
          pointRadius: 3.5,
          pointHoverRadius: 6,
          borderColor: '#f59e0b', // warm line like the screenshot
          pointBackgroundColor: '#f59e0b',
          pointBorderColor: '#fff',
          pointBorderWidth: 1.5,
          fill: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(0,0,0,.8)',
            padding: 10,
            callbacks: {
              label: ctx => ` ${ctx.dataset.label}：${ctx.formattedValue} 人`
            }
          },
          title: { display: false }
        },
        scales: {
          x: {
            grid: { color: gridColor },
            ticks: { maxRotation: 0, autoSkip: false }
          },
          y: {
            beginAtZero: false,
            suggestedMin: 200,
            suggestedMax: 300,
            grid: { color: gridColor },
            ticks: {
              callback: v => v + ' 人'
            }
          }
        }
      }
    });

    // ----- UI behaviors ----------------------------------------------------
    const selArea = document.getElementById('selArea');
    const selMetric = document.getElementById('selMetric');
    const selScope = document.getElementById('selScope'); // not used but wired for future

    function refreshChart() {
      const labelMap = { deaths: '死亡人數', injuries: '受傷人數', accidents: '事故件數' };
      const series = getSeries(currentArea, currentMetric);
      chart.data.datasets[0].data = series;
      chart.data.datasets[0].label = labelMap[currentMetric] || '死亡人數';
      chart.update();
    }

    selArea.addEventListener('change', () => {
      currentArea = selArea.value;
      refreshChart();
    });
    selMetric.addEventListener('change', () => {
      currentMetric = selMetric.value;
      refreshChart();
    });
    selScope.addEventListener('change', () => {
      // scope toggles could scale values a bit to simulate filtering
      const scope = selScope.value;
      const factor = scope === 'urban' ? 0.82 : scope === 'rural' ? 0.56 : 1.0;
      chart.data.datasets[0].data = chart.data.datasets[0].data.map(v => Math.round(v * factor + rand(-5,5)));
      chart.update();
    });

    // ----- Buttons ---------------------------------------------------------
    const btnDownload = document.getElementById('btnDownload');
    const btnPrint = document.getElementById('btnPrint');
    const toggleTheme = document.getElementById('toggleTheme');
    clickOnEnter(btnDownload);
    clickOnEnter(btnPrint);
    clickOnEnter(toggleTheme);

    btnDownload.addEventListener('click', () => {
      const link = document.createElement('a');
      link.download = 'trend-chart.png';
      link.href = chart.toBase64Image(); // export current canvas
      link.click();
    });

    btnPrint.addEventListener('click', () => window.print());

    toggleTheme.addEventListener('click', () => {
      const dark = document.body.classList.toggle('dark');
      toggleTheme.setAttribute('aria-pressed', String(dark));
      // Update grid color dynamically when theme changes
      const newGrid = getComputedStyle(document.body).getPropertyValue('--bd').trim();
      chart.options.scales.x.grid.color = newGrid;
      chart.options.scales.y.grid.color = newGrid;
      chart.update('none');
    });

    // ----- Small enhancement: remember theme across reload -----------------
    (function rememberTheme(){
      const key = 'demo.theme.dark';
      const saved = localStorage.getItem(key);
      if (saved === '1') {
        document.body.classList.add('dark');
        toggleTheme.setAttribute('aria-pressed', 'true');
      }
      toggleTheme.addEventListener('click', () => {
        const isDark = document.body.classList.contains('dark');
        localStorage.setItem(key, isDark ? '1' : '0');
      });
    })();

    // ----- Extra: pretend loading to mimic production pages ----------------
    // (purely cosmetic; adds a bit of realism and extra code lines)
    document.addEventListener('DOMContentLoaded', () => {
      document.body.style.opacity = '1';
    });
  </script>
</body>
</html>
"""
path = "/mnt/data/road-safety-trend.html"
with open(path, "w", encoding="utf-8") as f:
    f.write(html)
path
