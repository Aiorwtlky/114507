<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>道安總動員｜大型車事故統計（純 HTML+CSS 版｜紫色系）</title>
  <style>
    /* ================================
       色系：紫 / 洋紅（無 JS）
       ================================ */
    :root{
      --bg:#f7f5ff;
      --panel:#ffffff;
      --text:#1d1633;
      --muted:#6b647a;
      --primary:#a855f7;      /* violet-500 */
      --line:#e9e5f5;
      --chip:#f5f3ff;         /* violet-50 */
      --accent:#e879f9;       /* fuchsia-400 */
    }
    *{box-sizing:border-box}
    html,body{height:100%}
    body{margin:0}
    .page{
      min-height:100%;
      color:var(--text);
      background:linear-gradient(180deg,#fbfaff 0%, #efe9ff 120%);
      font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,"Noto Sans TC",Arial,"Microsoft JhengHei",sans-serif;
    }

    /* CSS-only 深色模式（checkbox hack） */
    .theme-toggle:checked ~ .page{
      --bg:#0b0716;
      --panel:#120e22;
      --text:#ede9fe;
      --muted:#b3a9d3;
      --primary:#c084fc;
      --line:#2b2340;
      --chip:#1a1336;
      --accent:#f0abfc;
      background:linear-gradient(180deg,#0d0820 0%, #0a0716 120%);
    }

    a{color:var(--primary);text-decoration:none}
    a:hover{text-decoration:underline}

    /* 頂部導覽列 */
    .topbar{
      position:sticky;top:0;z-index:40;
      background:rgba(255,255,255,.86);
      backdrop-filter:saturate(180%) blur(8px);
      border-bottom:1px solid var(--line);
    }
    .theme-toggle:checked ~ .page .topbar{background:rgba(18,14,34,.86)}
    .topbar-inner{display:flex;align-items:center;gap:14px;max-width:1200px;padding:10px 20px;margin:0 auto}
    .logo{
      width:36px;height:36px;border-radius:50%;
      display:grid;place-items:center;color:#fff;
      background:conic-gradient(from 180deg,var(--accent),#c084fc,var(--primary));
      box-shadow:0 4px 12px rgba(0,0,0,.12) inset, 0 1px 0 rgba(255,255,255,.9);
      font-weight:700;letter-spacing:1px;
    }
    .title{font-size:20px;font-weight:800;letter-spacing:.08em}
    .tabs{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}
    .tab{
      padding:8px 12px;border:1px solid var(--line);
      border-radius:999px;background:#fff;color:#1f133a;
      display:inline-flex;align-items:center;gap:6px;
    }
    .theme-toggle:checked ~ .page .tab{background:#0f0a22;color:#ede9fe;border-color:#2b2340}
    .tab.active{background:var(--chip);border-color:#ddd6fe;color:#6d28d9}
    .theme-toggle:checked ~ .page .tab.active{background:#1a1336;border-color:#372a63;color:#c4b5fd}

    /* 容器與控制列 */
    .container{max-width:1200px;margin:18px auto;padding:0 20px}
    .control{
      background:var(--panel);border:1px solid var(--line);
      border-radius:14px;padding:12px 12px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;
      box-shadow:0 8px 24px rgba(0,0,0,.04);
    }
    .chip{padding:6px 10px;border-radius:10px;background:#faf5ff;color:#4b3b73;border:1px solid var(--line)}
    .select,.input{
      appearance:none;padding:8px 10px;border-radius:10px;border:1px solid var(--line);
      background:#fff;min-width:120px;color:#1f133a;
    }
    .theme-toggle:checked ~ .page .control,
    .theme-toggle:checked ~ .page .panel{background:#120e22;border-color:#2b2340}
    .theme-toggle:checked ~ .page .select,.theme-toggle:checked ~ .page .input{background:#0f0a22;color:#ede9fe;border-color:#2b2340}
    .note{font-size:12px;color:var(--muted)}

    /* 面板與表格 */
    .panel{
      background:var(--panel);border:1px solid var(--line);border-radius:14px;margin-top:14px;
      overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.04);
    }
    .panel .hd{display:flex;align-items:center;gap:10px;padding:12px 14px;border-bottom:1px solid var(--line);background:#fbfaff}
    .theme-toggle:checked ~ .page .panel .hd{background:#130e25}
    .panel .hd h2{font-size:16px;margin:0}
    .tag{padding:3px 8px;border-radius:999px;background:#f3e8ff;color:#6b21a8;border:1px solid #e9d5ff;font-size:12px}
    .panel .bd{padding:10px;overflow:auto}
    .table{border-collapse:separate;border-spacing:0;width:100%;min-width:880px}
    .table th,.table td{border-right:1px solid var(--line);border-bottom:1px solid var(--line);padding:9px 8px;font-size:14px;white-space:nowrap}
    .table th{position:sticky;top:0;background:#faf5ff;color:#1f133a;z-index:1}
    .theme-toggle:checked ~ .page .table th{background:#130e25;color:#ede9fe}
    .table th:first-child,.table td:first-child{border-left:1px solid var(--line)}
    .table tr:first-child th{border-top:1px solid var(--line)}
    .table td{background:#fff}
    .table tr:nth-child(even) td{background:#fdfaff}
    .theme-toggle:checked ~ .page .table td{background:#0f0a22;color:#ede9fe}
    .theme-toggle:checked ~ .page .table tr:nth-child(even) td{background:#100c24}
    .table .num{text-align:right;font-variant-numeric:tabular-nums}
    .table .left{text-align:left}
    .pin-left{position:sticky;left:0;background:linear-gradient(90deg, #ffffff 80%, rgba(255,255,255,0));z-index:2}
    .theme-toggle:checked ~ .page .pin-left{background:linear-gradient(90deg, #0f0a22 80%, rgba(15,10,34,0))}

    .foot{
      display:flex;justify-content:space-between;align-items:center;gap:10px;
      padding:10px 14px;border-top:1px solid var(--line);color:var(--muted);font-size:12px;background:#faf7ff;
    }
    .theme-toggle:checked ~ .page .foot{background:#0f0a22;color:#b3a9d3}

    /* 響應式 */
    @media (max-width:960px){ .table{min-width:720px} }
    @media (max-width:640px){ .table{min-width:640px} }

    /* 列印 */
    @media print{
      .topbar,.theme-switch,.note-print{display:none !important}
      .container{margin:0;padding:0}
      .panel{box-shadow:none;border-color:#bbb}
    }
  </style>
</head>
<body>
  <!-- CSS-only 深色模式切換器（無 JS） -->
  <input type="checkbox" id="theme" class="theme-toggle" hidden />
  <div class="page">
    <header class="topbar">
      <div class="topbar-inner">
        <div class="logo" aria-label="logo">安</div>
        <div class="title">道安總動員（純前端示範｜紫色系）</div>
        <nav class="tabs" role="tablist" aria-label="主導航">
          <span class="tab active">主題分析</span>
          <span class="tab">統計快搜</span>
          <span class="tab">縣市鄉鎮與國道</span>
          <span class="tab">趨勢分析</span>
          <span class="tab">危險據點</span>
          <span class="tab">學校周邊熱點</span>
        </nav>
      </div>
    </header>

    <main class="container">
      <!-- 控制列（展示用，無 JS 事件） -->
      <section class="control" aria-label="篩選器">
        <div class="chip">年 度</div>
        <select class="select" aria-label="年度"><option selected>114年</option><option>113年</option><option>112年</option></select>
        <div class="chip">轄別</div>
        <select class="select" aria-label="轄別"><option selected>臺北市</option><option>新北市</option><option>桃園市</option><option>臺中市</option><option>高雄市</option></select>
        <div class="chip">區域</div>
        <select class="select" aria-label="行政區"><option selected>全部</option><option>中正區</option><option>大同區</option><option>中山區</option><option>松山區</option><option>大安區</option><option>萬華區</option></select>
        <div class="chip">事故類型</div>
        <select class="select" aria-label="事故類型"><option selected>大型車事故</option><option>大型車與自行車</option></select>

        <label class="theme-switch" for="theme" style="margin-left:auto;display:flex;align-items:center;gap:8px;cursor:pointer">
          <span class="note">切換深色模式</span>
          <span style="width:42px;height:26px;border-radius:999px;border:1px solid var(--line);background:#fff;position:relative;display:inline-block">
            <span style="position:absolute;left:3px;top:3px;width:20px;height:20px;border-radius:50%;background:linear-gradient(180deg,#e9d5ff,#c4b5fd)"></span>
          </span>
        </label>
      </section>

      <!-- 面板 1：大型車事故 -->
      <section class="panel">
        <div class="hd">
          <h2>114年1～6月臺北市大型車左／右轉事故統計</h2>
          <span class="tag">靜態資料</span>
        </div>
        <div class="bd">
          <table class="table" aria-describedby="大型車事故統計表">
            <thead>
              <tr>
                <th rowspan="2" class="left pin-left">排序</th>
                <th rowspan="2" class="left">當事者區分</th>
                <th colspan="3">件數</th>
                <th colspan="3">案件死亡人數</th>
                <th colspan="3">案件受傷人數</th>
              </tr>
              <tr>
                <th>左轉彎</th><th>右轉彎</th><th>小計</th>
                <th>左轉彎</th><th>右轉彎</th><th>小計</th>
                <th>左轉彎</th><th>右轉彎</th><th>小計</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="num pin-left">1</td>
                <td class="left">大貨車</td>
                <td class="num">4</td><td class="num">10</td><td class="num"><strong>14</strong></td>
                <td class="num">0</td><td class="num">2</td><td class="num"><strong>2</strong></td>
                <td class="num">6</td><td class="num">8</td><td class="num"><strong>14</strong></td>
              </tr>
              <tr>
                <td class="num pin-left">2</td>
                <td class="left">大客車</td>
                <td class="num">8</td><td class="num">6</td><td class="num"><strong>14</strong></td>
                <td class="num">0</td><td class="num">1</td><td class="num"><strong>1</strong></td>
                <td class="num">6</td><td class="num">14</td><td class="num"><strong>20</strong></td>
              </tr>
              <tr>
                <td class="num pin-left">3</td>
                <td class="left">曳引車</td>
                <td class="num">1</td><td class="num">2</td><td class="num"><strong>3</strong></td>
                <td class="num">0</td><td class="num">0</td><td class="num"><strong>0</strong></td>
                <td class="num">2</td><td class="num">3</td><td class="num"><strong>5</strong></td>
              </tr>
              <tr>
                <td class="num pin-left">4</td>
                <td class="left">半聯結車</td>
                <td class="num">0</td><td class="num">2</td><td class="num"><strong>2</strong></td>
                <td class="num">0</td><td class="num">0</td><td class="num"><strong>0</strong></td>
                <td class="num">0</td><td class="num">1</td><td class="num"><strong>1</strong></td>
              </tr>
              <tr>
                <td class="num pin-left">5</td>
                <td class="left">全聯結車</td>
                <td class="num">0</td><td class="num">1</td><td class="num"><strong>1</strong></td>
                <td class="num">0</td><td class="num">0</td><td class="num"><strong>0</strong></td>
                <td class="num">0</td><td class="num">1</td><td class="num"><strong>1</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="foot">
          <div>說明：本頁為純 HTML + CSS 示範，無任何 JavaScript。</div>
          <div>總計：34 件；死亡 3 人；受傷 41 人</div>
        </div>
      </section>

      <!-- 面板 2：大型車與自行車 -->
      <section class="panel">
        <div class="hd">
          <h2>大型車與自行車事故統計（114年1～6月）</h2>
          <span class="tag">靜態資料</span>
        </div>
        <div class="bd">
          <table class="table" aria-describedby="大型車與自行車事故統計">
            <thead>
              <tr>
                <th class="left pin-left">排序</th>
                <th class="left">當事者區分</th>
                <th>件數</th>
                <th>死亡人數</th>
                <th>受傷人數</th>
              </tr>
            </thead>
            <tbody>
              <tr><td class="num pin-left">1</td><td class="left">大客車</td><td class="num">2</td><td class="num">1</td><td class="num">3</td></tr>
              <tr><td class="num pin-left">2</td><td class="left">半聯結車</td><td class="num">2</td><td class="num">0</td><td class="num">1</td></tr>
              <tr><td class="num pin-left">3</td><td class="left">大貨車</td><td class="num">1</td><td class="num">0</td><td class="num">1</td></tr>
              <tr><td class="num pin-left">4</td><td class="left">全聯結車</td><td class="num">0</td><td class="num">0</td><td class="num">0</td></tr>
              <tr><td class="num pin-left">5</td><td class="left">曳引車</td><td class="num">0</td><td class="num">0</td><td class="num">0</td></tr>
            </tbody>
          </table>
        </div>
        <div class="foot">
          <div>資料來源：示範合成資料；僅供版面展示。</div>
          <div>總計：5 件；死亡 1 人；受傷 5 人</div>
        </div>
      </section>

      <!-- 面板 3：列印提示 -->
      <section class="panel">
        <div class="hd"><h2>列印提示</h2><span class="tag">CSS</span></div>
        <div class="bd"><p class="note">若需列印，請直接使用瀏覽器「列印」功能（Windows：Ctrl+P／macOS：⌘+P）。本頁已提供 @media print 樣式。</p></div>
      </section>
    </main>

    <footer class="foot" style="border-top:none;margin-top:18px">
      <div>© 2025 交通資料視覺化離線範例（ChatGPT 產生）。</div>
      <div class="note-print">版本 v2.0（無 JS｜紫色系）</div>
    </footer>
  </div>
</body>
</html>
