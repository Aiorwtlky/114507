# Create a teal-themed HTML with JS (Chart.js) restored.
html = r"""<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>道安總動員 — 趨勢分析（JS 版 · Teal 主題）</title>

  <!-- =========================================================
       Style: Teal/Cyan theme (與前版顏色不同) + 長度充足的說明註解
       ========================================================= -->
  <style>
    /* ===== CSS Reset / Base ===== */
    *, *::before, *::after { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; height: 100%; }
    body {
      /* 新色調：Teal / Cyan */
      --bg: #f6fbf9;             /* page background (minty light) */
      --panel: #ffffff;          /* card/panel background */
      --ink: #0f172a;            /* primary text (slate-900) */
      --muted: #657084;          /* secondary text */
      --brand: #14b8a6;          /* accent / brand (teal-500) */
      --brand-weak: rgba(20,184,166,.12);
      --ring: rgba(45,212,191,.25); /* focus ring */
      --ok: #059669;             /* success (emerald-600) */
      --warn: #b45309;           /* warn (amber-700) */
      --bd: #e5f3ef;             /* borders (soft green) */
      --shadow: 0 10px 30px rgba(2, 6, 23, .06);
      --r: 16px;                 /* corner radius */
      --chip-bg: #edf8f5;        /* chip background */
      --chip-ink: #0f3a36;       /* chip text */
      --chip-active-bg: #def7f1; /* chip active background */
      --chip-active-ink: #064e3b;/* chip active text */
      --nav-pill-bg: #fff;       /* nav pill background */
      --nav-pill-bd: #d9eee8;    /* nav pill border */

      /* Chart tones */
      --line: #0ea5a3;           /* primary line (teal-500) */
      --line2: #06b6d4;          /* cyan-500 (hover/points) */

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
      box-shadow: 0 1px 0 rgba(2,6,23,.03);
    }
    .header-inner {
      max-width: 1100px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: auto 1fr auto;
      align-items: center;
      gap: 16px;
      height: 64px;
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
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: inline-grid;
      place-items: center;
      background: radial-gradient(circle at 30% 30%, #a7f3d0, #06b6d4);
      color: #083344;
      font-weight: 900;
      font-size: 16px;
      box-shadow: var(--shadow);
      border: 1px solid #99f6e4;
    }
    .title { font-weight: 800; letter-spacing: .02em; }
    .sub { font-size: 12px; color: var(--muted); }

    /* ===== Pills (tabs near the top) ===== */
    .pillbar {
      display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
    }
    .pill {
      --padx: 14px; --pady: 8px;
      display: inline-flex; align-items: center; gap: 6px;
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
    .pill:hover { background: #f3faf8; border-color: #bfeee3; transform: translateY(-1px); }
    .pill.active {
      background: var(--chip-active-bg);
      color: var(--chip-active-ink);
      border-color: #b8efe6;
      box-shadow: 0 0 0 3px var(--brand-weak);
    }

    /* ===== Actions (right side) ===== */
    .actions { display: flex; gap: 8px; align-items: center; }
    .btn {
      display: inline-flex; align-items: center; gap: 8px;
      padding: 8px 12px; border: 1px solid var(--bd);
      background: #fff; color: var(--ink); border-radius: 12px;
      font-size: 12px; cursor: pointer; transition: all .15s ease; text-decoration: none;
    }
    .btn:hover { border-color: #bfeee3; background: #f2fbf7; }
    .btn.primary {
      background: var(--brand); border-color: var(--brand); color: #042f2e;
      box-shadow: 0 4px 16px rgba(20,184,166,.25); font-weight: 700;
    }
    .btn.primary:hover { filter: brightness(1.02); transform: translateY(-1px); }

    /* ===== Info ticker ===== */
    .ticker { background: linear-gradient(90deg, #f2fbf7, #fff); border-bottom: 1px solid var(--bd); font-size: 13px; }
    .ticker-inner { max-width: 1100px; margin: 0 auto; padding: 10px 16px; color: #134e4a; display: flex; gap: 10px; flex-wrap: wrap; }
    .tag { padding: 4px 8px; border-radius: 999px; background: var(--chip-bg); color: var(--chip-ink); border: 1px solid var(--bd); }
    .tag.strong { background: #def7f1; color: #065f46; border-color: #b7f7e0; }
    .tag.warn { background: #fff7ed; color: #92400e; border-color: #fde68a; }

    /* ===== Main layout ===== */
    .container { max-width: 1100px; margin: 24px auto; padding: 0 16px 48px; display: grid; gap: 20px; }
    .panel { background: var(--panel); border: 1px solid var(--bd); border-radius: var(--r); box-shadow: var(--shadow); overflow: hidden; }
    .panel-head { display: grid; grid-template-columns: 1fr auto; gap: 12px; padding: 14px 16px; border-bottom: 1px solid var(--bd); background: #f2fbf7; }
    .panel-title { font-weight: 700; letter-spacing: .02em; }
    .filters { display: inline-flex; gap: 8px; align-items: center; flex-wrap: wrap; }
    .select {
      appearance: none; -webkit-appearance: none; -moz-appearance: none;
      background: #fff; color: var(--ink); padding: 8px 32px 8px 10px; border-radius: 12px; border: 1px solid var(--bd); font-size: 13px;
      background-image:
        linear-gradient(45deg, transparent 50%, #0ea5a3 50%),
        linear-gradient(135deg, #0ea5a3 50%, transparent 50%),
        linear-gradient(to right, #cbeee8, #cbeee8);
      background-position:
        calc(100% - 18px) calc(1em + 2px),
        calc(100% - 13px) calc(1em + 2px),
        calc(100% - 2.2em) 0.2em;
      background-size: 5px 5px, 5px 5px, 1px 2.2em;
      background-repeat: no-repeat;
    }
    .panel-body { padding: 12px 12px 18px; }
    .chart-wrap { padding: 8px; background: #ffffff; border-radius: 12px; border: 1px dashed var(--bd); }
    .legend { padding: 6px 10px 2px 10px; font-size: 12px; color: var(--muted); }

    /* ===== Utility ===== */
    .muted { color: var(--muted); } .small { font-size: 12px; } .spacer{ height: 8px; }
    .mono  { font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; }

    /* ===== Footer ===== */
    footer { border-top: 1px solid var(--bd); background: #fff; padding: 24px 16px; color: var(--muted); }
    .footer-inner { max-width: 1100px; margin: 0 auto; display: grid; gap: 6px; }

    /* ===== Dark mode ===== */
    body.dark {
      --bg: #071a17;
      --panel: #0b1f1d;
      --ink: #e7fffa;
      --muted: #9ed0c9;
      --brand: #22d3bd;
      --brand-weak: rgba(34,211,178,.18);
      --ring: rgba(56,189,248,.30);
      --bd: #10302c;
      --chip-bg: #0d2624;
      --chip-ink: #d1faf5;
      --chip-active-bg: #0e2e2b;
      --chip-active-ink: #c7fff5;
      --nav-pill-bg: #0d2422;
      --nav-pill-bd: #10302c;
      --line: #22d3bd;
      --line2: #67e8f9;
    }
    body.dark .panel-head { background: #0d2624; }
    body.dark .chart-wrap { background: #0b1f1d; }
    body.dark .btn { background: #0d2422; color: var(--ink); border-color: var(--bd); }
    body.dark .btn.primary { color: #042f2e; }
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
          <div class="sub">示範 | 趨勢分析（JS 版 · Teal 主題）</div>
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
       Ticker: quick stats
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
          <span class="muted small">（示範資料 · Teal 主題）</span>
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

    <!-- Secondary information block -->
    <section class="panel">
      <div class="panel-head"><div class="panel-title">關於此版本</div></div>
      <div class="panel-body">
        <ul>
          <li>色系全面改為 <strong>Teal/Cyan</strong>，並優化暗色模式的對比。</li>
          <li>保留下載 PNG、列印與三個篩選器（以隨機擾動模擬差異）。</li>
          <li>Chart.js 以 CSS 變數驅動顏色，可快速換主題。</li>
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
       Script: Chart.js + behaviors
       ========================================================= -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js" integrity="sha256-j+7VxW8gtJZ2aIY4Zt0htS3wBfHOmOQfTgja1rTBmoc=" crossorigin="anonymous"></script>
  <script>
    // ----- Helpers ---------------------------------------------------------
    const $ = (sel, el=document) => el.querySelector(sel);
    const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n));
    const rand = (min, max) => Math.random() * (max - min) + min;
    const jitter = (v, pct=0.06) => Math.round(v * (1 + (Math.random() * 2 - 1) * pct));

    // ----- Data baseline ---------------------------------------------------
    const baseLabels = [
      "112年7月","112年8月","112年9月","112年10月","112年11月","112年12月",
      "114年1月","114年2月","114年3月","114年4月","114年5月","114年6月"
    ];
    const baseDeaths = [257,246,229,267,246,270,242,232,237,217,230,210];
    const synth = (arr, mult=3.2, noise=0.15) => arr.map(v => Math.round(v * mult + rand(-v*noise, v*noise)));
    const baseInjuries  = synth(baseDeaths, 35, 0.25);
    const baseAccidents = synth(baseDeaths, 20, 0.20);

    function getSeries(area, metric) {
      let src = metric === 'injuries' ? [...baseInjuries]
              : metric === 'accidents' ? [...baseAccidents]
              : [...baseDeaths];
      const areaFactor = area === 'north' ? 0.04 : area === 'central' ? 0.02 : area === 'south' ? 0.06 : area === 'east' ? 0.035 : 0.0;
      src = src.map(v => jitter(v, 0.06 + areaFactor));
      return src;
    }

    // ----- Chart init ------------------------------------------------------
    const ctx = document.getElementById('trendChart');

    function colorVar(name) {
      return getComputedStyle(document.body).getPropertyValue(name).trim();
    }
    function buildGradient(ctx, colorHex) {
      const g = ctx.createLinearGradient(0, 0, 0, 360);
      g.addColorStop(0, colorHex + 'dd');
      g.addColorStop(.6, colorHex + '33');
      g.addColorStop(1, colorHex + '00');
      return g;
    }

    let currentArea = 'nation';
    let currentMetric = 'deaths';

    const lineColor = colorVar('--line') || '#0ea5a3';
    const pointColor = colorVar('--line2') || '#06b6d4';
    const borderColor = getComputedStyle(document.body).getPropertyValue('--bd').trim() || '#e5f3ef';

    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: baseLabels,
        datasets: [{
          label: '死亡人數',
          data: getSeries(currentArea, currentMetric),
          borderWidth: 2,
          tension: 0.25,
          pointRadius: 3.8,
          pointHoverRadius: 6.2,
          borderColor: lineColor,
          pointBackgroundColor: pointColor,
          pointBorderColor: '#fff',
          pointBorderWidth: 1.5,
          fill: true,
          backgroundColor: (c) => buildGradient(c.chart.ctx, lineColor.replace('#', '#'))
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(2,6,23,.85)',
            padding: 10,
            callbacks: { label: ctx => ` ${ctx.dataset.label}：${ctx.formattedValue} 人` }
          },
          title: { display: false }
        },
        scales: {
          x: {
            grid: { color: borderColor },
            ticks: { maxRotation: 0, autoSkip: false }
          },
          y: {
            beginAtZero: false,
            suggestedMin: 200,
            suggestedMax: 300,
            grid: { color: borderColor },
            ticks: { callback: v => v + ' 人' }
          }
        }
      }
    });

    // ----- UI wiring -------------------------------------------------------
    const selArea = $('#selArea');
    const selMetric = $('#selMetric');
    const selScope = $('#selScope');
    const btnDownload = $('#btnDownload');
    const btnPrint = $('#btnPrint');
    const toggleTheme = $('#toggleTheme');

    function refreshChart() {
      const labelMap = { deaths: '死亡人數', injuries: '受傷人數', accidents: '事故件數' };
      const series = getSeries(currentArea, currentMetric);
      chart.data.datasets[0].data = series;
      chart.data.datasets[0].label = labelMap[currentMetric] || '死亡人數';
      chart.update();
    }

    selArea.addEventListener('change', () => { currentArea = selArea.value; refreshChart(); });
    selMetric.addEventListener('change', () => { currentMetric = selMetric.value; refreshChart(); });
    selScope.addEventListener('change', () => {
      const scope = selScope.value;
      const factor = scope === 'urban' ? 0.82 : scope === 'rural' ? 0.56 : 1.0;
      chart.data.datasets[0].data = chart.data.datasets[0].data.map(v => Math.round(v * factor + rand(-5,5)));
      chart.update();
    });

    btnDownload.addEventListener('click', () => {
      const link = document.createElement('a');
      link.download = 'trend-chart-teal.png';
      link.href = chart.toBase64Image();
      link.click();
    });
    btnPrint.addEventListener('click', () => window.print());

    // Theme toggle + live grid recolor
    toggleTheme.addEventListener('click', () => {
      const dark = document.body.classList.toggle('dark');
      toggleTheme.setAttribute('aria-pressed', String(dark));
      const newGrid = getComputedStyle(document.body).getPropertyValue('--bd').trim();
      chart.options.scales.x.grid.color = newGrid;
      chart.options.scales.y.grid.color = newGrid;
      const newLine = getComputedStyle(document.body).getPropertyValue('--line').trim();
      const newPoint = getComputedStyle(document.body).getPropertyValue('--line2').trim();
      chart.data.datasets[0].borderColor = newLine || chart.data.datasets[0].borderColor;
      chart.data.datasets[0].pointBackgroundColor = newPoint || chart.data.datasets[0].pointBackgroundColor;
      chart.update('none');
    });

    // Persist theme
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
  </script>
</body>
</html>
"""
path = "/mnt/data/road-safety-trend-teal.html"
with open(path, "w", encoding="utf-8") as f:
    f.write(html)
path
