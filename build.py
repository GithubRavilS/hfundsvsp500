#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
copy = json.loads((root / "copy-gemini.json").read_text(encoding="utf-8"))
dca = json.loads((root / "dca-data.json").read_text(encoding="utf-8"))
m = dca["meta"]
years = dca["years"]
monthly = dca["monthly"]
labels = [r["ym"] for r in monthly]
inv = [r["inv"] for r in monthly]
val = [r["val"] for r in monthly]
val_now = val[:-1] + [m["value_now"]]
dca_js = json.dumps({"labels": labels, "inv": inv, "val": val_now}, ensure_ascii=False)
years_rows = "".join(
    f'      <tr><td>{y["y"]}</td><td class="n">${y["invested"]:,}</td><td class="n">{y["btc"]:.4f}</td>'
    f'<td class="n">${y["avg"]:,.0f}</td><td class="n">${y["value"]:,.0f}</td>'
    f'<td class="n">{y["ret_pct"]:+.1f}%</td></tr>\n'
    for y in years
)

spot_now = f"{m['spot_now']:,.0f}"
ret_now = f"{m['ret_now']:.0f}"
invested = f"{m['invested']:,.0f}"
btc = f"{m['btc']:.4f}"
avg_cost = f"{m['avg_cost']:,.0f}"
value_now = f"{m['value_now']:,.0f}"
value_old = f"{m['value_old']:,.0f}"
pnl_now = f"{m['pnl_now']:,.0f}"
spot_old = f"{m['spot_old']:,.0f}"
ret_old = f"{m['ret_old']:.0f}"
months = str(m["months"])
as_of_old = m["as_of_old"]
as_of_now = m["as_of_now"]


def esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def scrub_inline(html: str) -> str:
    """Drop Gemini inline styles that fight the dark theme."""
    html = re.sub(r'\sstyle="[^"]*"', "", html)
    html = html.replace("<h2>", "<p><b>").replace("</h2>", "</b></p>")
    return html


def study_block(num: int, key: str, chart_id: str, sources_html: str) -> str:
    s = copy[key]
    return f"""
  <article class="study" id="study-{key}">
    <h3>{num}. {esc(s['title'])}</h3>
    <dl class="meta">
      <dt>Кто</dt><dd>{esc(s['who'])}</dd>
      <dt>Период</dt><dd>{esc(s['period'])}</dd>
      <dt>Данные</dt><dd>{s['data']}</dd>
      <dt>Ссылки</dt><dd>{sources_html}</dd>
    </dl>
    <div class="explain">{s['explain_html']}</div>
    <div class="box" style="margin-top:1rem">
      <div class="chart tall"><canvas id="{chart_id}"></canvas></div>
      <p class="err" id="err-{chart_id}">График не загрузился.</p>
      <p class="note">{esc(s['chart_caption'])}</p>
    </div>
  </article>
"""


eras_html = "\n".join(
    f'    <div class="box"><h4>{esc(e["title"])}</h4>'
    f'<p class="muted" style="margin:0">{esc(e["text"])}</p></div>'
    for e in copy["eras"]
)

sources = {
    "bogle": '<a href="https://boglecenter.net/wp-content/uploads/JCB_AXA_10-01.pdf" target="_blank" rel="noopener">PDF доклада Богла</a>',
    "morningstar": '<a href="https://assets.contentstack.io/v3/assets/blt4eb669caa7dc65b2/blte7224d06fe1faf84/66df6bf5a193e5d7e23bb9c9/Morningstar_US_Active_Passive_Barometer_Mid_Year_2024.pdf" target="_blank" rel="noopener">Morningstar Active/Passive Barometer (PDF)</a>',
    "spiva": '<a href="https://www.spglobal.com/spdji/en/research-insights/spiva/" target="_blank" rel="noopener">хаб SPIVA</a> · <a href="https://www.spglobal.com/spdji/en/documents/spiva/spiva-us-year-end-2024.pdf" target="_blank" rel="noopener">PDF YE 2024</a>',
    "sp20": '<a href="https://www.spglobal.com/spdji/en/documents/research/research-returns-values-and-outcomes-a-counterfactual-history.pdf" target="_blank" rel="noopener">S&amp;P: Returns, Values, and Outcomes (PDF)</a>',
    "hfr": '<a href="https://www.hfr.com/hfr-indices/compare-hfr-index-types/" target="_blank" rel="noopener">типы индексов HFR</a> · <a href="https://riabiz.com/charts/sp-500-vs-hedge-funds" target="_blank" rel="noopener">RIABiz: S&amp;P vs hedge funds</a>',
    "buffett": '<a href="https://longnow.org/ideas/warren-buffett-wins-million-dollar-long-bet/" target="_blank" rel="noopener">Long Now — разбор спора</a> · <a href="https://www.ft.com/content/3f449299-318c-4c8f-ab7a-bb3fa7221f9c" target="_blank" rel="noopener">Financial Times</a>',
}

