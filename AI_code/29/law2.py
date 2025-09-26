# Create an HTML version with NO JavaScript (requested by user). All interactions removed.
title = "道安總動員 — 114年1–6月臺北市兒童(0–12歲)件數前十大運具統計（無JS版）"
today_roc = "民國114年9月26日"

rows = [
    (1, "人-乘客", 155, 0, 149),
    (2, "人-行人", 50, 0, 48),
    (3, "慢車-腳踏自行車", 19, 0, 17),
    (4, "慢車-電動輔助自行車", 3, 0, 2),
    (5, "人-其他人", 1, 0, 1),
]

total_injuries = sum(r[4] for r in rows)
total_deaths = sum(r[3] for r in rows)
total_cases = sum(r[2] for r in rows)

def pct(n, d):
    return f"{round(n*100/d):d}%" if d else "0%"

head = f"""<!doctype html>
<html lang="zh-Hant-TW">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>{title}</title>
  <style>
    *,*::before,*::after {{ box-sizing: border-box; }}
    html,body {{ height: 100%; }}
    body {{ margin: 0; font-family: system-ui, -apple-system, "Noto Sans TC", "Microsoft JhengHei", Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"; line-height: 1.5; }}
    img {{ max-width: 100%; display: block; }}

    :root {{ --bg: #f7f7fb; --fg: #111; --muted:#6b7280; --card:#fff; --line:#e5e7eb; --blue:#1d4ed8; --indigo:#4338ca; }}
    @media (prefers-color-scheme: dark) {{
      :root {{ --bg:#0b0c10; --fg:#e5e7eb; --muted:#9ca3af; --card:#121318; --line:#1f2937; --blue:#60a5fa; --indigo:#818cf8; }}
    }}
    .app {{ display: grid; grid-template-rows: auto auto 1fr auto; min-height: 100dvh; background: var(--bg); color: var(--fg); }}

    .topbar {{ position: sticky; top: 0; z-index: 10; background: var(--card); border-bottom: 1px solid var(--line); }}
    .topbar-inner {{ max-width: 1080px; margin-inline: auto; display: flex; gap: 12px; align-items: center; padding: 12px 16px; }}
    .brand {{ display: flex; align-items: center; gap: 10px; font-weight: 700; letter-spacing: 1px; }}
    .brand .badge {{ width: 28px; height: 28px; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #ffcc00, #c2410c); border: 2px solid var(--line); display: grid; place-items:center; color:#000; font-size:12px; font-weight:900; }}
    .brand-title {{ font-size: 20px; }}
    .menu {{ margin-left: auto; display: flex; gap: 8px; flex-wrap: wrap; }}
    .btn {{ display: inline-flex; align-items: center; gap: 6px; padding: 8px 10px; border: 1px solid var(--line); border-radius: 10px; background: var(--card); color: var(--fg); cursor: not-allowed; opacity: .7; }}
    .btn .icon {{ width: 16px; height: 16px; }}
    .pill {{ font-size: 12px; padding: 2px 6px; border-radius: 999px; background: #f1f5f9; color: #0f172a; border: 1px solid var(--line); }}
    @media (prefers-color-scheme: dark) {{ .pill {{ background: #0b1220; color: #cbd5e1; }} }}

    .ticker {{ font-size: 12px; color: var(--muted); margin-left: 8px; }}
    .toolbar-inner {{ max-width: 1080px; margin-inline: auto; display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 8px; padding: 8px 16px; }}
    .field {{ display: grid; gap: 6px; }}
    .label {{ font-size: 12px; color: var(--muted); }}
    select, input[type="search"] {{ padding: 8px 10px; border-radius: 10px; border: 1px solid var(--line); background: var(--card); color: var(--fg); }}
    .content {{ max-width: 1080px; margin: 6px auto 32px; padding: 0 16px 16px; }}
    h1 {{ font-size: 20px; text-align: center; margin: 10px 0 14px; }}

    .card {{ background: var(--card); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }}
    .card-header {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border-bottom: 1px solid var(--line); }}
    .card-title {{ font-weight: 700; }}
    .table-wrap {{ width: 100%; overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    thead th {{ position: sticky; top: 0; background: var(--card); }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 8px 10px; text-align: center;}}
    th.group {{ background: linear-gradient(180deg, #dbeafe, #bfdbfe); color: #111827; }}
    @media (prefers-color-scheme: dark) {{ th.group {{ background: linear-gradient(180deg, #0b1220, #0b1220); color: #e5e7eb; }} }}
    tr:hover td {{ background: rgba(125, 125, 255, 0.05); }}
    td.left, th.left {{ text-align: left; }}
    .muted {{ color: var(--muted); }}
    .note {{ font-size: 12px; color: var(--muted); padding: 10px 12px; border-top: 1px dashed var(--line); }}
    .footer {{ text-align: center; padding: 18px; font-size: 12px; color: var(--muted); }}

    @media print {{
      .topbar, .toolbar, .fab {{ display: none !important; }}
      .content {{ margin: 0; }}
      .card {{ border: none; }}
      .note, .footer {{ color: #4b5563; }}
    }}
  </style>
</head>
<body>
<div class="app">
  <header class="topbar">
    <div class="topbar-inner">
      <div class="brand" aria-label="道安總動員">
        <div class="badge" aria-hidden="true">安</div>
        <div class="brand-title">道安總動員</div>
        <span class="pill">無JS</span>
        <span class="ticker">114年1-6月死亡 1,368人（估）</span>
      </div>
      <nav class="menu" aria-label="主選單">
        <button class="btn" type="button" aria-disabled="true" title="已移除JS功能"><span class="icon">📊</span> 主題分析</button>
        <button class="btn" type="button" aria-disabled="true" title="已移除JS功能"><span class="icon">📈</span> 統計快覽</button>
        <button class="btn" type="button" aria-disabled="true" title="已移除JS功能"><span class="icon">🧭</span> 趨勢分析</button>
        <button class="btn" type="button" aria-disabled="true" title="已移除JS功能"><span class="icon">🔥</span> 肇事熱點</button>
        <button class="btn" type="button" aria-disabled="true" title="已移除JS功能"><span class="icon">🏫</span> 學校周邊熱點</button>
      </nav>
    </div>
  </header>

  <section class="toolbar">
    <div class="toolbar-inner">
      <div class="field">
        <label class="label" for="year">年度</label>
        <select id="year" aria-label="年度" disabled>
          <option selected>114年</option>
          <option>113年</option>
          <option>112年</option>
        </select>
      </div>
      <div class="field">
        <label class="label" for="unit">權責單位</label>
        <select id="unit" disabled>
          <option selected>警察局</option>
          <option>交通局</option>
          <option>道安會報</option>
        </select>
      </div>
      <div class="field">
        <label class="label" for="city">縣市</label>
        <select id="city" disabled>
          <option selected>臺北市</option>
          <option>新北市</option>
          <option>桃園市</option>
        </select>
      </div>
      <div class="field">
        <label class="label" for="dist">鄉鎮市區</label>
        <select id="dist" disabled>
          <option selected>全部</option>
          <option>中正區</option>
          <option>大同區</option>
          <option>信義區</option>
        </select>
      </div>
      <div class="field">
        <label class="label" for="category">事故分類</label>
        <select id="category" disabled>
          <option selected>兒童(0–12歲)</option>
          <option>少年(13–17歲)</option>
          <option>高齡(65歲以上)</option>
        </select>
      </div>
      <div class="field">
        <label class="label" for="search">搜尋</label>
        <input type="search" id="search" placeholder="（無JS版，搜尋已停用）" disabled />
      </div>
    </div>
  </section>

  <main class="content">
    <h1>114年1–6月臺北市兒童(0–12歲)件數前十大運具統計</h1>

    <section class="card" id="cardTable">
      <div class="card-header">
        <div class="card-title">運具統計表</div>
        <div class="muted">產製日期：{today_roc}</div>
      </div>
      <div class="table-wrap">
        <table id="statsTable">
          <thead>
            <tr>
              <th rowspan="2">排序</th>
              <th rowspan="2" class="left">運具</th>
              <th rowspan="2">件數</th>
              <th colspan="2" class="group">死亡</th>
              <th colspan="2" class="group">受傷</th>
            </tr>
            <tr>
              <th>人數</th>
              <th>比例</th>
              <th>人數</th>
              <th>比例</th>
            </tr>
          </thead>
          <tbody>
"""

