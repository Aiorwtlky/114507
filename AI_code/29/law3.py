<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>道安總動員｜大型車事故統計（純 HTML+CSS 版本）</title>
  <style>
    :root{
      --bg:#f7f8fb;
      --panel:#ffffff;
      --text:#1a1f36;
      --muted:#6b7280;
      --primary:#1163ff;
      --line:#e5e7eb;
      --chip:#eff6ff;
      --accent:#0ea5e9;
    }
    *{box-sizing:border-box} html,body{height:100%} body{margin:0}
    .page{min-height:100%;color:var(--text);background:linear-gradient(180deg,#f9fafb 0%, #eef2ff 120%);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,"Noto Sans TC",Arial,"Microsoft JhengHei",sans-serif}
    .theme-toggle:checked ~ .page{--bg:#0b1020;--panel:#0f1529;--text:#e5e7eb;--muted:#a9b1c0;--primary:#7aa2f7;--line:#1f2937;--chip:#18223c;--accent:#7dcfff;background:linear-gradient(180deg,#0d1326 0%, #0b1020 120%)}
    a{color:var(--primary);text-decoration:none} a:hover{text-decoration:underline}
    .topbar{position:sticky;top:0;z-index:40;background:rgba(255,255,255,.86);backdrop-filter:saturate(180%) blur(8px);border-bottom:1px solid var(--line)}
    .theme-toggle:checked ~ .page .topbar{background:rgba(15,21,41,.86)}
    .topbar-inner{display:flex;align-items:center;gap:14px;max-width:1200px;padding:10px 20px;margin:0 auto}
    .logo{width:36px;height:36px;border-radius:50%;display:grid;place-items:center;color:white;background:conic-gradient(from 180deg,var(--accent),#6366f1,var(--primary));box-shadow:0 4px 12px rgba(0,0,0,.12) inset, 0 1px 0 rgba(255,255,255,.9);font-weight:700;letter-spacing:1px}
    .title{font-size:20px;font-weight:800;letter-spacing:.08em}
    .tabs{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}
    .tab{padding:8px 12px;border:1px solid var(--line);border-radius:999px;background:#fff;color:#111827;display:inline-flex;align-items:center;gap:6px}
    .theme-toggle:checked ~ .page .tab{background:#0b1327;color:#e5e7eb;border-color:#1f2937}
    .tab.active{background:var(--chip);border-color:#bfdbfe;color:#1d4ed8}
    .theme-toggle:checked ~ .page .tab.active{background:#111c35;border-color:#1f2a49;color:#93c5fd}
    .container{max-width:1200px;margin:18px auto;padding:0 20px}
    .control{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:12px 12px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;box-shadow:0 8px 24px rgba(0,0,0,.04)}
    .chip{padding:6px 10px;border-radius:10px;background:#f3f4f6;color:#111827;border:1px solid var(--line)}
    .select,.input{appearance:none;padding:8px 10px;border-radius:10px;border:1px solid var(--line);background:#fff;min-width:120px;color:#111827}
    .theme-toggle:checked ~ .page .control,.theme-toggle:checked ~ .page .panel{background:#0f1529;border-color:#1f2937}
    .theme-toggle:checked ~ .page .select,.theme-toggle:checked ~ .page .input{background:#0b1327;color:#e5e7eb;border-color:#1f2937}
    .note{font-size:12px;color:var(--muted)}
    .panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin-top:14px;overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.04)}
    .panel .hd{display:flex;align-items:center;gap:10px;padding:12px 14px;border-bottom:1px solid var(--line);background:#fcfcff}
    .theme-toggle:checked ~ .page .panel .hd{background:#0c142a}
    .panel .hd h2{font-size:16px;margin:0}
    .tag{padding:3px 8px;border-radius:999px;background:#eef2ff;color:#3730a3;border:1px solid #c7d2fe;font-size:12px}
    .panel .bd{padding:10px;overflow:auto}
    .table{border-collapse:separate;border-spacing:0;width:100%;min-width:880px}
    .table th,.table td{border-right:1px solid var(--line);border-bottom:1px solid var(--line);padding:9px 8px;font-size:14px;white-space:nowrap}
    .table th{position:sticky;top:0;background:#fafbff;color:#111827;z-index:1}
    .theme-toggle:checked ~ .page .table th{background:#0c142a;color:#e5e7eb}
    .table th:first-child,.table td:first-child{border-left:1px solid var(--line)}
    .table tr:first-child th{border-top:1px solid var(--line)}
    .table td{background:white}
    .table tr:nth-child(even) td{background:#fbfdff}
    .theme-toggle:checked ~ .page .table td{background:#0f172a;color:#e5e7eb}
    .theme-toggle:checked ~ .page .table tr:nth-child(even) td{background:#101a32}
    .table .num{text-align:right;font-variant-numeric:tabular-nums} .table .left{text-align:left}
    .pin-left{position:sticky;left:0;background:linear-gradient(90deg, #ffffff 80%, rgba(255,255,255,0));z-index:2}
    .theme-toggle:checked ~ .page .pin-left{background:linear-gradient(90deg, #0f172a 80%, rgba(15,23,42,0))}
    .foot{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 14px;border-top:1px solid var(--line);color:var(--muted);font-size:12px;background:#fafafa}
    .theme-toggle:checked ~ .page .foot{background:#0b1327;color:#9aa3b2}
    @media (max-width:960px){.table{min-width:720px}} @media (max-width:640px){.table{min-width:640px}}
    @media print{.topbar,.theme-switch,.note-print{display:none !important} .container{margin:0;padding:0} .panel{box-shadow:none;border-color:#ccc}}
  </style>
</head>
<body>
  <input type="checkbox" id="theme" class="theme-toggle" hidden />
  <div class="page">
    <header class="topbar">
      <div class="topbar-inner">
        <div class="logo" aria-label="logo">安</div>
        <div class="title">道安總動員（純前端示範）</div>
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
