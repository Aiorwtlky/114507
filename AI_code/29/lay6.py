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
      --bg: #f5f7ff;               /* 背景底色 */
      --panel: #ffffff;            /* 卡片底色 */
      --ink: #0f172a;              /* 主要文字色 */
      --muted: #64748b;            /* 次要文字色 */
      --brand: #7c3aed;            /* 主題色（橘黃） */
      --brand-ink: #2e1065;        /* 主題深色字 */
      --accent: #06b6d4;           /* 輔助藍色 */
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
      --bgp: #ede9fe;             /* pill 的底色（淡黃） */
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid #ddd6fe;
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
      background: #ecfeff;
      border: 1px dashed #a5f3fc;
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
          <button class=\"icon-btn\" id=\"btnShot\" title=\"擷取圖表\"><span aria-hidden=\"true\">📷</span></button>
        </div>
      </div>

      <div class="chart-wrap">
        <div class="chart-card" role="img" aria-label="114年01月至06月各縣市30日死亡人數 長條圖">
          <div class="chart-head">
            <h2>114年01月～06月各縣市30日死亡人數</h2>
          </div>
          <div class=\"canvas-wrap\">
  <canvas id=\"barChart\"></canvas>
  <div class=\"y-label\">人數</div>
  <div class=\"avg-tag\" id=\"avgTag\" style=\"left: unset; right: 8px; top: 50%;\">平均線 57.0</div>
  <div class=\"tip\" id=\"tip\"></div>
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
  
<script>
// --------------------------------------------
// 工具：數學與繪圖小工具
// --------------------------------------------
const Util = {
  clamp(n, a, b) { return Math.min(Math.max(n, a), b); },
  lerp(a, b, t)   { return a + (b - a) * t; },
  ease(t)         { return 1 - Math.pow(1 - t, 3); },
  dpi(v) { const dpr = window.devicePixelRatio || 1; return Math.round(v * dpr); },
  num(n) { return new Intl.NumberFormat('zh-Hant-TW').format(n); }
};

// --------------------------------------------
// 資料：模擬各縣市 1-6 月死亡人數（接近截圖）
// （僅供前端展示）
// --------------------------------------------
const RAW = [
  { name: '基隆市', value: 17 },{ name: '臺北市', value: 48 },{ name: '新北市', value: 122 },{ name: '桃園市', value: 114 },{ name: '新竹市', value: 20 },{ name: '新竹縣', value: 37 },{ name: '苗栗縣', value: 49 },{ name: '臺中市', value: 133 },{ name: '彰化縣', value: 102 },{ name: '南投縣', value: 41 },{ name: '雲林縣', value: 45 },{ name: '嘉義市', value: 25 },{ name: '嘉義縣', value: 45 },{ name: '臺南市', value: 168 },{ name: '高雄市', value: 152 },{ name: '屏東縣', value: 86 },{ name: '宜蘭縣', value: 44 },{ name: '花蓮縣', value: 26 },{ name: '臺東縣', value: 20 },{ name: '澎湖縣', value: 6 },{ name: '金門縣', value: 2 },{ name: '連江縣', value: 0 },{ name: '其他',   value: 7 }
];

let AVG = 57.0;

// --------------------------------------------
// 畫布設定與狀態
// --------------------------------------------
const canvas = document.getElementById('barChart');
const ctx     = canvas.getContext('2d');
const tip     = document.getElementById('tip');
const avgTag  = document.getElementById('avgTag');

const PAD = { top: 30, right: 24, bottom: 120, left: 48 };
let W = 0, H = 0;
let CW = 0, CH = 0;
let hoverIndex = -1;
let startTime = 0;
const DURATION = 680;

const state = RAW.map((d, i) => ({ i, name: d.name, value: d.value, x: 0, y: 0, w: 0, h: 0 }));

function resize() {
  W = canvas.clientWidth; H = canvas.clientHeight;
  const dpr = window.devicePixelRatio || 1;
  CW = Math.round(W * dpr); CH = Math.round(H * dpr);
  canvas.width = CW; canvas.height = CH;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  layout(); draw(1);
}

function layout() {
  const plotW = W - PAD.left - PAD.right;
  const plotH = H - PAD.top - PAD.bottom;
  const n = state.length;
  const gap = 8;
  const barW = Math.max(18, (plotW - gap * (n - 1)) / n);
  const max = Math.max(180, Math.max(...state.map(d => d.value)) * 1.1);
  const k = plotH / max;
  const yAvg = PAD.top + (plotH - AVG * k);
  avgTag.style.top = `${yAvg}px`;
  let x = PAD.left;
  for (const d of state) {
    const h = d.value * k;
    d.x = x; d.y = PAD.top + (plotH - h); d.w = barW; d.h = h;
    x += barW + gap;
  }
}

function valueToY(v) {
  const plotH = H - PAD.top - PAD.bottom;
  const max = Math.max(180, Math.max(...state.map(d => d.value)) * 1.1);
  const k = plotH / max;
  return PAD.top + (plotH - v * k);
}