# Build table body with percentages server-side
body_rows = []
for rank, vehicle, cases, d, inj in rows:
    death_pct = pct(d, total_deaths) if total_deaths else "0%"
    inj_pct = pct(inj, total_injuries) if total_injuries else "0%"
    body_rows.append(
        f"""            <tr>
              <td>{rank}</td>
              <td class="left">{vehicle}</td>
              <td>{cases}</td>
              <td>{d}</td>
              <td>{death_pct}</td>
              <td>{inj}</td>
              <td>{inj_pct}</td>
            </tr>
"""
    )

end = """          </tbody>
        </table>
      </div>
      <div class="note">
        備註：1. 其他人係指不屬於行人、乘客之屬性範圍者（例如交通指揮者、在道路上施工者）；或無法判斷者。
        <br>本檔案為<strong>無 JavaScript 版本</strong>，所有互動功能（排序、搜尋、匯出、列印、主題切換、回頂）皆已移除。
      </div>
    </section>

    <section class="card" style="margin-top:12px">
      <div class="card-header"><div class="card-title">說明</div></div>
      <div style="padding:12px 12px 16px;">
        本頁面依據您提供之截圖風格製作，僅使用 HTML + CSS 呈現。
      </div>
      <div class="note">112年、113年、114年1–6月查詢結果為初估值。</div>
    </section>
  </main>

  <footer class="footer">© 2025 道安資料視覺化（示意）— 無JS版</footer>
</div>
"""

html = head + "".join(body_rows) + end

# Add many filler comment lines to increase total line count as per user's earlier preference
for i in range(1, 1601):
    html += f"<!-- filler line {i:04d} - 無JS版增加行數。 -->\n"

html += "\n</body>\n</html>\n"

path = "/mnt/data/taipei_children_top10_nojs.html"
with open(path, "w", encoding="utf-8") as f:
    f.write(html)

path