studies = (
    study_block(1, "bogle", "chart-bogle", sources["bogle"])
    + study_block(2, "morningstar", "chart-morningstar", sources["morningstar"])
    + study_block(3, "spiva", "chart-spiva", sources["spiva"])
    + study_block(4, "sp20", "chart-sp20", sources["sp20"])
    + study_block(5, "hfr", "chart-hfr", sources["hfr"])
    + study_block(6, "buffett", "chart-buffett", sources["buffett"])
)

html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>H Funds — широкий рынок против ручного отбора</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Spectral:ital,wght@0,500;0,700;1,500&display=swap" rel="stylesheet" />
<script src="./chart.umd.min.js"></script>
<style>
:root{{--bg:#0b1210;--card:#141c19;--line:rgba(220,235,225,.12);--text:#eef6f1;--muted:#8fa197;--acc:#2db88a;--gold:#d4a017;--bad:#e35d4d;--max:920px}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:Manrope,system-ui,sans-serif;line-height:1.75;
background-image:radial-gradient(ellipse 70% 40% at 10% -10%,rgba(45,184,138,.18),transparent 55%),radial-gradient(ellipse 50% 35% at 90% 0%,rgba(212,160,23,.1),transparent 50%)}}
.wrap{{width:min(var(--max),calc(100% - 2rem));margin:0 auto}}
a{{color:var(--acc)}}
nav.toc{{position:sticky;top:0;z-index:20;backdrop-filter:blur(12px);background:rgba(11,18,16,.85);border-bottom:1px solid var(--line);padding:.7rem 0;font-size:.78rem}}
nav.toc .wrap{{display:flex;gap:.9rem;flex-wrap:wrap;align-items:center}}
nav.toc a{{color:var(--muted);text-decoration:none}}nav.toc a:hover{{color:var(--text)}}
.hero{{padding:4.2rem 0 2.8rem}}
.badge{{display:inline-block;padding:.25rem .65rem;border:1px solid var(--line);border-radius:999px;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--acc);margin-bottom:1rem}}
h1{{font-family:Spectral,Georgia,serif;font-size:clamp(2rem,5vw,3.2rem);line-height:1.12;margin:0 0 1.1rem;max-width:22ch}}
.lead{{font-size:1.16rem;color:var(--muted);max-width:62ch;margin:0 0 1.6rem}}
.thesis{{background:linear-gradient(145deg,rgba(45,184,138,.14),transparent 60%),var(--card);border:1px solid var(--line);border-radius:22px;padding:1.5rem 1.6rem;margin:1.5rem 0}}
.thesis strong{{color:var(--acc)}}
.kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1.6rem}}
@media(max-width:800px){{.kpis{{grid-template-columns:1fr}}}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:1.15rem}}
.kpi em{{display:block;font-style:normal;font-size:.78rem;color:var(--muted)}}
.kpi b{{display:block;font-size:1.65rem;margin:.25rem 0;color:var(--bad)}}
.kpi b.ok{{color:var(--acc)}}.kpi b.gold{{color:var(--gold)}}
.kpi span{{font-size:.86rem;color:var(--muted)}}
section{{padding:3rem 0;border-top:1px solid var(--line)}}
h2{{font-family:Spectral,Georgia,serif;font-size:clamp(1.4rem,3.2vw,2.1rem);margin:0 0 .85rem;line-height:1.25}}
h3{{font-size:1.12rem;margin:0 0 .55rem}}
p,li{{font-size:1.05rem}}.muted{{color:var(--muted)}}
.box{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:1.3rem 1.4rem;margin:1.1rem 0}}
.two{{display:grid;grid-template-columns:1.05fr .95fr;gap:1.1rem}}@media(max-width:820px){{.two{{grid-template-columns:1fr}}}}
.chart{{height:320px;position:relative;width:100%}}.chart.tall{{height:380px}}
.chart canvas{{display:block;width:100%!important;height:100%!important}}
table{{width:100%;border-collapse:collapse;font-size:.94rem}}
th,td{{padding:.62rem .45rem;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
td.n,th.n{{text-align:right;font-family:"IBM Plex Mono",monospace;font-size:.88rem}}
.note{{font-size:.8rem;color:var(--muted);margin-top:.55rem}}
.verdict{{background:linear-gradient(135deg,rgba(45,184,138,.12),transparent 55%),var(--card);border:1px solid var(--line);border-radius:20px;padding:1.45rem 1.55rem}}
.verdict strong{{color:var(--acc)}}
.gloss{{background:rgba(45,184,138,.08);border:1px solid var(--line);border-radius:14px;padding:1rem 1.15rem;margin:1rem 0;font-size:.98rem}}
.gloss b{{color:var(--acc)}}
.src{{font-size:.82rem;color:var(--muted)}}
.foot{{padding:2.5rem 0 4rem;color:var(--muted);font-size:.85rem;border-top:1px solid var(--line)}}
.num{{font-family:"IBM Plex Mono",monospace;color:var(--acc)}}
.err{{color:var(--bad);font-size:.9rem;display:none;padding:.5rem 0}}
.study{{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:1.35rem 1.45rem;margin:1.35rem 0}}
.study h3{{font-family:Spectral,Georgia,serif;font-size:1.28rem;margin:0 0 .85rem;line-height:1.3}}
.meta{{display:grid;grid-template-columns:7.5rem 1fr;gap:.35rem .75rem;margin:0 0 1rem;font-size:.92rem}}
.meta dt{{color:var(--muted);margin:0}}.meta dd{{margin:0}}
.meta a{{word-break:break-word}}
.explain p{{margin:.55rem 0}}.explain b{{color:var(--acc)}}
.era{{display:grid;gap:.85rem;margin:1rem 0}}
.era .box{{margin:0}}
.era h4{{margin:0 0 .35rem;font-size:1rem;color:var(--acc)}}
.paths{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1rem 0}}
.paths > div{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:1.15rem 1.25rem}}
@media(max-width:820px){{.paths{{grid-template-columns:1fr}}}}
.problem-block table th{{width:50%}}
</style>
</head>
<body>
<nav class="toc"><div class="wrap">
  <b style="color:var(--text)">H Funds</b>
  <a href="#thesis">Суть</a>
  <a href="#problem">Два пути</a>
  <a href="#evidence">Исследования</a>
  <a href="#why">Почему так</a>
  <a href="#btc">Крипта</a>
  <a href="#dca">Как копить</a>
  <a href="#end">Вывод</a>