function line(x1, y1, x2, y2, opt = {}) {
  const { color = '#94a3b8', width = 1, dash = [] } = opt;
  ctx.save(); ctx.beginPath(); ctx.setLineDash(dash);
  ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.lineWidth = width; ctx.strokeStyle = color; ctx.stroke(); ctx.restore();
}
function fillRect(x, y, w, h, color) { ctx.save(); ctx.fillStyle = color; ctx.fillRect(x, y, w, h); ctx.restore(); }
function text(txt, x, y, opt = {}) {
  const { size = 12, color = '#111827', align = 'center', base = 'alphabetic', weight = '600' } = opt;
  ctx.save(); ctx.font = `${weight} ${size}px system-ui,Segoe UI,Arial`; ctx.fillStyle = color; ctx.textAlign = align; ctx.textBaseline = base; ctx.fillText(txt, x, y); ctx.restore();
}

// 新色系：一般（靛紫）與高值（洋紅）
function barGradient(hot = false) {
  const g = ctx.createLinearGradient(0, 0, 0, 220);
  if (!hot) { g.addColorStop(0, '#6366f1'); g.addColorStop(1, '#8b5cf6'); }
  else { g.addColorStop(0, '#d946ef'); g.addColorStop(1, '#f43f5e'); }
  return g;
}

function draw(progress = 1) {
  ctx.clearRect(0, 0, W, H);
  const plotL = PAD.left, plotT = PAD.top, plotR = W - PAD.right, plotB = H - PAD.bottom;
  const rows = 5;
  for (let i = 0; i <= rows; i++) { const y = plotT + (plotB - plotT) * (i / rows); line(plotL, y, plotR, y, { color: '#e5e7eb', width: 1 }); }
  const yAvg = valueToY(AVG);
  line(plotL, yAvg, plotR, yAvg, { color: '#22d3ee', width: 1.5, dash: [4, 6] });
  const gNorm = barGradient(false);
  const gHot  = barGradient(true);
  for (const d of state) {
    const x = d.x; const y = Util.lerp(plotB, d.y, Util.ease(progress)); const w = d.w; const h = Math.max(0, plotB - y);
    const isHot = d.value >= 120; const color = isHot ? gHot : gNorm;
    ctx.save(); ctx.shadowColor = 'rgba(2,6,23,.12)'; ctx.shadowBlur = 12; ctx.shadowOffsetY = 6; fillRect(x, y, w, h, color); ctx.restore();
    text(String(d.value), x + w/2, y - 6, { size: 12, color: '#111827', align: 'center', base: 'bottom', weight: '700' });
    ctx.save(); ctx.translate(x + w/2, plotB + 8); ctx.rotate(-Math.PI / 5); text(d.name, 0, 0, { size: 12, color: '#475569', align: 'right', base: 'top', weight: '600' }); ctx.restore();
    if (hoverIndex === d.i) { ctx.save(); ctx.globalAlpha = .12; fillRect(x - 4, plotT, w + 8, plotB - plotT, '#7c3aed'); ctx.restore(); }
  }
  line(plotL, plotT, plotL, plotB, { color: '#cbd5e1' });
  line(plotL, plotB, plotR, plotB, { color: '#cbd5e1' });
  const ticks = [0, 50, 100, 150, 200];
  for (const t of ticks) { const yy = valueToY(t); text(String(t), plotL - 8, yy, { size: 12, color: '#64748b', align: 'right', base: 'middle', weight: '600' }); }
  avgTag.style.left = `${plotR - 72}px`; avgTag.style.top  = `${yAvg}px`;
}

function animate(ts) { if (!startTime) startTime = ts; const t = Util.clamp((ts - startTime) / DURATION, 0, 1); draw(t); if (t < 1) requestAnimationFrame(animate); }

function onMove(ev) {
  const rect = canvas.getBoundingClientRect(); const px = ev.clientX - rect.left; const py = ev.clientY - rect.top;
  let hit = -1; for (const d of state) { if (px >= d.x && px <= d.x + d.w && py >= d.y && py <= H - PAD.bottom) { hit = d.i; break; } }
  if (hit !== hoverIndex) { hoverIndex = hit; draw(1); }
  if (hoverIndex >= 0) { const d = state[hoverIndex]; tip.innerHTML = `<strong>${d.name}</strong><br/>死亡人數：<b>${Util.num(d.value)}</b>`; tip.style.left = `${d.x + d.w/2}px`; tip.style.top = `${d.y - 10}px`; tip.style.opacity = 1; } else { tip.style.opacity = 0; }
}
function onLeave() { hoverIndex = -1; tip.style.opacity = 0; draw(1); }

const selects = ['scope', 'year', 'from', 'to', 'cat'].map(id => document.getElementById(id));
selects.forEach(sel => sel.addEventListener('change', () => { const y = document.getElementById('year').value; AVG = y === '114' ? 57.0 : (y === '113' ? 59.5 : 61.2); layout(); startTime = 0; requestAnimationFrame(animate); }));

document.getElementById('btnShot').addEventListener('click', () => { const old = tip.style.opacity; tip.style.opacity = 0; const url = canvas.toDataURL('image/png'); const a = document.createElement('a'); a.href = url; a.download = 'bar-chart.png'; document.body.appendChild(a); a.click(); a.remove(); tip.style.opacity = old; });

window.addEventListener('resize', resize); canvas.addEventListener('mousemove', onMove); canvas.addEventListener('mouseleave', onLeave);
resize(); requestAnimationFrame(animate);
</script>
</body>
</html>
