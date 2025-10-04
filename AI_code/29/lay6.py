<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>道安總動員 — 縣市鄉鎮與圖譜（互動長條圖範例）</title>
  
  <!-- ============================ -->
  <!--           CSS 範圍           -->
  <!-- ============================ -->
  <style>
    /* ----------------------------- */
    /* 基本變數：方便全站色彩統一       */
    /* ----------------------------- */
    :root {
      --bg: #f6f8fb;               /* 背景底色 */
      --panel: #ffffff;            /* 卡片底色 */
      --ink: #0f172a;              /* 主要文字色 */
      --muted: #64748b;            /* 次要文字色 */
      --brand: #f59e0b;            /* 主題色（橘黃） */
      --brand-ink: #713f12;        /* 主題深色字 */
      --accent: #2563eb;           /* 輔助藍色 */
      --ok: #0f766e;               /* 成功色 */
      --warn: #b91c1c;             /* 警示色 */
      --grid: #e5e7eb;             /* 格線色 */
      --dash: rgba(2, 6, 23, .35); /* 虛線/陰影色 */
      --ring: rgba(37, 99, 235, .18); /* 焦點外圈 */
      --shadow: 0 20px 50px rgba(2, 6, 23, .06);
      --r: 16px;                   /* 卡片圓角 */
      --font: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans TC", "PingFang TC", "Heiti TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    /* ----------------------------- */
    /* Reset：更容易做 pixel-perfect  */
    /* ----------------------------- */
    *, *::before, *::after { box-sizing: border-box; }
    html, body { height: 100%; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: var(--font);
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      line-height: 1.6;
    }
    img { max-width: 100%; display: block; }
    button, select { font-family: inherit; }

    /* ----------------------------- */
    /* App 架構                      */
    /* ----------------------------- */
    .app {
      max-width: 1080px;           /* 與截圖相近的視寬 */
      margin: 24px auto 80px auto; /* 上下留白 */
      padding: 0 16px;             /* 手機左右邊距 */
    }

    header.appbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 14px 16px;
      background: var(--panel);
      border-radius: calc(var(--r) + 4px);
      box-shadow: var(--shadow);
      position: sticky;
      top: 8px;
      z-index: 5;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand .logo {
      width: 36px;
      height: 36px;
      border-radius: 999px;
      display: grid; place-items: center;
      background: radial-gradient(circle at 30% 30%, #1d4ed8, #0ea5e9 40%, #22c55e 70%);
      color: #fff;
      font-weight: 900;
      box-shadow: inset 0 0 0 3px rgba(255,255,255,.45), 0 4px 8px rgba(2,6,23,.15);
      user-select: none;
    }
    .brand h1 {
      font-size: 20px;
      letter-spacing: .04em;
      margin: 0;
      font-weight: 800;
    }

    nav.quick-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .pill {
      --bgp: #fef3c7;             /* pill 的底色（淡黃） */
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid #f8e6a2;
      background: linear-gradient(180deg, var(--bgp), #fff 90%);
      color: var(--brand-ink);
      padding: 8px 12px;
      font-size: 14px;
      border-radius: 999px;
      box-shadow: 0 1px 0 #fff inset, 0 2px 0 rgba(0,0,0,.02);
      cursor: pointer;
      transition: transform .08s ease, box-shadow .2s ease;
      text-decoration: none;
      user-select: none;
    }
    .pill:hover { transform: translateY(-1px); box-shadow: 0 2px 0 #fff inset, 0 10px 16px rgba(0,0,0,.06); }
    .pill:active { transform: translateY(0); }
    .pill .dot { width: 7px; height: 7px; border-radius: 999px; background: var(--brand); box-shadow: 0 0 0 3px rgba(245, 158, 11, .25); }

    /* ----------------------------- */
    /* 卡片與內容區                   */
    /* ----------------------------- */
    .panel {
      margin-top: 16px;
      background: var(--panel);
      border-radius: var(--r);
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .panel .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 12px 16px;
      border-bottom: 1px solid #eef2f7;
      background: linear-gradient(180deg, #fff, #fbfdff);
    }

    .toolbar .left {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .burger { width: 28px; height: 28px; border-radius: 8px; display: grid; place-items: center; color: var(--muted); border: 1px solid #e5e7eb; background: #fff; box-shadow: 0 1px 0 #fff inset; }
    .burger i { width: 16px; height: 2px; background: currentColor; position: relative; display: block; }
    .burger i::before, .burger i::after { content: ""; position: absolute; left: 0; width: 16px; height: 2px; background: currentColor; }
    .burger i::before { top: -5px; }
    .burger i::after  { top:  5px; }

    .toolbar .right {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .toolbar .title {
      white-space: nowrap;
      font-weight: 700;
      font-size: 15px;
      color: var(--muted);
    }

    .filters { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
    .filters label { font-size: 12px; color: var(--muted); }

    .select {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid #e5e7eb;
      padding: 6px 10px;
      border-radius: 10px;
      background: #fff;
      box-shadow: 0 1px 0 #fff inset;
    }
    .select select {
      border: 0;
      outline: none;
      background: transparent;
      font-size: 14px;
      color: var(--ink);
    }

    .icon-btn {
      width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center; border: 1px solid #e5e7eb; background: #fff; color: #0f172a; cursor: pointer; box-shadow: 0 1px 0 #fff inset;
    }
    .icon-btn:hover { box-shadow: 0 1px 0 #fff inset, 0 8px 16px rgba(15, 23, 42, .06); }

    /* ----------------------------- */
    /* 圖表區                          */
    /* ----------------------------- */
    .chart-wrap { position: relative; padding: 16px; }
    .chart-card {
      position: relative;
      background: #fff;
      border: 1px solid #eef2f7;
      border-radius: 14px;
      padding: 12px 12px 24px 12px;
      box-shadow: 0 1px 0 #fff inset;
    }

    .chart-head { display: flex; align-items: center; justify-content: center; padding: 10px; }
    .chart-head h2 { margin: 0; font-size: 16px; color: #111827; letter-spacing: .02em; }

    .canvas-wrap { position: relative; height: 540px; }
    canvas#barChart { width: 100%; height: 100%; display: block; }

    .y-label, .x-label { position: absolute; pointer-events: none; color: var(--muted); font-size: 12px; }
    .y-label { left: 6px; top: 8px; }

    /* 平均線小字 */
    .avg-tag {
      position: absolute;
      font-size: 12px;
      color: var(--accent);
      background: #eef2ff;
      border: 1px dashed #bfdbfe;
      padding: 2px 6px;
      border-radius: 999px;
      transform: translateY(-50%);
      white-space: nowrap;
    }

    /* 滑動提示框 */
    .tip {
      position: absolute;
      min-width: 120px;
      max-width: 240px;
      background: #0f172a;
      color: #f8fafc;
      font-size: 12px;
      padding: 8px 10px;
      border-radius: 10px;
      box-shadow: 0 10px 30px rgba(2,6,23,.25);
      transform: translate(-50%, calc(-100% - 14px));
      pointer-events: none;
      opacity: 0;
      transition: opacity .15s ease;
      z-index: 10;
    }
    .tip::after {
      content: "";
      position: absolute;
      left: 50%;
      bottom: -6px;
      transform: translateX(-50%);
      width: 10px; height: 10px;
      background: #0f172a;
      clip-path: polygon(50% 100%, 0 0, 100% 0);
    }

    /* 底部註記 */
    .footnote {
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      text-align: center;
      border-top: 1px dashed #e5e7eb;
      padding: 10px 8px 2px 8px;
    }

    /* RWD - 小螢幕微調 */
    @media (max-width: 720px) {
      .brand h1 { font-size: 18px; }
      .pill { padding: 6px 10px; }
      .toolbar .title { display: none; }
      .filters { width: 100%; }
      .canvas-wrap { height: 520px; }
    }
  </style>
</head>

<body>
  <div class="app" id="app">
    <!-- 上方 App Bar -->
    <header class="appbar">
      <div class="brand">
        <div class="logo" aria-hidden="true">台</div>
        <h1>道安總動員</h1>
      </div>
      <nav class="quick-actions" aria-label="快速功能">
        <a class="pill" href="#" title="主題分析"><span class="dot"></span><span>主題分析</span></a>
        <a class="pill" href="#" title="統計快覽"><span class="dot"></span><span>統計快覽</span></a>
        <a class="pill" href="#" title="縣市鄉鎮與圖譜"><span class="dot"></span><span>縣市鄉鎮與圖譜</span></a>
        <a class="pill" href="#" title="趨勢分析"><span class="dot"></span><span>趨勢分析</span></a>
        <a class="pill" href="#" title="肇事熱點"><span class="dot"></span><span>肇事熱點</span></a>
        <a class="pill" href="#" title="學校周邊熱點"><span class="dot"></span><span>學校周邊熱點</span></a>
      </nav>
    </header>

    <!-- 卡片 Panel：圖表 -->
    <section class="panel">
      <div class="toolbar">
        <div class="left">
          <button class="burger" aria-label="開關側欄"><i></i></button>
          <div class="title">114年1–6月死亡 1,368人（每日 7.6人）</div>
        </div>
        <div class="right">
          <div class="filters" aria-label="條件篩選">
            <span class="select"><label for="scope">請選擇</label>
              <select id="scope" aria-label="區域範圍">
                <option value="nation" selected>全國</option>
                <option value="north">北部</option>
                <option value="center">中部</option>
                <option value="south">南部</option>
                <option value="east">東部</option>
                <option value="islands">離島</option>
              </select>
            </span>
            <span class="select"><label for="year">年份</label>
              <select id="year" aria-label="年份">
                <option value="114" selected>114年</option>
                <option value="113">113年</option>
                <option value="112">112年</option>
              </select>
            </span>
            <span class="select"><label for="from">起</label>
              <select id="from" aria-label="起始月份">
                <option>01月</option>
                <option selected>01月至</option>
              </select>
            </span>
            <span class="select"><label for="to">迄</label>
              <select id="to" aria-label="結束月份">
                <option>02月</option>
                <option selected>06月</option>
                <option>12月</option>
              </select>
            </span>
            <span class="select"><label for="cat">類別</label>
              <select id="cat" aria-label="族群類別">
                <option selected>全部</option>
                <option>機車</option>
                <option>行人</option>
                <option>汽車</option>
              </select>
            </span>
          </div>
          <span class="muted" style="font-size:12px;color:#94a3b8">（JS 已移除，以下為靜態 SVG 圖表示意）</span>
        </div>
      </div>

      <div class="chart-wrap">
        <div class="chart-card" role="img" aria-label="114年01月至06月各縣市30日死亡人數 長條圖">
          <div class="chart-head">
            <h2>114年01月～06月各縣市30日死亡人數</h2>
          </div>
          <div class="canvas-wrap">
  <svg id="chart" viewBox="0 0 960 540" preserveAspectRatio="none" role="img" aria-label="114年01月至06月各縣市30日死亡人數 長條圖（靜態）">
    <defs>
      <linearGradient id="gNorm" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#f59e0b"/>
        <stop offset="100%" stop-color="#fbbf24"/>
      </linearGradient>
      <linearGradient id="gHot" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ef4444"/>
        <stop offset="100%" stop-color="#f97316"/>
      </linearGradient>
    </defs>

    <!-- 背景 -->
    <rect x="0" y="0" width="960" height="540" fill="#ffffff" />

    <!-- 格線與座標軸 -->
    <g>
      <line class="grid" x1="64" y1="420" x2="920" y2="420" />
      <line class="grid" x1="64" y1="320" x2="920" y2="320" />
      <line class="grid" x1="64" y1="220" x2="920" y2="220" />
      <line class="grid" x1="64" y1="120" x2="920" y2="120" />
      <line class="grid" x1="64" y1="20"  x2="920" y2="20"  />

      <line class="axis" x1="64" y1="20" x2="64" y2="420" />
      <line class="axis" x1="64" y1="420" x2="920" y2="420" />

      <text class="tick" x="56" y="420" dominant-baseline="middle">0</text>
      <text class="tick" x="56" y="320" dominant-baseline="middle">50</text>
      <text class="tick" x="56" y="220" dominant-baseline="middle">100</text>
      <text class="tick" x="56" y="120" dominant-baseline="middle">150</text>
      <text class="tick" x="56" y="20"  dominant-baseline="middle">200</text>

      <!-- 平均線 -->
      <line class="avg" x1="64" y1="306" x2="920" y2="306" />
      <text class="avgtag" x="882" y="298">平均線 57.0</text>
    </g>

    <!-- 柱狀圖（靜態資料） -->
    <g>
      <g><rect x="64.0" y="386.0" width="29.6" height="34.0" fill="url(#gNorm)" rx="4" /><text x="78.8" y="380.0" class="v">17</text><text x="78.8" y="440" class="lbl" transform="rotate(-40 78.8,440)">基隆市</text></g>
      <g><rect x="101.6" y="324.0" width="29.6" height="96.0" fill="url(#gNorm)" rx="4" /><text x="116.4" y="318.0" class="v">48</text><text x="116.4" y="440" class="lbl" transform="rotate(-40 116.4,440)">臺北市</text></g>
      <g><rect x="139.2" y="176.0" width="29.6" height="244.0" fill="url(#gHot)"  rx="4" /><text x="154.0" y="170.0" class="v">122</text><text x="154.0" y="440" class="lbl" transform="rotate(-40 154.0,440)">新北市</text></g>
      <g><rect x="176.8" y="192.0" width="29.6" height="228.0" fill="url(#gHot)"  rx="4" /><text x="191.6" y="186.0" class="v">114</text><text x="191.6" y="440" class="lbl" transform="rotate(-40 191.6,440)">桃園市</text></g>
      <g><rect x="214.4" y="380.0" width="29.6" height="40.0" fill="url(#gNorm)" rx="4" /><text x="229.2" y="374.0" class="v">20</text><text x="229.2" y="440" class="lbl" transform="rotate(-40 229.2,440)">新竹市</text></g>
      <g><rect x="252.0" y="346.0" width="29.6" height="74.0" fill="url(#gNorm)" rx="4" /><text x="266.8" y="340.0" class="v">37</text><text x="266.8" y="440" class="lbl" transform="rotate(-40 266.8,440)">新竹縣</text></g>
      <g><rect x="289.6" y="322.0" width="29.6" height="98.0" fill="url(#gNorm)" rx="4" /><text x="304.4" y="316.0" class="v">49</text><text x="304.4" y="440" class="lbl" transform="rotate(-40 304.4,440)">苗栗縣</text></g>
      <g><rect x="327.2" y="154.0" width="29.6" height="266.0" fill="url(#gHot)"  rx="4" /><text x="342.0" y="148.0" class="v">133</text><text x="342.0" y="440" class="lbl" transform="rotate(-40 342.0,440)">臺中市</text></g>
      <g><rect x="364.8" y="216.0" width="29.6" height="204.0" fill="url(#gNorm)" rx="4" /><text x="379.6" y="210.0" class="v">102</text><text x="379.6" y="440" class="lbl" transform="rotate(-40 379.6,440)">彰化縣</text></g>
      <g><rect x="402.4" y="338.0" width="29.6" height="82.0" fill="url(#gNorm)" rx="4" /><text x="417.2" y="332.0" class="v">41</text><text x="417.2" y="440" class="lbl" transform="rotate(-40 417.2,440)">南投縣</text></g>
      <g><rect x="440.0" y="330.0" width="29.6" height="90.0" fill="url(#gNorm)" rx="4" /><text x="454.8" y="324.0" class="v">45</text><text x="454.8" y="440" class="lbl" transform="rotate(-40 454.8,440)">雲林縣</text></g>
      <g><rect x="477.6" y="370.0" width="29.6" height="50.0" fill="url(#gNorm)" rx="4" /><text x="492.4" y="364.0" class="v">25</text><text x="492.4" y="440" class="lbl" transform="rotate(-40 492.4,440)">嘉義市</text></g>
      <g><rect x="515.2" y="330.0" width="29.6" height="90.0" fill="url(#gNorm)" rx="4" /><text x="530.0" y="324.0" class="v">45</text><text x="530.0" y="440" class="lbl" transform="rotate(-40 530.0,440)">嘉義縣</text></g>
      <g><rect x="552.8" y="84.0" width="29.6" height="336.0" fill="url(#gHot)"  rx="4" /><text x="567.6" y="78.0" class="v">168</text><text x="567.6" y="440" class="lbl" transform="rotate(-40 567.6,440)">臺南市</text></g>
      <g><rect x="590.4" y="116.0" width="29.6" height="304.0" fill="url(#gHot)"  rx="4" /><text x="605.2" y="110.0" class="v">152</text><text x="605.2" y="440" class="lbl" transform="rotate(-40 605.2,440)">高雄市</text></g>
      <g><rect x="628.0" y="248.0" width="29.6" height="172.0" fill="url(#gNorm)" rx="4" /><text x="642.8" y="242.0" class="v">86</text><text x="642.8" y="440" class="lbl" transform="rotate(-40 642.8,440)">屏東縣</text></g>
      <g><rect x="665.6" y="332.0" width="29.6" height="88.0" fill="url(#gNorm)" rx="4" /><text x="680.4" y="326.0" class="v">44</text><text x="680.4" y="440" class="lbl" transform="rotate(-40 680.4,440)">宜蘭縣</text></g>
      <g><rect x="703.2" y="368.0" width="29.6" height="52.0" fill="url(#gNorm)" rx="4" /><text x="718.0" y="362.0" class="v">26</text><text x="718.0" y="440" class="lbl" transform="rotate(-40 718.0,440)">花蓮縣</text></g>
      <g><rect x="740.8" y="380.0" width="29.6" height="40.0" fill="url(#gNorm)" rx="4" /><text x="755.6" y="374.0" class="v">20</text><text x="755.6" y="440" class="lbl" transform="rotate(-40 755.6,440)">臺東縣</text></g>
      <g><rect x="778.4" y="408.0" width="29.6" height="12.0" fill="url(#gNorm)" rx="4" /><text x="793.2" y="402.0" class="v">6</text><text x="793.2" y="440" class="lbl" transform="rotate(-40 793.2,440)">澎湖縣</text></g>
      <g><rect x="816.0" y="416.0" width="29.6" height="4.0"  fill="url(#gNorm)" rx="4" /><text x="830.8" y="410.0" class="v">2</text><text x="830.8" y="440" class="lbl" transform="rotate(-40 830.8,440)">金門縣</text></g>
      <g><rect x="853.6" y="420.0" width="29.6" height="0.0"  fill="url(#gNorm)" rx="4" /><text x="868.4" y="414.0" class="v">0</text><text x="868.4" y="440" class="lbl" transform="rotate(-40 868.4,440)">連江縣</text></g>
      <g><rect x="891.2" y="406.0" width="29.6" height="14.0" fill="url(#gNorm)" rx="4" /><text x="906.0" y="400.0" class="v">7</text><text x="906.0" y="440" class="lbl" transform="rotate(-40 906.0,440)">其他</text></g>
    </g>

    <style>
      .grid { stroke: #e5e7eb; stroke-width: 1; }
      .axis { stroke: #cbd5e1; stroke-width: 1; }
      .avg  { stroke: #60a5fa; stroke-width: 1.5; stroke-dasharray: 4 6; }
      text.v { font: 700 12px system-ui,Segoe UI,Arial; fill: #111827; text-anchor: middle; }
      text.lbl { font: 600 12px system-ui,Segoe UI,Arial; fill: #475569; text-anchor: end; }
      text.tick { font: 600 12px system-ui,Segoe UI,Arial; fill: #64748b; text-anchor: end; }
      text.avgtag { font: 600 12px system-ui,Segoe UI,Arial; fill: #2563eb; }
    </style>
  </svg>
</div>
            <div class="avg-tag" id="avgTag" style="left: unset; right: 8px; top: 50%;">平均線 57.0</div>
            <div class="tip" id="tip"></div>
          </div>
          <div class="footnote">112年、113年・114年1-6月查詢結果為初估值</div>
        </div>
      </div>
    </section>
  </div>

  <!-- ============================ -->
  <!--            JS 區              -->
  <!-- ============================ -->
  
</body>
</html>