</div></nav>

<header class="hero wrap">
  <div class="badge">{esc(copy['badge'])}</div>
  <h1>{esc(copy['h1'])}</h1>
  <p class="lead">{esc(copy['lead'])}</p>

  <div class="gloss">{copy['glossary']}</div>

  <div class="thesis" id="thesis">
    <h2 style="margin-top:0">{esc(copy['thesis_title'])}</h2>
    {copy['thesis_html']}
  </div>

  <div class="kpis">
    <div class="kpi"><em>{esc(copy['kpi1_b'])}</em><b>{esc(copy['kpi1_em'])}</b><span>{esc(copy['kpi1_span'])}</span></div>
    <div class="kpi"><em>{esc(copy['kpi2_b'])}</em><b>{esc(copy['kpi2_em'])}</b><span>{esc(copy['kpi2_span'])}</span></div>
    <div class="kpi"><em>{esc(copy['kpi3_b'])}</em><b class="ok">{esc(copy['kpi3_em'])}</b><span>{esc(copy['kpi3_span'])}</span></div>
  </div>
</header>

<section class="wrap problem-block" id="problem">
  <h2>{esc(copy['problem_title'])}</h2>
  __PROBLEM_BODY__
</section>

<section class="wrap" id="evidence">
  <h2>Что показывают исследования</h2>
  <p class="muted">{esc(copy['evidence_intro'])}</p>
  <p class="muted" style="margin-top:.4rem">Фонды и отчёты здесь — не «главный герой спора», а доказательная база: обыграть широкий рынок навыком отбора на длинной дистанции почти никому не удаётся.</p>
{studies}
</section>

