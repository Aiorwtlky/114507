# Create a long, self-contained HTML file (with HTML + CSS + JS in one file)
# that mimics the provided screenshot theme and includes interactive features.
from pathlib import Path

html = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>道安總動員｜大型車事故統計範例（離線示範頁）</title>
  <style>
    /* ================================
       基礎重置與變數
       ================================ */
    :root{
      --bg:#f7f8fb;
      --panel:#ffffff;
      --text:#1a1f36;
      --muted:#6b7280;
      --primary:#1163ff;
      --primary-600:#0f57e3;
      --line:#e5e7eb;
      --chip:#eff6ff;
      --accent:#0ea5e9;
      --danger:#ef4444;
      --ok:#10b981;
      --warn:#f59e0b;
    }
    *{box-sizing:border-box}
    html,body{height:100%}
    body{
      margin:0;
      font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,"Noto Sans TC",Arial,"Microsoft JhengHei",sans-serif;
      color:var(--text);
      background:linear-gradient(180deg,#f9fafb 0%, #eef2ff 120%);
    }
    a{color:var(--primary);text-decoration:none}
    a:hover{text-decoration:underline}

    /* ================================
       頂部導覽列
       ================================ */
    .topbar{
      position:sticky;top:0;z-index:50;
      background:rgba(255,255,255,.86);
      backdrop-filter:saturate(180%) blur(8px);
      border-bottom:1px solid var(--line);
    }
    .topbar-inner{
      display:flex;align-items:center;gap:14px;
      max-width:1200px;padding:10px 20px;margin:0 auto;
    }
    .logo{
      width:36px;height:36px;border-radius:50%;
      display:grid;place-items:center;color:white;
      background:conic-gradient(from 180deg,var(--accent),#6366f1,var(--primary));
      box-shadow:0 4px 12px rgba(0,0,0,.12) inset, 0 1px 0 rgba(255,255,255,.9);
      font-weight:700;letter-spacing:1px;
    }
    .title{font-size:20px;font-weight:800;letter-spacing:.08em}
    .tabs{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}
    .tab{
      padding:8px 12px;border:1px solid var(--line);
      border-radius:999px;background:#fff;color:#111827;
      display:inline-flex;align-items:center;gap:6px;
      cursor:pointer;user-select:none;
    }
    .tab.active{background:var(--chip);border-color:#bfdbfe;color:#1d4ed8}
    .tab:hover{box-shadow:0 1px 0 rgba(0,0,0,.05),0 2px 12px rgba(17,99,255,.08)}

    /* ================================
       容器與控制列
       ================================ */
    .container{max-width:1200px;margin:18px auto;padding:0 20px}
    .control{
      background:var(--panel);border:1px solid var(--line);
      border-radius:14px;padding:12px 12px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;
      box-shadow:0 8px 24px rgba(0,0,0,.04);
    }
    .control .row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
    .chip{
      padding:6px 10px;border-radius:10px;background:#f3f4f6;color:#111827;border:1px solid var(--line);
    }
    .select, .input{
      appearance:none;
      padding:8px 10px;border-radius:10px;border:1px solid var(--line);
      background:#fff;min-width:120px;color:#111827;
    }
    .btn{
      padding:8px 12px;border:1px solid var(--line);border-radius:10px;background:#fff;cursor:pointer;
    }
    .btn.primary{background:var(--primary);color:#fff;border-color:var(--primary-600)}
    .btn:hover{filter:brightness(.98)}
    .spacer{flex:1}
    .note{font-size:12px;color:var(--muted)}

    /* ================================
       卡片與表格樣式
       ================================ */
    .panel{
      background:var(--panel);border:1px solid var(--line);border-radius:14px;margin-top:14px;
      overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.04);
    }
    .panel .hd{display:flex;align-items:center;gap:10px;padding:12px 14px;border-bottom:1px solid var(--line);background:#fcfcff}
    .panel .hd h2{font-size:16px;margin:0}
    .tag{padding:3px 8px;border-radius:999px;background:#eef2ff;color:#3730a3;border:1px solid #c7d2fe;font-size:12px}
    .panel .bd{padding:10px;overflow:auto}
    .table{border-collapse:separate;border-spacing:0;width:100%;min-width:880px}
    .table th, .table td{border-right:1px solid var(--line);border-bottom:1px solid var(--line);padding:9px 8px;font-size:14px;white-space:nowrap}
    .table th{position:sticky;top:0;background:#fafbff;color:#111827;z-index:1}
    .table th:first-child, .table td:first-child{border-left:1px solid var(--line)}
    .table tr:first-child th{border-top:1px solid var(--line)}
    .table td{background:white}
    .table tr:nth-child(even) td{background:#fbfdff}
    .table .subhead{font-size:12px;color:#6b7280}
    .table .num{text-align:right;font-variant-numeric:tabular-nums}
    .table .left{text-align:left}
    .kpi-up{color:var(--ok);font-weight:700}
    .kpi-down{color:var(--danger);font-weight:700}
    .pin-left{position:sticky;left:0;background:linear-gradient(90deg, #ffffff 80%, rgba(255,255,255,0));z-index:2}

    .foot{
      display:flex;justify-content:space-between;align-items:center;gap:10px;
      padding:10px 14px;border-top:1px solid var(--line);color:var(--muted);font-size:12px;background:#fafafa;
    }

    /* ================================
       深色模式（可由 JS 切換）
       ================================ */
    body.dark{
      --bg:#0b1020;
      --panel:#0f1529;
      --text:#e5e7eb;
      --muted:#a9b1c0;
      --primary:#7aa2f7;
      --primary-600:#6b91d8;
      --line:#1f2937;
      --chip:#18223c;
      --accent:#7dcfff;
    }
    body.dark{background:linear-gradient(180deg,#0d1326 0%, #0b1020 120%)}
    body.dark .tab{background:#0b1327;color:#e5e7eb;border-color:#1f2937}
    body.dark .tab.active{background:#111c35;border-color:#1f2a49;color:#93c5fd}
    body.dark .table th{background:#0c142a}
    body.dark .table td{background:#0f172a}
    body.dark .table tr:nth-child(even) td{background:#101a32}
    body.dark .control, body.dark .panel{background:#0f1529;border-color:#1f2937}
    body.dark .foot{background:#0b1327;color:#9aa3b2}
    body.dark .btn{background:#0b1327;color:#e5e7eb;border-color:#1f2937}
    body.dark .select, body.dark .input{background:#0b1327;color:#e5e7eb;border-color:#1f2937}

    /* ================================
       響應式調整
       ================================ */
    @media (max-width:960px){
      .tabs{width:100%}
      .table{min-width:720px}
    }
    @media (max-width:640px){
      .topbar-inner{gap:10px}
      .title{font-size:18px}
      .select{min-width:100px}
      .table{min-width:640px}
    }
  </style>
</head>
<body>
  <!-- =========================================
       頂部導覽
       ========================================= -->
  <header class="topbar">
    <div class="topbar-inner">
      <div class="logo" aria-label="logo">安</div>
      <div class="title">道安總動員（示範頁）</div>
      <nav class="tabs" role="tablist" aria-label="主導航">
        <button class="tab active" data-tab="topic">主題分析</button>
        <button class="tab" data-tab="quick">統計快搜</button>
        <button class="tab" data-tab="geo">縣市鄉鎮與國道</button>
        <button class="tab" data-tab="trend">趨勢分析</button>
        <button class="tab" data-tab="danger">危險據點</button>
        <button class="tab" data-tab="school">學校周邊熱點</button>
      </nav>
    </div>
  </header>

  <main class="container">
    <!-- 控制列 -->
    <section class="control" aria-label="篩選器">
      <div class="row">
        <span class="chip">年 度</span>
        <select id="year" class="select" aria-label="年度">
          <option value="114" selected>114年</option>
          <option value="113">113年</option>
          <option value="112">112年</option>
        </select>

        <span class="chip">轄別</span>
        <select id="region" class="select" aria-label="轄別">
          <option value="臺北市" selected>臺北市</option>
          <option>新北市</option>
          <option>桃園市</option>
          <option>臺中市</option>
          <option>高雄市</option>
        </select>

        <span class="chip">區域</span>
        <select id="district" class="select" aria-label="行政區">
          <option value="全部" selected>全部</option>
          <option>中正區</option><option>大同區</option><option>中山區</option>
          <option>松山區</option><option>大安區</option><option>萬華區</option>
        </select>

        <span class="chip">事故類型</span>
        <select id="type" class="select" aria-label="事故類型">
          <option value="大型車事故" selected>大型車事故</option>
          <option value="大型車與自行車">大型車與自行車</option>
        </select>

        <input id="search" class="input" placeholder="快速搜尋（如：大貨車）" />
      </div>
      <div class="row" style="margin-left:auto">
        <button id="exportCsv" class="btn">匯出 CSV</button>
        <button id="toggleDark" class="btn">深色模式</button>
        <button id="reset" class="btn">重設</button>
        <button id="printBtn" class="btn">列印</button>
        <span class="note">資料期間：114年1月～6月　統計日：民國114年9月27日</span>
      </div>
    </section>

    <!-- 面板 1：大型車事故 -->
    <section class="panel" id="panel-main">
      <div class="hd">
        <h2>114年1～6月臺北市大型車左轉等事故統計</h2>
        <span class="tag">示範資料</span>
      </div>
      <div class="bd">
        <table class="table" id="mainTable" aria-describedby="大型車事故統計表">
          <thead>
            <tr>
              <th rowspan="2" class="left pin-left" data-sort="rank">排序</th>
              <th rowspan="2" class="left">當事者區分</th>
              <th colspan="3">件數</th>
              <th colspan="3">案件死亡人數</th>
              <th colspan="3">案件受傷人數</th>
            </tr>
            <tr>
              <th data-sort="lCount">左轉彎</th>
              <th data-sort="rCount">右轉彎</th>
              <th data-sort="sumCount">小計</th>
              <th data-sort="lDeath">左轉彎</th>
              <th data-sort="rDeath">右轉彎</th>
              <th data-sort="sumDeath">小計</th>
              <th data-sort="lInj">左轉彎</th>
              <th data-sort="rInj">右轉彎</th>
              <th data-sort="sumInj">小計</th>
            </tr>
          </thead>
          <tbody id="mainTbody">
            <!-- 由 JS 產生 -->
          </tbody>
        </table>
      </div>
      <div class="foot">
        <div>說明：表格可點欄位排序、可關鍵字搜尋；本頁為離線範例，並非正式統計。</div>
        <div id="summaryKpi">總計：-- 件；死亡 -- 人；受傷 -- 人</div>
      </div>
    </section>

    <!-- 面板 2：大型車與自行車 -->
    <section class="panel">
      <div class="hd">
        <h2>大型車與自行車事故統計（114年1～6月）</h2>
        <span class="tag">示範資料</span>
      </div>
      <div class="bd">
        <table class="table" id="bikeTable" aria-describedby="大型車與自行車事故統計">
          <thead>
            <tr>
              <th class="left pin-left">排序</th>
              <th class="left">當事者區分</th>
              <th>件數</th>
              <th>死亡人數</th>
              <th>受傷人數</th>
            </tr>
          </thead>
          <tbody id="bikeTbody">
            <!-- 由 JS 產生 -->
          </tbody>
        </table>
      </div>
      <div class="foot">
        <div>資料來源：示範合成資料；僅供版面與互動展示。</div>
        <div id="bikeKpi">總計：-- 件；死亡 -- 人；受傷 -- 人</div>
      </div>
    </section>

    <!-- 面板 3：小型視覺化（Canvas 簡易長條圖） -->
    <section class="panel">
      <div class="hd">
        <h2>可視化：各車種小計（件數）</h2>
        <span class="tag">Canvas</span>
      </div>
      <div class="bd">
        <canvas id="miniChart" height="200" aria-label="長條圖" role="img"></canvas>
      </div>
      <div class="foot">
        <div class="note">此圖以原生 Canvas 繪製，不依賴外部套件。</div>
        <div class="note">單位：件</div>
      </div>
    </section>

  </main>

  <footer class="foot" style="border-top:none;margin-top:18px">
    <div>© 2025 交通資料視覺化離線範例（ChatGPT 產生）。</div>
    <div>版本 v1.0 ｜
      <a href="#" id="scrollTop">回到頂端</a> ｜
      <a href="#" id="mockRefresh">重新整理</a>
    </div>
  </footer>

  <script>
    // =============================================
    // 假資料（接近螢幕截圖的內容）
    // =============================================
    const demoRows = [
      { rank:1, cat:"大貨車", lCount:4, rCount:10, lDeath:0, rDeath:2, lInj:6, rInj:8 },
      { rank:2, cat:"大客車", lCount:8, rCount:6,  lDeath:0, rDeath:1, lInj:6, rInj:14 },
      { rank:3, cat:"曳引車", lCount:1, rCount:2,  lDeath:0, rDeath:0, lInj:2, rInj:3 },
      { rank:4, cat:"半聯結車", lCount:0, rCount:2,  lDeath:0, rDeath:0, lInj:0, rInj:1 },
      { rank:5, cat:"全聯結車", lCount:0, rCount:1,  lDeath:0, rDeath:0, lInj:0, rInj:1 },
    ];

    const bikeRows = [
      { rank:1, cat:"大客車", lCount:1, rCount:1, lDeath:0, rDeath:1, lInj:1, rInj:2 },
      { rank:2, cat:"半聯結車", lCount:0, rCount:2, lDeath:0, rDeath:0, lInj:0, rInj:1 },
      { rank:3, cat:"大貨車", lCount:0, rCount:1, lDeath:0, rDeath:0, lInj:0, rInj:1 },
      { rank:4, cat:"全聯結車", lCount:0, rCount:0, lDeath:0, rDeath:0, lInj:0, rInj:0 },
      { rank:5, cat:"曳引車", lCount:0, rCount:0, lDeath:0, rDeath:0, lInj:0, rInj:0 },
    ];

    // 補充欄位：小計計算
    function enrich(rows){
      return rows.map(r=>({
        ...r,
        sumCount: (r.lCount||0) + (r.rCount||0),
        sumDeath: (r.lDeath||0) + (r.rDeath||0),
        sumInj: (r.lInj||0) + (r.rInj||0),
      }));
    }

    let mainData = enrich(demoRows);
    let bikeData = enrich(bikeRows);

    // =============================================
    // 工具函式
    // =============================================
    const $ = (sel, el=document)=>el.querySelector(sel);
    const $$ = (sel, el=document)=>Array.from(el.querySelectorAll(sel));

    function toCSV(rows, columns){
      const header = columns.map(c=>c.title).join(",");
      const body = rows.map(r=>columns.map(c=>String(r[c.key]).replace(/,/g,"")).join(",")).join("\\n");
      return header + "\\n" + body;
    }

    function download(filename, text){
      const blob = new Blob([text], {type:"text/csv;charset=utf-8"});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = filename; a.click();
      setTimeout(()=>URL.revokeObjectURL(url), 1000);
    }

    // =============================================
    // 表格渲染
    // =============================================
    function renderMainTable(rows){
      const tbody = $("#mainTbody");
      tbody.innerHTML = "";
      rows.forEach(r=>{
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="num pin-left">${r.rank}</td>
          <td class="left">${r.cat}</td>
          <td class="num">${r.lCount}</td>
          <td class="num">${r.rCount}</td>
          <td class="num"><strong>${r.sumCount}</strong></td>
          <td class="num ${r.lDeath>0?"kpi-down":""}">${r.lDeath}</td>
          <td class="num ${r.rDeath>0?"kpi-down":""}">${r.rDeath}</td>
          <td class="num"><strong>${r.sumDeath}</strong></td>
          <td class="num ${r.lInj>0?"kpi-up":""}">${r.lInj}</td>
          <td class="num ${r.rInj>0?"kpi-up":""}">${r.rInj}</td>
          <td class="num"><strong>${r.sumInj}</strong></td>
        `;
        tbody.appendChild(tr);
      });
      const sum = rows.reduce((a,b)=>({
        sumCount:a.sumCount+b.sumCount,
        sumDeath:a.sumDeath+b.sumDeath,
        sumInj:a.sumInj+b.sumInj
      }),{sumCount:0,sumDeath:0,sumInj:0});
      $("#summaryKpi").textContent = `總計：${sum.sumCount} 件；死亡 ${sum.sumDeath} 人；受傷 ${sum.sumInj} 人`;
    }

    function renderBikeTable(rows){
      const tbody = $("#bikeTbody");
      tbody.innerHTML = "";
      rows.forEach(r=>{
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="num pin-left">${r.rank}</td>
          <td class="left">${r.cat}</td>
          <td class="num">${r.sumCount}</td>
          <td class="num">${r.sumDeath}</td>
          <td class="num">${r.sumInj}</td>
        `;
        tbody.appendChild(tr);
      });
      const sum = rows.reduce((a,b)=>({
        sumCount:a.sumCount+b.sumCount,
        sumDeath:a.sumDeath+b.sumDeath,
        sumInj:a.sumInj+b.sumInj
      }),{sumCount:0,sumDeath:0,sumInj:0});
      $("#bikeKpi").textContent = `總計：${sum.sumCount} 件；死亡 ${sum.sumDeath} 人；受傷 ${sum.sumInj} 人`;
    }

    // =============================================
    // 排序互動
    // =============================================
    let sortKey = null;
    let sortAsc = true;

    function sortBy(key){
      sortAsc = (sortKey===key) ? !sortAsc : true;
      sortKey = key;
      const dir = sortAsc ? 1 : -1;
      mainData.sort((a,b)=> (a[key]-b[key]) * dir );
      renderMainTable(mainData);
      drawMiniChart(mainData);
    }

    $$("#mainTable thead [data-sort]").forEach(th=>{
      th.style.cursor = "pointer";
      th.title = "點擊排序";
      th.addEventListener("click", ()=> sortBy(th.dataset.sort));
    });

    // =============================================
    // 搜尋與過濾
    // =============================================
    $("#search").addEventListener("input", e=>{
      const kw = e.target.value.trim();
      const filtered = mainData.filter(r=>!kw || r.cat.includes(kw));
      renderMainTable(filtered);
    });

    $("#type").addEventListener("change", e=>{
      const tab = e.target.value;
      if(tab==="大型車與自行車"){
        $("#panel-main").scrollIntoView({behavior:"smooth", block:"start"});
        // 只是示範，不切換頁；保留在同頁
      }
    });

    // =============================================
    // 匯出、列印、重設、深色模式
    // =============================================
    const mainColumns = [
      {key:"rank", title:"排序"},
      {key:"cat", title:"當事者區分"},
      {key:"lCount", title:"件數-左轉彎"},
      {key:"rCount", title:"件數-右轉彎"},
      {key:"sumCount", title:"件數-小計"},
      {key:"lDeath", title:"死亡-左轉彎"},
      {key:"rDeath", title:"死亡-右轉彎"},
      {key:"sumDeath", title:"死亡-小計"},
      {key:"lInj", title:"受傷-左轉彎"},
      {key:"rInj", title:"受傷-右轉彎"},
      {key:"sumInj", title:"受傷-小計"},
    ];

    $("#exportCsv").addEventListener("click", ()=>{
      download("大型車事故統計.csv", toCSV(mainData, mainColumns));
    });

    $("#printBtn").addEventListener("click", ()=>{
      window.print();
    });

    $("#reset").addEventListener("click", ()=>{
      $("#year").value="114";
      $("#region").value="臺北市";
      $("#district").value="全部";
      $("#type").value="大型車事故";
      $("#search").value="";
      sortKey = null; sortAsc = true;
      mainData = enrich(demoRows);
      bikeData = enrich(bikeRows);
      renderMainTable(mainData);
      renderBikeTable(bikeData);
      drawMiniChart(mainData);
      window.scrollTo({top:0, behavior:"smooth"});
    });

    $("#toggleDark").addEventListener("click", ()=>{
      document.body.classList.toggle("dark");
      drawMiniChart(mainData);
    });

    $("#scrollTop").addEventListener("click", (e)=>{
      e.preventDefault();
      window.scrollTo({top:0, behavior:"smooth"});
    });

    $("#mockRefresh").addEventListener("click", (e)=>{
      e.preventDefault();
      const btn = e.target;
      const txt = btn.textContent;
      btn.textContent = "更新中…";
      setTimeout(()=>{
        btn.textContent = txt;
        // 模擬：將某一項件數 +1
        mainData[0].lCount += 1;
        mainData = enrich(mainData);
        renderMainTable(mainData);
        drawMiniChart(mainData);
      }, 700);
    });

    // =============================================
    // 簡易長條圖（原生 Canvas）
    // =============================================
    function drawMiniChart(rows){
      const c = $("#miniChart");
      const ctx = c.getContext("2d");
      const DPR = window.devicePixelRatio || 1;
      const W = c.clientWidth || c.parentElement.clientWidth - 20;
      const H = c.getAttribute("height");
      c.width = W * DPR;
      c.height = H * DPR;
      ctx.scale(DPR, DPR);

      // 背景
      ctx.clearRect(0,0,W,H);
      const dark = document.body.classList.contains("dark");
      ctx.fillStyle = dark ? "#0f172a" : "#ffffff";
      ctx.fillRect(0,0,W,H);

      // 軸線
      ctx.strokeStyle = dark ? "#23314d" : "#e5e7eb";
      ctx.lineWidth = 1;
      for(let i=0;i<=5;i++){
        const y = 20 + i*((H-40)/5);
        ctx.beginPath(); ctx.moveTo(40,y); ctx.lineTo(W-10,y); ctx.stroke();
      }

      // 資料
      const labels = rows.map(r=>r.cat);
      const values = rows.map(r=>r.sumCount);
      const max = Math.max(1, ...values);
      const barW = Math.max(20, (W-80)/values.length - 20);
      const baseY = H-30;

      values.forEach((v,i)=>{
        const x = 60 + i*(barW+20);
        const h = Math.max(1, (v/max)*(H-80));
        ctx.fillStyle = dark ? "#7aa2f7" : "#2563eb";
        ctx.fillRect(x, baseY - h, barW, h);
        // label
        ctx.fillStyle = dark ? "#cbd5e1" : "#111827";
        ctx.font = "12px system-ui, -apple-system";
        ctx.fillText(labels[i], x-4, baseY+14);
        ctx.fillText(String(v), x+barW/2-6, baseY - h - 6);
      });

      // 標題
      ctx.fillStyle = dark ? "#cbd5e1" : "#111827";
      ctx.font = "bold 14px system-ui, -apple-system";
      ctx.fillText("件數小計", 6, 16);
    }

    // =============================================
    // 初始化
    // =============================================
    function init(){
      renderMainTable(mainData);
      renderBikeTable(bikeData);
      drawMiniChart(mainData);
    }
    window.addEventListener("resize", ()=> drawMiniChart(mainData));
    init();
  </script>
</body>
</html>
"""

out = Path("/mnt/data/road_safety_dashboard.html")
out.write_text(html, encoding="utf-8")

# Count lines to satisfy the user's "more lines" request
num_lines = len(html.splitlines())
print(f"已產生 road_safety_dashboard.html（共 {num_lines} 行）")
