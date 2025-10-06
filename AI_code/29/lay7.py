<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>最新法令修正或宣導｜運研所指引（原則）</title>
  
  <!--
    本檔為單一 HTML，內嵌 CSS 與 JS。
    版面依照使用者提供之截圖風格設計：上方大標、中標；
    下方四張卡片（含標題、下載圖示、插圖、意見回饋連結）與左右導引箭頭。
    盡量讓行數多，並維持可讀性與可維護性。
  -->

  <style>
    /* ==========================
       基礎變數（CSS Variables）
       ========================== */
    :root {
      --bg-0: #bfe7ff;         /* 背景由淡藍到更淡的漸層  */
      --bg-1: #d5f0ff;         /* 背景上層色                                  */
      --panel: #eaf6ff;        /* 外框面板色                                   */
      --paper: #ffffff;        /* 卡片內文底色                                 */
      --ink: #0f172a;          /* 文字主色                                     */
      --muted: #3b82f6;        /* 主要藍色                                     */
      --muted-2: #2563eb;      /* 深一階藍                                      */
      --muted-3: #1d4ed8;      /* 更深藍                                        */
      --accent: #38bdf8;       /* 青藍點綴                                      */
      --ok: #059669;           /* 綠色（成功）                                   */
      --warn: #b91c1c;         /* 紅色（警示）                                   */
      --ring: rgba(59,130,246,.35); /* 聚焦陰影                                 */
      --shadow: 0 10px 40px rgba(2, 8, 23, 0.12);
      --radius: 16px;          /* 圓角                                          */
      --radius-2: 24px;        /* 大圓角                                        */
      --gap: 22px;             /* 卡片間距                                      */
      --pad: 20px;             /* 內距                                          */
      --maxw: 1220px;          /* 主要內容最大寬度                              */
      --title-size: clamp(28px, 3.6vw, 56px);
      --subtitle-size: clamp(20px, 2.4vw, 36px);
      --heading-size: clamp(16px, 1.6vw, 22px);
      --small: 12px;
    }

    /* ==========================
       全域 reset 與排版
       ========================== */
    *, *::before, *::after {
      box-sizing: border-box;
    }
    html, body {
      height: 100%;
    }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans TC", "PingFang TC", Arial, "Apple Color Emoji", "Segoe UI Emoji";
      color: var(--ink);
      background: linear-gradient(180deg, var(--bg-0) 0%, var(--bg-1) 45%, #c2e8ff 100%);
      letter-spacing: .2px;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    /* 外框容器，對應截圖的淺藍面板邊界 */
    .frame {
      max-width: calc(var(--maxw) + 120px);
      margin: 36px auto;
      background: linear-gradient(180deg, #d9f1ff 0, #d9f1ff 60%, #d3edff 100%);
      border: 2px solid #b9def9;
      border-radius: var(--radius-2);
      box-shadow: var(--shadow);
      padding: 36px 30px 40px 30px;
    }

    /* 頁首大標與副標（仿截圖置中） */
    .hero {
      text-align: center;
      user-select: none;
    }
    .hero h1 {
      margin: 0 0 6px 0;
      font-size: var(--title-size);
      font-weight: 900;
      letter-spacing: .1em;
      text-shadow: 0 1px 0 #fff, 0 8px 28px rgba(13,38,61,.15);
    }
    .hero h2 {
      margin: 10px 0 6px 0;
      font-size: var(--subtitle-size);
      color: var(--muted-2);
      font-weight: 800;
    }

    /* 可滑動區（卡片） */
    .carousel {
      position: relative;
      margin: 18px auto 8px auto;
      max-width: var(--maxw);
      padding: 0 62px; /* 讓左右箭頭不遮擋卡片 */
    }

    .track {
      display: grid;
      grid-template-columns: repeat(4, minmax(240px, 1fr));
      gap: var(--gap);
      align-items: stretch;
    }

    /* 卡片樣式 */
    .card {
      position: relative;
      background: var(--paper);
      border: 1px solid #e7f1fb;
      border-radius: var(--radius);
      box-shadow: 0 2px 0 rgba(255,255,255,.8) inset, 0 1px 0 rgba(0,0,0,.02) inset, var(--shadow);
      padding: calc(var(--pad) + 2px);
      display: flex;
      flex-direction: column;
      min-height: 360px;
      transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
      overflow: hidden;
    }
    .card:focus-within,
    .card:hover {
      transform: translateY(-2px);
      box-shadow: 0 0 0 4px var(--ring), var(--shadow);
      border-color: #cfe7ff;
    }

    .card-title {
      margin: 6px 0 8px 0;
      text-align: center;
      font-size: var(--heading-size);
      font-weight: 800;
      color: #204b9f;
      line-height: 1.35;
      min-height: 3.4em; /* 讓兩行標題時高度一致 */
    }

    /* 下載按鈕（小圖示置中） */
    .dl {
      display: grid;
      place-items: center;
      margin: 2px auto 10px auto;
      width: 46px;
      height: 46px;
      border-radius: 12px;
      background: linear-gradient(180deg, #eff7ff, #dff0ff);
      border: 1px solid #c7e2ff;
      cursor: pointer;
      transition: transform .2s ease;
    }
    .dl:active { transform: scale(.98); }
    .dl svg { width: 24px; height: 24px; fill: var(--muted-3); }

    /* 插圖區（用 SVG 矢量圖示重現截圖風格） */
    .art {
      flex: 1 1 auto;
      background: #f4f9ff;
      border: 1px dashed #d7e8ff;
      border-radius: 12px;
      display: grid;
      place-items: center;
      margin: 6px 0 10px 0;
      overflow: hidden;
    }
    .art svg { width: 78%; height: auto; }

    /* 意見回饋連結 */
    .feedback {
      text-align: center;
      margin-top: 6px;
      font-weight: 900;
      color: #1253df;
      text-decoration: none;
      padding: 8px 0 6px 0;
      border-top: 1px solid #e8f0fd;
      display: block;
    }
    .feedback:focus,
    .feedback:hover {
      text-decoration: underline;
    }

    /* 左右箭頭（導引） */
    .nav {
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      width: 42px;
      height: 42px;
      display: grid;
      place-items: center;
      border-radius: 50%;
      border: 1px solid #c9e2ff;
      background: linear-gradient(180deg,#ffffff,#eef6ff);
      box-shadow: var(--shadow);
      cursor: pointer;
      user-select: none;
      transition: transform .2s ease, box-shadow .2s ease;
    }
    .nav:active { transform: translateY(-50%) scale(.98); }
    .nav svg { width: 22px; height: 22px; fill: #1f4fd6; }
    .nav.left  { left: 12px; }
    .nav.right { right: 12px; }

    /* 回饋對話框（Modal） */
    .scrim {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, .48);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
      z-index: 40;
    }
    .scrim[aria-hidden="false"] { display: flex; }

    .dialog {
      width: min(720px, 92vw);
      background: var(--paper);
      border-radius: 20px;
      border: 1px solid #d7e8ff;
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .dialog header { 
      display: flex; 
      justify-content: space-between; 
      align-items: center; 
      padding: 16px 18px; 
      background: linear-gradient(180deg,#f6fbff,#ebf5ff);
      border-bottom: 1px solid #e2eeff;
    }
    .dialog header h3 { margin: 0; font-size: 18px; }
    .dialog header button { 
      border: 0; 
      background: transparent; 
      cursor: pointer; 
      padding: 6px; 
    }
    .dialog header button svg { width: 22px; height: 22px; fill: #3656d7; }

    .dialog form { padding: 18px; display: grid; gap: 12px; }
    .dialog label { font-size: 14px; font-weight: 700; }
    .dialog input, .dialog textarea, .dialog select {
      width: 100%;
      padding: 12px 14px;
      border: 1px solid #cfe3ff;
      border-radius: 10px;
      outline: none;
      box-shadow: 0 0 0 0 var(--ring);
      transition: box-shadow .18s ease, border-color .18s ease;
      font-size: 14px;
      background: #f9fcff;
    }
    .dialog input:focus,
    .dialog textarea:focus,
    .dialog select:focus {
      border-color: #9cc4ff;
      box-shadow: 0 0 0 4px var(--ring);
      background: #fff;
    }
    .dialog textarea { min-height: 120px; resize: vertical; }

    .dialog .actions { display: flex; gap: 10px; justify-content: flex-end; padding-top: 4px; }
    .btn {
      padding: 10px 16px;
      border-radius: 10px;
      border: 1px solid #c7dbff;
      cursor: pointer;
      background: linear-gradient(180deg,#ffffff,#eef6ff);
      font-weight: 700;
    }
    .btn.primary { 
      background: linear-gradient(180deg, #4f8bff, #3b74f6);
      color: #fff;
      border-color: #2d63e9;
    }

    /* Toast 小訊息 */
    .toast {
      position: fixed;
      left: 50%;
      bottom: 18px;
      transform: translateX(-50%) translateY(20px);
      background: #0b1220;
      color: #fff;
      padding: 10px 14px;
      border-radius: 10px;
      font-size: 14px;
      opacity: 0;
      transition: opacity .22s ease, transform .22s ease;
      z-index: 50;
      box-shadow: 0 10px 32px rgba(0,0,0,.35);
    }
    .toast.show {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }

    /* 響應式：窄螢幕下卡片改為兩欄/單欄 */
    @media (max-width: 1024px) {
      .carousel { padding: 0 44px; }
      .track { grid-template-columns: repeat(2, minmax(240px, 1fr)); }
    }
    @media (max-width: 640px) {
      .carousel { padding: 0 22px; }
      .track { grid-template-columns: 1fr; }
      .nav { display: none; }
    }

    /* 細節裝飾：進場動畫（非必要，純增加行數與質感） */
    .card { animation: fadeUp .5s ease both; }
    .card:nth-child(2) { animation-delay: .04s; }
    .card:nth-child(3) { animation-delay: .08s; }
    .card:nth-child(4) { animation-delay: .12s; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(6px); }
      to   { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>

<body>
  <main class="frame" aria-label="最新法令修正或宣導">
    <!-- 頁首區（大標、副標） -->
    <section class="hero" aria-describedby="subtitle">
      <h1>最新法令修正或宣導</h1>
      <h2 id="subtitle">運研所指引（原則）</h2>
    </section>

    <!-- 可滑動卡片區（含左右導引） -->
    <section class="carousel" aria-label="指引清單">
      <button class="nav left" type="button" aria-label="往左捲動">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.5 4.5a1.25 1.25 0 0 1 .9 2.14L11.04 12l5.36 5.36a1.25 1.25 0 1 1-1.77 1.77l-6.25-6.25a1.25 1.25 0 0 1 0-1.77l6.25-6.25c.24-.24.55-.36.87-.36Z"/></svg>
      </button>

      <div class="track" id="track">
        <!-- 卡片 1：人行空間改善原則 -->
        <article class="card" tabindex="-1">
          <h3 class="card-title">人行空間改善原則</h3>
          <button class="dl" data-file="人行空間改善原則.pdf" title="下載：人行空間改善原則">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 15.75c-.32 0-.62-.13-.84-.35l-3.4-3.4a1.19 1.19 0 1 1 1.68-1.68l1.58 1.58V4.75a1.25 1.25 0 1 1 2.5 0v7.15l1.58-1.58a1.19 1.19 0 0 1 1.68 1.68l-3.4 3.4c-.22.22-.52.35-.84.35Z"/><path d="M6.5 18.5a1.5 1.5 0 0 1-1.5-1.5v-.75a1 1 0 1 1 2 0v.25h10v-.25a1 1 0 1 1 2 0v.75a1.5 1.5 0 0 1-1.5 1.5h-11Z"/></svg>
          </button>
          <div class="art" aria-hidden="true">
            <!-- 斑馬線＋學童 SVG（簡化示意） -->
            <svg viewBox="0 0 256 180" role="img">
              <defs>
                <linearGradient id="zebra" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0" stop-color="#dde8f9"/>
                  <stop offset="1" stop-color="#ffffff"/>
                </linearGradient>
              </defs>
              <rect x="0" y="0" width="256" height="180" fill="#eaf4ff"/>
              <rect x="36" y="128" width="184" height="28" fill="url(#zebra)"/>
              <!-- zebra stripes -->
              <g fill="#cddaf2">
                <rect x="40" y="132" width="24" height="20"/>
                <rect x="72" y="132" width="24" height="20"/>
                <rect x="104" y="132" width="24" height="20"/>
                <rect x="136" y="132" width="24" height="20"/>
                <rect x="168" y="132" width="24" height="20"/>
                <rect x="200" y="132" width="16" height="20"/>
              </g>
              <!-- traffic light -->
              <g transform="translate(22,36)">
                <rect x="0" y="0" width="22" height="82" rx="4" fill="#2f3b5e"/>
                <circle cx="11" cy="16" r="6" fill="#cbd5e1"/>
                <circle cx="11" cy="40" r="6" fill="#fbbf24"/>
                <circle cx="11" cy="64" r="6" fill="#22c55e"/>
              </g>
              <!-- two kids -->
              <g transform="translate(84,58)">
                <circle cx="18" cy="14" r="10" fill="#ffd9c7"/>
                <rect x="8" y="26" width="20" height="28" rx="6" fill="#9ec3ff"/>
                <rect x="10" y="54" width="16" height="8" fill="#2f3b5e"/>
                <circle cx="70" cy="14" r="10" fill="#ffd9c7"/>
                <rect x="60" y="26" width="20" height="28" rx="6" fill="#9ec3ff"/>
                <rect x="62" y="54" width="16" height="8" fill="#2f3b5e"/>
              </g>
            </svg>
          </div>
          <a class="feedback" href="#" data-topic="人行空間改善原則">意見回饋</a>
        </article>

        <!-- 卡片 2：行人專用時相與行人早開時相設置原則 -->
        <article class="card" tabindex="-1">
          <h3 class="card-title">行人專用時相與行人<br/>早開時相設置原則</h3>
          <button class="dl" data-file="行人專用時相與早開時相設置原則.pdf" title="下載：行人專用時相與行人早開時相設置原則">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 15.75c-.32 0-.62-.13-.84-.35l-3.4-3.4a1.19 1.19 0 1 1 1.68-1.68l1.58 1.58V4.75a1.25 1.25 0 1 1 2.5 0v7.15l1.58-1.58a1.19 1.19 0 0 1 1.68 1.68l-3.4 3.4c-.22.22-.52.35-.84.35Z"/><path d="M6.5 18.5a1.5 1.5 0 0 1-1.5-1.5v-.75a1 1 0 1 1 2 0v.25h10v-.25a1 1 0 1 1 2 0v.75a1.5 1.5 0 0 1-1.5 1.5h-11Z"/></svg>
          </button>
          <div class="art" aria-hidden="true">
            <!-- 行人號誌按鈕／行人綠燈圖示 -->
            <svg viewBox="0 0 256 180" role="img">
              <rect width="256" height="180" fill="#eaf4ff"/>
              <rect x="86" y="20" width="84" height="140" rx="16" fill="#334155"/>
              <rect x="94" y="28" width="68" height="60" rx="12" fill="#383d47"/>
              <rect x="94" y="96" width="68" height="60" rx="12" fill="#16a34a"/>
              <!-- walking man -->
              <g transform="translate(115,112) scale(0.8)">
                <circle cx="16" cy="6" r="6" fill="#e6fff0"/>
                <path d="M10,22 L18,14 L24,22 L30,44 L24,44 L20,30 L14,36 L10,34 Z" fill="#e6fff0"/>
                <rect x="6" y="22" width="8" height="4" fill="#e6fff0"/>
              </g>
            </svg>
          </div>
          <a class="feedback" href="#" data-topic="行人專用時相與行人早開時相設置原則">意見回饋</a>
        </article>

        <!-- 卡片 3：改善機車交通環境原則及作法 -->
        <article class="card" tabindex="-1">
          <h3 class="card-title">改善機車交通環境原則<br/>及作法</h3>
          <button class="dl" data-file="改善機車交通環境原則及作法.pdf" title="下載：改善機車交通環境原則及作法">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 15.75c-.32 0-.62-.13-.84-.35l-3.4-3.4a1.19 1.19 0 1 1 1.68-1.68l1.58 1.58V4.75a1.25 1.25 0 1 1 2.5 0v7.15l1.58-1.58a1.19 1.19 0 0 1 1.68 1.68l-3.4 3.4c-.22.22-.52.35-.84.35Z"/><path d="M6.5 18.5a1.5 1.5 0 0 1-1.5-1.5v-.75a1 1 0 1 1 2 0v.25h10v-.25a1 1 0 1 1 2 0v.75a1.5 1.5 0 0 1-1.5 1.5h-11Z"/></svg>
          </button>
          <div class="art" aria-hidden="true">
            <!-- 機車 SVG（簡化） -->
            <svg viewBox="0 0 256 180" role="img">
              <rect width="256" height="180" fill="#eaf4ff"/>
              <g fill="#111827" transform="translate(20,100)">
                <circle cx="52" cy="40" r="22" fill="#2f3b5e"/>
                <circle cx="184" cy="40" r="22" fill="#2f3b5e"/>
                <rect x="40" y="36" width="128" height="8" rx="4" fill="#475569"/>
              </g>
              <path d="M70,106 C90,70 140,60 170,70 L200,80 L190,94 L156,96 L132,108 Z" fill="#2e2f36"/>
              <rect x="98" y="70" width="28" height="12" rx="6" fill="#94a3b8"/>
              <rect x="162" y="64" width="20" height="6" rx="3" fill="#94a3b8"/>
            </svg>
          </div>
          <a class="feedback" href="#" data-topic="改善機車交通環境原則及作法">意見回饋</a>
        </article>

        <!-- 卡片 4：校園周邊人行空間改善參考指引 -->
        <article class="card" tabindex="-1">
          <h3 class="card-title">校園周邊人行空間改善<br/>參考指引</h3>
          <button class="dl" data-file="校園周邊人行空間改善參考指引.pdf" title="下載：校園周邊人行空間改善參考指引">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 15.75c-.32 0-.62-.13-.84-.35l-3.4-3.4a1.19 1.19 0 1 1 1.68-1.68l1.58 1.58V4.75a1.25 1.25 0 1 1 2.5 0v7.15l1.58-1.58a1.19 1.19 0 0 1 1.68 1.68l-3.4 3.4c-.22.22-.52.35-.84.35Z"/><path d="M6.5 18.5a1.5 1.5 0 0 1-1.5-1.5v-.75a1 1 0 1 1 2 0v.25h10v-.25a1 1 0 1 1 2 0v.75a1.5 1.5 0 0 1-1.5 1.5h-11Z"/></svg>
          </button>
          <div class="art" aria-hidden="true">
            <!-- 牽手學童（簡化） -->
            <svg viewBox="0 0 256 180" role="img">
              <rect width="256" height="180" fill="#eaf4ff"/>
              <g transform="translate(54,54)">
                <circle cx="30" cy="16" r="12" fill="#ffd9c7"/>
                <rect x="16" y="30" width="28" height="34" rx="7" fill="#93c5fd"/>
                <rect x="20" y="64" width="20" height="8" fill="#2f3b5e"/>
              </g>
              <g transform="translate(152,54)">
                <circle cx="30" cy="16" r="12" fill="#ffd9c7"/>
                <rect x="16" y="30" width="28" height="34" rx="7" fill="#93c5fd"/>
                <rect x="20" y="64" width="20" height="8" fill="#2f3b5e"/>
              </g>
              <!-- hands -->
              <rect x="112" y="70" width="32" height="6" rx="3" fill="#f59e0b"/>
            </svg>
          </div>
          <a class="feedback" href="#" data-topic="校園周邊人行空間改善參考指引">意見回饋</a>
        </article>
      </div>

      <button class="nav right" type="button" aria-label="往右捲動">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8.5 4.5a1.25 1.25 0 0 0-.9 2.14L12.96 12l-5.36 5.36a1.25 1.25 0 1 0 1.77 1.77l6.25-6.25a1.25 1.25 0 0 0 0-1.77l-6.25-6.25c-.24-.24-.55-.36-.87-.36Z"/></svg>
      </button>
    </section>
  </main>

  <!-- 回饋表單 Modal -->
  <div class="scrim" id="scrim" aria-hidden="true" role="dialog" aria-modal="true">
    <div class="dialog" role="document">
      <header>
        <h3>意見回饋</h3>
        <button id="closeDialog" aria-label="關閉回饋對話框">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.4 5.1a1 1 0 0 0-1.3 1.5L10 11.5l-5 5a1 1 0 0 0 1.4 1.4l5-5 5 5a1 1 0 0 0 1.4-1.4l-5-5 4.9-4.9a1 1 0 0 0-1.4-1.4L11.4 10 6.4 5.1Z"/></svg>
        </button>
      </header>
      <form id="fbForm">
        <div>
          <label for="topic">主題</label>
          <input id="topic" name="topic" required placeholder="例如：人行空間改善原則" />
        </div>
        <div>
          <label for="name">您的姓名</label>
          <input id="name" name="name" placeholder="可留空" />
        </div>
        <div>
          <label for="email">電子郵件</label>
          <input id="email" name="email" type="email" placeholder="example@mail.com（可留空）" />
        </div>
        <div>
          <label for="msg">意見內容</label>
          <textarea id="msg" name="msg" required placeholder="請輸入您的建議或疑問……"></textarea>
        </div>
        <div class="actions">
          <button type="button" class="btn" id="cancel">取消</button>
          <button type="submit" class="btn primary">送出回饋</button>
        </div>
      </form>
    </div>
  </div>

  <!-- Toast 區 -->
  <div id="toast" class="toast" role="status" aria-live="polite"></div>

  <script>
    // ==========================
    // JS：互動邏輯（左右導引、下載、回饋對話框、Toast）
    // ==========================
    (function() {
      const track = document.getElementById('track');
      const left = document.querySelector('.nav.left');
      const right = document.querySelector('.nav.right');
      const scrim = document.getElementById('scrim');
      const fbForm = document.getElementById('fbForm');
      const topicInput = document.getElementById('topic');
      const closeDialog = document.getElementById('closeDialog');
      const cancelBtn = document.getElementById('cancel');
      const toast = document.getElementById('toast');

      // 左右捲動
      const unit = 320; // 每次大約捲一張卡片寬
      function scrollBy(dx) {
        track.scrollBy({ left: dx, behavior: 'smooth' });
      }
      left.addEventListener('click', () => scrollBy(-unit));
      right.addEventListener('click', () => scrollBy(+unit));

      // 鍵盤左右鍵支援
      document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') { scrollBy(-unit); }
        if (e.key === 'ArrowRight') { scrollBy(+unit); }
      });

      // 點擊「意見回饋」開啟 modal，並帶入主題
      document.querySelectorAll('.feedback').forEach(a => {
        a.addEventListener('click', (e) => {
          e.preventDefault();
          const topic = a.getAttribute('data-topic') || '';
          topicInput.value = topic;
          openDialog();
        });
      });

      // 下載按鈕：動態產生假檔供下載（示意用途）
      document.querySelectorAll('.dl').forEach(btn => {
        btn.addEventListener('click', () => {
          const filename = btn.getAttribute('data-file') || 'download.pdf';
          const content = `此為示意檔案：${filename}\n\n（請替換為實際檔案連結或後端串接）`;
          const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          a.remove();
          URL.revokeObjectURL(url);
          showToast(`已開始下載：${filename}`);
        });
      });

      // 對話框開關
      function openDialog() {
        scrim.setAttribute('aria-hidden', 'false');
        setTimeout(() => topicInput.focus(), 30);
      }
      function closeModal() {
        scrim.setAttribute('aria-hidden', 'true');
      }
      closeDialog.addEventListener('click', closeModal);
      cancelBtn.addEventListener('click', closeModal);
      scrim.addEventListener('click', (e) => {
        if (e.target === scrim) closeModal();
      });
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && scrim.getAttribute('aria-hidden') === 'false') {
          closeModal();
        }
      });

      // 送出回饋（純前端示意）
      fbForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(fbForm);
        const topic = formData.get('topic');
        const msg = formData.get('msg');
        if (!topic || !msg) {
          showToast('請填寫主題與意見內容');
          return;
        }
        closeModal();
        fbForm.reset();
        showToast('感謝您的回饋，我們已收到！');
      });

      // Toast 工具
      let toastTimer = null;
      function showToast(text) {
        toast.textContent = text;
        toast.classList.add('show');
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => toast.classList.remove('show'), 2200);
      }
    })();
  </script>
</body>
</html>