<section class="wrap" id="why">
  <h2>{esc(copy['why_title'])}</h2>
  <p>{esc(copy['why_intro'])}</p>
  <div class="era">
{eras_html}
  </div>
  <div class="verdict">
    {copy['why_verdict']}
  </div>
</section>

<section class="wrap" id="btc">
  <h2>{esc(copy['btc_title'])}</h2>
  {copy['btc_html']}
</section>

<section class="wrap" id="dca">
  <h2>{esc(copy['dca_title'])}</h2>
  <div class="gloss">{copy['dca_gloss']}</div>
  {copy['dca_html']}
  <div class="kpis">
    <div class="kpi"><em>Вложено за {months} мес.</em><b class="gold">${invested}</b><span>$100 каждый месяц с января 2021</span></div>
    <div class="kpi"><em>Сколько BTC накопилось</em><b class="ok">{btc}</b><span>средняя цена покупки ~${avg_cost}</span></div>
    <div class="kpi"><em>Сколько это стоит сейчас</em><b class="ok">${value_now}</b><span>на {as_of_old} было ${value_old} (+{ret_old}%)</span></div>
  </div>
  <div class="box" style="margin-top:1.4rem">
    <div class="chart tall"><canvas id="chart-dca"></canvas></div>
    <p class="err" id="err-chart-dca">График не загрузился.</p>
    <p class="note">Серая линия — сколько денег вы внесли. Зелёная — сколько стоит портфель. Последняя точка зелёной пересчитана на спот ~${spot_now} ({as_of_now}).</p>
  </div>
  <h3>Что дал каждый год покупок</h3>
  <div class="box">
    <table>
      <tr><th>Год</th><th class="n">Вложили</th><th class="n">Купили BTC</th><th class="n">Средняя цена года</th><th class="n">Оценка на старом споте*</th><th class="n">Результат*</th></tr>
{years_rows}    </table>
    <p class="note">*Оценка на цене июля 2026 (~$65k) — как в исходном расчёте. Годы просадки купили больше монет.</p>
  </div>
  <div class="verdict">{copy['dca_verdict']}</div>
</section>

<section class="wrap" id="end">
  <h2>{esc(copy['end_title'])}</h2>
  {copy['end_html']}
</section>

<footer class="wrap foot">
  <p>{esc(copy['footer'])}</p>
  <p class="src">Источники внутри блоков исследований: Богл · Morningstar · SPIVA · S&amp;P · HFR / RIABiz · спор Баффета · расчёт регулярных покупок $100/мес с 2021-01.</p>
  <p style="margin-top:1.2rem">H Funds · разбор публичных данных · не персональная инвестиционная рекомендация.</p>
</footer>

<script>
const DCA = {dca_js};
function boot() {{
  if (typeof Chart === 'undefined') {{
    document.querySelectorAll('.err').forEach(function(e){{ e.style.display='block'; e.textContent='Не загрузилась библиотека графиков.'; }});
    return;
  }}
  Chart.defaults.color = '#8fa197';
  Chart.defaults.borderColor = 'rgba(220,235,225,.12)';
  Chart.defaults.font.family = 'Manrope';

  function mk(id, cfg) {{
    var el = document.getElementById(id);
    if (!el) return;
    try {{ new Chart(el, cfg); }}
    catch (e) {{
      var err = document.getElementById('err-' + id);
      if (err) {{ err.style.display = 'block'; err.textContent = 'Ошибка графика: ' + e.message; }}
    }}
  }}

  var labelPlugin = {{
    id: 'valueLabels',
    afterDatasetsDraw: function(chart) {{
      var ctx = chart.ctx;
      chart.data.datasets.forEach(function(ds, di) {{
        var meta = chart.getDatasetMeta(di);
        if (meta.hidden) return;
        meta.data.forEach(function(el, i) {{
          var v = ds.data[i];
          if (v === null || v === undefined) return;
          var pos = el.tooltipPosition();
          ctx.save();
          ctx.fillStyle = '#eef6f1';
          ctx.font = '600 12px Manrope';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'bottom';
          var txt = (typeof ds._labelFmt === 'function') ? ds._labelFmt(v) : String(v);
          ctx.fillText(txt, pos.x, pos.y - 6);
          ctx.restore();
        }});
      }});
    }}
  }};

  // 1. Bogle: survivors vs S&P annual return
  mk('chart-bogle', {{
    type: 'bar',
    data: {{
      labels: ['Выжившие фонды', 'S&P 500'],
      datasets: [{{
        label: '% в год',
        data: [10.4, 11.8],
        backgroundColor: ['rgba(227,93,77,.85)', 'rgba(45,184,138,.85)'],
        borderRadius: 10,
        _labelFmt: function(v){{ return v.toFixed(1) + '%'; }}
      }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }}, title: {{ display: true, text: 'Средняя доходность в год, 1970–2001', color: '#8fa197' }} }},
      scales: {{ y: {{ beginAtZero: true, max: 14, ticks: {{ callback: function(v){{ return v + '%'; }} }} }} }}
    }},
    plugins: [labelPlugin]
  }});

  // 2. Morningstar success rates
  mk('chart-morningstar', {{
    type: 'bar',
    data: {{
      labels: ['Все активные\\n10 лет', 'Крупные смешанные\\n10 лет', 'Крупные смешанные\\n15 лет', 'Ростовые крупные\\n15 лет'],
      datasets: [{{
        label: 'Успех: выжил и обогнал',
        data: [29, 15, 9, 3.5],
        backgroundColor: 'rgba(212,160,23,.88)',
        borderRadius: 10,
        _labelFmt: function(v){{ return v + '%'; }}
      }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: true, position: 'bottom', labels: {{ color: '#8fa197' }} }},
        title: {{ display: true, text: 'Доля фондов, которые выжили И обогнали рынок', color: '#8fa197' }}
      }},
      scales: {{
        x: {{ ticks: {{ maxRotation: 0, autoSkip: false, font: {{ size: 11 }} }} }},
        y: {{ beginAtZero: true, max: 40, ticks: {{ callback: function(v){{ return v + '%'; }} }} }}
      }}
    }},
    plugins: [labelPlugin]
  }});

  // 3. SPIVA — % of funds that LOST to index, with labels + legend
  mk('chart-spiva', {{
    type: 'bar',
    data: {{
      labels: ['1 год', '3 года', '5 лет', '10 лет', '15 лет', '20 лет'],
      datasets: [{{
        label: 'Доля активных фондов, которые заработали МЕНЬШЕ S&P 500',
        data: [65, 85, 76, 84, 90, 92],
        backgroundColor: 'rgba(227,93,77,.85)',
        borderRadius: 10,
        _labelFmt: function(v){{ return v + '%'; }}
      }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: true, position: 'bottom', labels: {{ color: '#eef6f1', boxWidth: 14 }} }},
        title: {{ display: true, text: 'SPIVA YE 2024: чем дольше срок — тем больше проигравших', color: '#8fa197' }}
      }},
      scales: {{ y: {{ beginAtZero: true, max: 100, ticks: {{ callback: function(v){{ return v + '%'; }} }} }} }}
    }},
    plugins: [labelPlugin]
  }});

  // 4. S&P 20y cumulative
  mk('chart-sp20', {{
    type: 'bar',
    data: {{
      labels: ['S&P 500', 'Средний управляющий'],
      datasets: [{{
        label: 'Накопительный рост за 20 лет',
        data: [322, 257],
        backgroundColor: ['rgba(45,184,138,.85)', 'rgba(227,93,77,.85)'],
        borderRadius: 10,
        _labelFmt: function(v){{ return '+' + v + '%'; }}
      }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: false }},
        title: {{ display: true, text: '2001–2020: накопительный рост (+322% vs +257%)', color: '#8fa197' }}
      }},
      scales: {{ y: {{ beginAtZero: true, ticks: {{ callback: function(v){{ return v + '%'; }} }} }} }}
    }},
    plugins: [labelPlugin]
  }});

  // 5. HFR years + side comparison strip via dual chart: yearly bars already exist
  mk('chart-hfr', {{
    type: 'bar',
    data: {{
      labels: ['10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'],
      datasets: [
        {{ label: 'S&P 500 за год', data: [12.6,0,13.3,29.6,11.5,-0.7,9.8,18.7,-6.6,30.4,15.8,26.6,-19.6,26.3,25], backgroundColor: 'rgba(238,246,241,.85)' }},
        {{ label: 'Средний хедж-фонд', data: [10.2,-5.2,6.5,11.1,3.2,1.8,5.4,8.6,-4,10.4,11.2,10.2,-4.2,7.5,8.5], backgroundColor: 'rgba(45,184,138,.85)' }}
      ]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: true, position: 'bottom' }},
        title: {{ display: true, text: 'Годовая доходность: рынок vs средний хедж-фонд (2010–2024)', color: '#8fa197' }}
      }},
      scales: {{ y: {{ ticks: {{ callback: function(v){{ return v + '%'; }} }} }} }}
    }}
  }});

  // 6. Buffett bet growth
  var y = []; for (var i=0;i<11;i++) y.push(2008+i);
  var s=1e6, f=1e6, S=[], F=[];
  for (i=0;i<y.length;i++) {{ S.push(Math.round(s)); F.push(Math.round(f)); s*=1.071; f*=1.022; }}
  mk('chart-buffett', {{
    type: 'line',
    data: {{
      labels: y,
      datasets: [
        {{ label: 'Индекс S&P (~7.1% в год)', data: S, borderColor: '#2db88a', fill: true, backgroundColor: 'rgba(45,184,138,.12)', tension: .25, pointRadius: 3 }},
        {{ label: 'Корзина Protégé (~2.2% в год)', data: F, borderColor: '#e35d4d', fill: true, backgroundColor: 'rgba(227,93,77,.1)', tension: .25, pointRadius: 3 }}
      ]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: true, position: 'bottom' }},
        title: {{ display: true, text: 'Как рос бы $1 000 000 за 10 лет пари', color: '#8fa197' }}
      }},
      scales: {{ y: {{ ticks: {{ callback: function(v){{ return '$' + (v/1e6).toFixed(1) + 'M'; }} }} }} }}
    }}
  }});

  mk('chart-dca', {{
    type: 'line',
    data: {{
      labels: DCA.labels,
      datasets: [
        {{ label: 'Сколько внесли $', data: DCA.inv, borderColor: '#6b8a9a', tension: .2, pointRadius: 0, borderWidth: 2 }},
        {{ label: 'Сколько стоит портфель $', data: DCA.val, borderColor: '#2db88a', fill: true, backgroundColor: 'rgba(45,184,138,.12)', tension: .2, pointRadius: 0, borderWidth: 2 }}
      ]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ position: 'bottom' }} }},
      scales: {{
        x: {{ ticks: {{ maxTicksLimit: 10, autoSkip: true }} }},
        y: {{ ticks: {{ callback: function(v){{ return '$' + v; }} }} }}
      }}
    }}
  }});
}}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
else boot();
</script>
</body>
</html>
"""

def build_problem_body(raw: str) -> str:
    pp = scrub_inline(raw)
    if "<table" in pp:
        return f'<div class="box">{pp}</div>'
    cards = re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", pp, flags=re.S)
    if len(cards) >= 2:
        intro = re.split(r"<h3>", pp, maxsplit=1)[0].strip()
        # drop leftover open wrappers from Gemini
        intro = re.sub(r"</?div[^>]*>", "", intro).strip()
        blocks = "".join(
            f'<div class="box" style="margin:0"><h3>{t}</h3>'
            f'<p class="muted" style="margin:0">{x}</p></div>'
            for t, x in cards[:2]
        )
        return f"{intro}<div class=\"paths\">{blocks}</div>"
    return f'<div class="box">{pp}</div>'


html = html.replace("__PROBLEM_BODY__", build_problem_body(copy["problem_html"]))

(root / "index.html").write_text(html, encoding="utf-8")
print("Wrote", root / "index.html", "bytes", len(html.encode("utf-8")))

banned = [
    "индекс ничего не берёт",
    "ничего не берёт",
    "RESULTS-BY-SOURCE",
    "SOURCES-LONG-HORIZON",
    "study-vanguard50",
    "50 years",
]
low = html.lower()
for b in banned:
    if b.lower() in low:
        print("WARN banned phrase still present:", b)
# Vanguard 50y study block must be gone; "Vanguard" as Bogle affiliation is OK
if "50 лет индексного" in html or "study-vanguard" in html:
    print("WARN vanguard50 study still present")
print("charts:", ", ".join(re.findall(r'id="(chart-[^"]+)"', html)))
print("OK")
