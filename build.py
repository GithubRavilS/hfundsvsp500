#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

root = Path(__file__).resolve().parent
dca = json.loads((root / "dca-data.json").read_text())
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

html = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>H Funds — широкий рынок против «умного» отбора</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Spectral:ital,wght@0,500;0,700;1,500&display=swap" rel="stylesheet" />
<script src="./chart.umd.min.js"></script>
<style>
:root{--bg:#0b1210;--card:#141c19;--line:rgba(220,235,225,.12);--text:#eef6f1;--muted:#8fa197;--acc:#2db88a;--gold:#d4a017;--bad:#e35d4d;--max:920px}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);font-family:Manrope,system-ui,sans-serif;line-height:1.75;
background-image:radial-gradient(ellipse 70% 40% at 10% -10%,rgba(45,184,138,.18),transparent 55%),radial-gradient(ellipse 50% 35% at 90% 0%,rgba(212,160,23,.1),transparent 50%)}
.wrap{width:min(var(--max),calc(100% - 2rem));margin:0 auto}
a{color:var(--acc)}
nav.toc{position:sticky;top:0;z-index:20;backdrop-filter:blur(12px);background:rgba(11,18,16,.85);border-bottom:1px solid var(--line);padding:.7rem 0;font-size:.78rem}
nav.toc .wrap{display:flex;gap:.9rem;flex-wrap:wrap;align-items:center}
nav.toc a{color:var(--muted);text-decoration:none}nav.toc a:hover{color:var(--text)}
.hero{padding:4.2rem 0 2.8rem}
.badge{display:inline-block;padding:.25rem .65rem;border:1px solid var(--line);border-radius:999px;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--acc);margin-bottom:1rem}
h1{font-family:Spectral,Georgia,serif;font-size:clamp(2rem,5vw,3.2rem);line-height:1.12;margin:0 0 1.1rem;max-width:20ch}
.lead{font-size:1.16rem;color:var(--muted);max-width:62ch;margin:0 0 1.6rem}
.thesis{background:linear-gradient(145deg,rgba(45,184,138,.14),transparent 60%),var(--card);border:1px solid var(--line);border-radius:22px;padding:1.5rem 1.6rem;margin:1.5rem 0}
.thesis strong{color:var(--acc)}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1.6rem}
@media(max-width:800px){.kpis{grid-template-columns:1fr}}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:1.15rem}
.kpi em{display:block;font-style:normal;font-size:.78rem;color:var(--muted)}
.kpi b{display:block;font-size:1.65rem;margin:.25rem 0;color:var(--bad)}
.kpi b.ok{color:var(--acc)}.kpi b.gold{color:var(--gold)}
.kpi span{font-size:.86rem;color:var(--muted)}
section{padding:3rem 0;border-top:1px solid var(--line)}
h2{font-family:Spectral,Georgia,serif;font-size:clamp(1.4rem,3.2vw,2.1rem);margin:0 0 .85rem;line-height:1.25}
h3{font-size:1.12rem;margin:0 0 .55rem}
p,li{font-size:1.05rem}.muted{color:var(--muted)}
.box{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:1.3rem 1.4rem;margin:1.1rem 0}
.two{display:grid;grid-template-columns:1.05fr .95fr;gap:1.1rem}@media(max-width:820px){.two{grid-template-columns:1fr}}
.chart{height:320px;position:relative;width:100%}.chart.tall{height:380px}
.chart canvas{display:block;width:100%!important;height:100%!important}
table{width:100%;border-collapse:collapse;font-size:.94rem}
th,td{padding:.62rem .45rem;border-bottom:1px solid var(--line);text-align:left}
td.n,th.n{text-align:right;font-family:"IBM Plex Mono",monospace;font-size:.88rem}
.note{font-size:.8rem;color:var(--muted);margin-top:.55rem}
.verdict{background:linear-gradient(135deg,rgba(45,184,138,.12),transparent 55%),var(--card);border:1px solid var(--line);border-radius:20px;padding:1.45rem 1.55rem}
.verdict strong{color:var(--acc)}
.callout{border-left:3px solid var(--gold);padding:.15rem 0 .15rem 1rem;margin:1.2rem 0;color:var(--muted)}
.gloss{background:rgba(45,184,138,.08);border:1px solid var(--line);border-radius:14px;padding:1rem 1.15rem;margin:1rem 0;font-size:.98rem}
.gloss b{color:var(--acc)}
.src{font-size:.82rem;color:var(--muted)}
.foot{padding:2.5rem 0 4rem;color:var(--muted);font-size:.85rem;border-top:1px solid var(--line)}
.num{font-family:"IBM Plex Mono",monospace;color:var(--acc)}
.err{color:var(--bad);font-size:.9rem;display:none;padding:.5rem 0}
.study{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:1.35rem 1.45rem;margin:1.35rem 0}
.study h3{font-family:Spectral,Georgia,serif;font-size:1.28rem;margin:0 0 .85rem;line-height:1.3}
.meta{display:grid;grid-template-columns:7.5rem 1fr;gap:.35rem .75rem;margin:0 0 1rem;font-size:.92rem}
.meta dt{color:var(--muted);margin:0}.meta dd{margin:0}
.meta a{word-break:break-word}
.era{display:grid;gap:.85rem;margin:1rem 0}
.era .box{margin:0}
.era h4{margin:0 0 .35rem;font-size:1rem;color:var(--acc)}
</style>
</head>
<body>
<nav class="toc"><div class="wrap">
  <b style="color:var(--text)">H Funds</b>
  <a href="#thesis">Главная мысль</a>
  <a href="#problem">О чём спор</a>
  <a href="#evidence">Исследования</a>
  <a href="#why">Почему индекс</a>
  <a href="#btc">Биткоин</a>
  <a href="#dca">Как копить</a>
  <a href="#end">Вывод</a>
</div></nav>

<header class="hero wrap">
  <div class="badge">Разбор на десятилетиях данных · без рекламы фондов</div>
  <h1>Широкий рынок против «умного» отбора бумаг</h1>
  <p class="lead">
    Многие думают: «отдам деньги умным людям — они точно обыграют рынок».
    Мы сверили крупные отчёты за десятилетия.
    Картина повторяется: <b style="color:var(--text)">большинство профессиональных управляющих не обгоняет простой рыночный индекс</b>.
    И важный нюанс: дело не в том, что «индекс ничего не берёт за управление».
    Дело в устройстве самого индекса — он отражает всю экономику и каждый цикл сам подхватывает новых лидеров.
  </p>

  <div class="gloss">
    <b>Короткий словарик.</b>
    <b>Индекс</b> — «средний портфель» большого рынка. Самый известный в США — S&amp;P 500: корзина примерно из 500 крупнейших американских компаний.
    Купить индексный фонд = купить сразу почти весь этот рынок.
    <b>Активный фонд / хедж-фонд</b> — команда, которая сама выбирает бумаги и обещает обыграть рынок навыком отбора.
  </div>

  <div class="thesis" id="thesis">
    <h2 style="margin-top:0">Главная мысль</h2>
    <p>
      <strong>Самая рабочая схема для длинных денег — владеть широким рынком и не пытаться угадать следующего героя.</strong>
      Не потому что управляющие «глупые». А потому что в каждом пятилетии и десятилетии лидеров меняют.
      Индекс автоматически держит тех, кто сейчас тянет экономику вверх. Отдельные направления и «гениальные» корзины
      могут блестеть один цикл — и отставать на следующем.
    </p>
    <p style="margin-bottom:0" class="muted">
      Отсюда вывод для крипты: базой копим биткоин как «главный актив» цифрового рынка —
      даже если повседневные транзакции идут через стейблкоины, а DeFi и ликвидность живут на других сетях.
      Копим регулярно, небольшими суммами. DeFi — надстройка поверх позиции, а не замена самой покупки.
    </p>
  </div>

  <div class="kpis">
    <div class="kpi"><em>За 20 лет (отчёт SPIVA)</em><b>~92%</b><span>крупных активных фондов США проиграли простому индексу S&amp;P 500</span></div>
    <div class="kpi"><em>Спор Баффета, 10 лет</em><b>2.2% vs 7.1%</b><span>профессиональная корзина «фондов фондов» против индекса — в среднем за год</span></div>
    <div class="kpi"><em>Покупка биткоина по $100/мес с 2021</em><b class="ok">+__RET_NOW__%</b><span>пересчёт на цену ~$__SPOT_NOW__ на __AS_OF_NOW__</span></div>
  </div>
</header>

<section class="wrap" id="problem">
  <h2>О чём вообще этот спор</h2>
  <p>
    В США сильная культура «умных управляющих». Кажется логичным:
    раз человек целый день смотрит рынок — он же обыграет «тупой» индекс.
    К концу 2025 года в хедж-фондах крутилось уже больше <span class="num">$5 триллионов</span>.
    Но большой объём денег — не доказательство, что средний клиент богатеет быстрее рынка.
  </p>
  <p>Мы делим вопрос на два — и оба про навык отбора, а не про «кто дешевле взял плату»:</p>
  <div class="two">
    <div class="box">
      <h3>Вопрос 1. Умение выбирать</h3>
      <p class="muted" style="margin:0">Часто ли профессионалы обыгрывают простой индекс чисто за счёт отбора бумаг — на длинной дистанции?</p>
    </div>
    <div class="box">
      <h3>Вопрос 2. Угадывание цикла</h3>
      <p class="muted" style="margin:0">Можно ли заранее выбрать отрасли и компании, которые потянут следующий цикл — или проще держать весь рынок?</p>
    </div>
  </div>
  <p class="callout">Где данных мало — говорим прямо. Полноценной «истории хедж-фондов на 50 лет» нет: нормальная статистика индустрии начинается примерно с 1990-х. Зато по обычным активным фондам акций США есть десятки лет отчётов.</p>
</section>

<section class="wrap" id="evidence">
  <h2>Что показывают исследования</h2>
  <p class="muted">
    Ниже — не мнения блогеров, а крупные отчёты.
    У каждого блока одна и та же структура: кто проводил, какой период, на каких данных, ссылка, главный результат.
  </p>

  <article class="study" id="study-bogle">
    <h3>1. Джон Богл (Vanguard): длинный отрезок 1970 → 2001</h3>
    <dl class="meta">
      <dt>Кто</dt><dd>Джон Богл, основатель Vanguard; доклад / PDF 2001</dd>
      <dt>Период</dt><dd>начало 1970 → 30.09.2001 (~32 года)</dd>
      <dt>Данные</dt><dd>американские фонды акций (equity mutual funds) против индекса S&amp;P 500</dd>
      <dt>Ссылка</dt><dd><a href="https://boglecenter.net/wp-content/uploads/JCB_AXA_10-01.pdf" target="_blank" rel="noopener">boglecenter.net — PDF доклада</a></dd>
    </dl>
    <div class="box" style="margin:0">
      <table>
        <tr><th>Что измерили</th><th class="n">Результат</th></tr>
        <tr><td>Фондов на старте</td><td class="n">355</td></tr>
        <tr><td>Закрылись / выбыли</td><td class="n">197 (больше половины)</td></tr>
        <tr><td>Дожили до конца</td><td class="n">158</td></tr>
        <tr><td>Средняя доходность выживших</td><td class="n">10.4% в год</td></tr>
        <tr><td>Доходность S&amp;P 500</td><td class="n">11.8% в год</td></tr>
        <tr><td>Отставание только «живых»</td><td class="n">−1.4 пункта в год</td></tr>
        <tr><td>С учётом закрывшихся (консервативно)</td><td class="n">примерно −2.9 пункта в год</td></tr>
      </table>
      <p class="note">Смысл: в красивых таблицах часто остаются только выжившие. Мёртвые исчезают — и кажется, что «все крутые». Даже среди выживших средний результат слабее индекса.</p>
    </div>
  </article>

  <article class="study" id="study-vanguard50">
    <h3>2. Vanguard: 50 лет индексного фонда</h3>
    <dl class="meta">
      <dt>Кто</dt><dd>корпоративный разбор Vanguard — «50 years. 50 facts»</dd>
      <dt>Период</dt><dd>с запуска первого индексного фонда 31.08.1976 → данные до 31.03.2026</dd>
      <dt>Данные</dt><dd>Vanguard 500 (VFINX) и сам индекс S&amp;P 500; отдельно — доля исчезающих активных фондов</dd>
      <dt>Ссылка</dt><dd><a href="https://corporate.vanguard.com/content/corporatesite/us/en/corp/articles/50-years-50-facts-indexing-since-1976.html" target="_blank" rel="noopener">corporate.vanguard.com — 50 years / 50 facts</a></dd>
    </dl>
    <p>
      Первый массовый индексный фонд почти один в один повторяет рынок полвека:
      около <span class="num">11.4%</span> в год при рынке около <span class="num">11.7%</span>.
      На любом пятилетнем отрезке заметная доля активных фондов просто исчезает из статистики.
      Это уже не «кто кого переиграл в удачный год», а история на полвека.
    </p>
  </article>

  <article class="study" id="study-morningstar">
    <h3>3. Morningstar: кто выжил и реально обогнал пассивный аналог</h3>
    <dl class="meta">
      <dt>Кто</dt><dd>Morningstar — US Active/Passive Barometer (середина 2024)</dd>
      <dt>Период</dt><dd>горизонты до 20 лет; срез данных на 30.06.2024</dd>
      <dt>Данные</dt><dd>активные фонды США; «успех» = фонд <b>не закрылся</b> и обогнал средний пассивный фонд своей категории</dd>
      <dt>Ссылка</dt><dd><a href="https://assets.contentstack.io/v3/assets/blt4eb669caa7dc65b2/blte7224d06fe1faf84/66df6bf5a193e5d7e23bb9c9/Morningstar_US_Active_Passive_Barometer_Mid_Year_2024.pdf" target="_blank" rel="noopener">PDF: Morningstar US Active/Passive Barometer</a></dd>
    </dl>
    <div class="two">
      <div class="box" style="margin:0">
        <ul style="margin:0;padding-left:1.1rem">
          <li>Все активные, 10 лет: успех примерно у <b>29%</b></li>
          <li>Крупные смешанные США, 10 лет: около <b>15%</b></li>
          <li>Те же, 15 лет: около <b>9%</b></li>
          <li>«Ростовые» крупные, 15 лет: около <b>3.5%</b></li>
          <li>Из стартовавших за 20 лет в крупном смешанном сегменте доживает примерно <b>треть</b></li>
        </ul>
      </div>
      <div class="box" style="margin:0">
        <p class="muted" style="margin:0">На одном годе иногда почти 50/50. На 10–20 годах шансы «я победил рынок и не закрылся» резко падают. Это как раз про навык и долговечность отбора — не про «кто сколько взял сверху».</p>
      </div>
    </div>
  </article>

  <article class="study" id="study-spiva">
    <h3>4. SPIVA: доля фондов, которые проиграли индексу</h3>
    <dl class="meta">
      <dt>Кто</dt><dd>S&amp;P Dow Jones Indices — ежегодный скоркард SPIVA (США)</dd>
      <dt>Период</dt><dd>серия с ~2001/2002; цифры ниже — YE 2024, горизонты до 20 лет</dd>
      <dt>Данные</dt><dd>все крупные активные фонды США против S&amp;P 500; считают долю тех, кто <b>уступил</b> индексу</dd>
      <dt>Ссылки</dt><dd>
        <a href="https://www.spglobal.com/spdji/en/research-insights/spiva/" target="_blank" rel="noopener">хаб SPIVA</a> ·
        <a href="https://www.spglobal.com/spdji/en/documents/spiva/spiva-us-year-end-2024.pdf" target="_blank" rel="noopener">PDF YE 2024</a>
      </dd>
    </dl>
    <div class="two">
      <div class="box" style="margin:0">
        <div class="chart"><canvas id="spiva"></canvas></div>
        <p class="err" id="err-spiva">График не загрузился — обновите страницу.</p>
        <p class="note">Доля крупных активных фондов, которые заработали меньше, чем S&amp;P 500.</p>
      </div>
      <div class="box" style="margin:0">
        <table>
          <tr><th>Срок</th><th class="n">Проиграли индексу</th></tr>
          <tr><td>1 год</td><td class="n">65%</td></tr>
          <tr><td>3 года</td><td class="n">85%</td></tr>
          <tr><td>5 лет</td><td class="n">76%</td></tr>
          <tr><td>10 лет</td><td class="n">84%</td></tr>
          <tr><td>15 лет</td><td class="n">90%</td></tr>
          <tr><td>20 лет</td><td class="n">~92%</td></tr>
        </table>
        <p class="note">Чем длиннее горизонт — тем меньше «победителей». На 20 годах примерно 9 из 10 не догоняют индекс.</p>
      </div>
    </div>
  </article>

  <article class="study" id="study-sp-counterfactual">
    <h3>5. Исследование S&amp;P: 2001–2020 по календарным годам</h3>
    <dl class="meta">
      <dt>Кто</dt><dd>S&amp;P Dow Jones Indices — research «Returns, Values, and Outcomes»</dd>
      <dt>Период</dt><dd>2001–2020 (ровно 20 календарных лет)</dd>
      <dt>Данные</dt><dd>крупные активные фонды США vs S&amp;P 500; кумулятивный рост и число лет, когда majority обогнала индекс</dd>
      <dt>Ссылка</dt><dd><a href="https://www.spglobal.com/spdji/en/documents/research/research-returns-values-and-outcomes-a-counterfactual-history.pdf" target="_blank" rel="noopener">PDF: Returns, Values, and Outcomes</a></dd>
    </dl>
    <p>
      За 20 календарных лет большинство крупных активных фондов обогнало индекс только в <b>трёх годах из двадцати</b>.
      Накопительно рынок вырос примерно на <span class="num">+322%</span>, средний активный фонд — около <span class="num">+257%</span>.
      Средний «добавленный результат» активного менеджера к бенчмарку — около <span class="num">−0.8%</span> в год.
      То есть отставание видно уже на уровне результата отбора, а не как «мелочь на фоне платы».
    </p>
  </article>

  <article class="study" id="study-hf">
    <h3>6. Хедж-фонды: когда они выглядят умнее</h3>
    <dl class="meta">
      <dt>Кто</dt><dd>открытые сводки по индексам HFR / HFRI; сводка RIABiz по годам; отдельно — срез Beacon Hill по HFRX</dd>
      <dt>Период</dt><dd>HFRI с ~1990; сравнительный ряд ниже — примерно 2010–2025; срез HFRX — 10 лет до конца 2018</dd>
      <dt>Данные</dt><dd>средняя «больница» хедж-фондов против S&amp;P 500 по годам; глобальный индекс HFRX vs широкий рынок акций США</dd>
      <dt>Ссылки</dt><dd>
        <a href="https://www.hfr.com/hfr-indices/compare-hfr-index-types/" target="_blank" rel="noopener">типы индексов HFR</a> ·
        <a href="https://riabiz.com/charts/sp-500-vs-hedge-funds" target="_blank" rel="noopener">RIABiz: S&amp;P vs hedge funds</a>
      </dd>
    </dl>
    <p>
      Если сравнивать средний хедж-фонд с S&amp;P 500 по годам, индекс чаще впереди в сильный рост.
      Хедж-фонды чаще выглядят лучше в плохие годы — когда рынок падает, а они падают меньше.
      Это другая задача: не «выжать максимум роста», а «меньше трястись в кризис».
    </p>
    <div class="box">
      <div class="chart tall"><canvas id="years"></canvas></div>
      <p class="err" id="err-years">График не загрузился.</p>
      <p class="note">2010–2024. Светлые столбцы — доходность S&amp;P за год. Зелёные — приближение среднего хедж-фонда по открытым сводкам.</p>
    </div>
    <ul>
      <li>За примерно 2010–2025 средний хедж-фонд обгонял S&amp;P примерно в <b>3</b> годах из 16.</li>
      <li>В одном 10-летнем срезе «глобальный» индекс хедж-фондов HFRX давал около <b>1.5%</b> в год при S&amp;P около <b>13%</b>.</li>
    </ul>
  </article>

  <article class="study" id="study-buffett">
    <h3>7. Спор Баффета: публичный матч на 10 лет</h3>
    <dl class="meta">
      <dt>Кто</dt><dd>Уоррен Баффет против Protégé Partners (Long Bet №362); разборы Long Now и Financial Times</dd>
      <dt>Период</dt><dd>01.01.2008 → 31.12.2017 (ровно 10 лет)</dd>
      <dt>Данные</dt><dd>обычный фонд на индекс S&amp;P 500 против корзины из пяти «фондов фондов» (через них — больше сотни хедж-фондов)</dd>
      <dt>Ссылки</dt><dd>
        <a href="https://longnow.org/ideas/warren-buffett-wins-million-dollar-long-bet/" target="_blank" rel="noopener">Long Now — разбор спора</a> ·
        <a href="https://www.ft.com/content/3f449299-318c-4c8f-ab7a-bb3fa7221f9c" target="_blank" rel="noopener">Financial Times</a>
      </dd>
    </dl>
    <p>
      Баффет поспорил, что простой индексный фонд обгонит отобранную профессиональную корзину.
      Индекс победил всухую: ни один из пяти «фондов фондов» его не обогнал.
    </p>
    <div class="two">
      <div class="box" style="margin:0">
        <div class="chart tall"><canvas id="buffett"></canvas></div>
        <p class="err" id="err-buffett">График не загрузился.</p>
        <p class="note">Как рос бы условный миллион долларов: ~7.1% в год у индекса против ~2.2% у профессиональной корзины.</p>
      </div>
      <div class="box" style="margin:0">
        <ul>
          <li>Индекс: примерно <b>+126%</b> за 10 лет</li>
          <li>Профессиональная корзина: примерно <b>+36%</b></li>
          <li>Среднегодовая: <b>7.1%</b> против <b>2.2%</b></li>
          <li>Из пяти «фондов фондов» индекс обогнал <b>все пять</b></li>
        </ul>
        <p class="muted" style="margin-bottom:0">Это не один неудачный менеджер. Это отбор команд, который всё равно проиграл широкому рынку.</p>
      </div>
    </div>
  </article>
</section>

<section class="wrap" id="why">
  <h2>Почему индекс выигрывает «по устройству»</h2>
  <p>
    Главная причина — не «индекс ничего не берёт».
    Главная причина в том, что <b>индекс отражает экономику целиком</b>.
    Каждый цикл, каждое пятилетие и десятилетие выдвигают своих лидеров.
    Индекс не обязан угадывать их заранее: он просто держит рынок, а рынок сам поднимает тех, кто сейчас сильнее.
  </p>

  <div class="era">
    <div class="box">
      <h4>Конец 1990-х — доткомы</h4>
      <p class="muted" style="margin:0">Тянули технологические и телеком-имена вроде Cisco, Microsoft, Intel, Oracle. Кто ставил только на «старую экономику», часто выглядел отстающим — пока пузырь не лопнул и лидеры снова сменились.</p>
    </div>
    <div class="box">
      <h4>Нулевые</h4>
      <p class="muted" style="margin:0">После краха доткомов долго звучали другие истории: энергия и сырьё (Exxon Mobil), крупные промышленные и потребительские имена (General Electric, Walmart), банки до кризиса 2008. В начале десятилетия «герои 90-х» уже не были автоматическими лидерами.</p>
    </div>
    <div class="box">
      <h4>Десятые</h4>
      <p class="muted" style="margin:0">Вверх тянули крупные технологические платформы — Apple, Amazon, Google (Alphabet), Facebook (Meta), Microsoft, Netflix. Смартфоны, облако, реклама в сети. Кто в 2010-м держал портфель «как в нулевых», легко пропустил этот сдвиг.</p>
    </div>
    <div class="box">
      <h4>Пандемия и сразу после</h4>
      <p class="muted" style="margin:0">Короткий цикл «домашней экономики»: Zoom, Shopify, Peloton, всплеск стриминга и онлайн-ритейла. Часть этих историй потом резко остыла. Рынок снова переставил акценты.</p>
    </div>
    <div class="box">
      <h4>Середина 2020-х — искусственный интеллект</h4>
      <p class="muted" style="margin:0">Сильно тянут Nvidia, Microsoft, Broadcom, Alphabet, Meta, Amazon и соседние имена вокруг вычислений и моделей. Это уже другой набор героев, чем даже пять лет назад.</p>
    </div>
  </div>

  <div class="verdict">
    <p>
      <strong>Вывод простой.</strong>
      Не надо заранее угадывать, какая компания «будет тащить».
      В индексе почти всегда оказывается что-то самое сильное текущего цикла.
      А когда выбираешь отдельные направления или «звёздный» набор идей, можно красиво выглядеть одно пятилетие —
      и отставать на следующем, когда лидеры сменятся.
    </p>
  </div>

  <div class="two" style="margin-top:1.2rem">
    <div class="box">
      <h3>Витрина выживших</h3>
      <p class="muted" style="margin:0">Провалившиеся фонды закрывают. Вы смотрите на оставшихся — и кажется, что «все успешные». Отчёты Богла и Morningstar как раз чинят эту оптическую иллюзию.</p>
    </div>
    <div class="box">
      <h3>Удача на короткой дистанции</h3>
      <p class="muted" style="margin:0">За один год кому-то везёт. За 15–20 лет отчёты показывают: большинство остаётся позади широкого рынка. Время смывает случайный «гений».</p>
    </div>
  </div>
</section>

<section class="wrap" id="btc">
  <h2>Как это связано с биткоином</h2>
  <p>
    Мы не говорим «биткоину нарисована вечная зелёная свеча».
    Мы переносим уже проверенный принцип: <b>держать главный актив класса, а не угадывать следующего героя внутри класса</b>.
  </p>
  <p>
    В обычных деньгах США таким «главным показателем» десятилетиями был широкий индекс акций:
    он отражает экономику, даже если сегодня тянет Nvidia, а вчера тянул Exxon или Cisco.
  </p>
  <p>
    В цифровых активах для многих роль базового актива занимает биткоин —
    хотя по функциям он в основном про хранение ценности.
    Повседневные переводы чаще идут через стейблкоины.
    Объёмы торгов, DeFi и «живая» ликвидность часто больше на Ethereum и соседних сетях.
    И всё же биткоин остаётся самым понятным «якорем» всего крипторынка:
    ограниченное предложение, мировые торги, нет совета директоров, который может внезапно «напечатать» ещё.
  </p>
  <p>
    DeFi здесь — не вместо покупки, а <b>поверх</b>: как заставить уже купленный капитал приносить доход
    (с оговоркой про риски смарт-контрактов и ликвидаций). Сначала позиция. Потом — вопрос, работает ли капитал.
  </p>
  <p class="callout">В логике еженедельных сводок то же самое: основной капитал уже в рынке, докупки по плану, регулярность важнее эмоций от заголовка.</p>
</section>

<section class="wrap" id="dca">
  <h2>Как копить: регулярные покупки</h2>
  <div class="gloss">
    <b>Регулярные покупки (часто называют DCA).</b>
    Каждый месяц (или неделю) покупаете на одну и ту же сумму.
    Не пытаетесь угадать дно. Когда дорого — монет меньше. Когда дёшево — монет больше. Главное — не останавливаться.
  </div>
  <p>
    Раньше, на срезе <b>__AS_OF_OLD__</b>, биткоин был около <b>$__SPOT_OLD__</b>.
    Мы посчитали простую серию: <b>$100 каждый месяц</b> с января 2021.
    Уже тогда выходило хорошо: вложили $__INVESTED__, накопили примерно __BTC__ BTC,
    портфель стоил около $__VALUE_OLD__ — это <b>+__RET_OLD__%</b> к вложениям.
  </p>
  <p>
    Сейчас, на <b>__AS_OF_NOW__</b>, тот же мешок при цене около <b>$__SPOT_NOW__</b>
    стоит уже примерно <b>$__VALUE_NOW__</b> — это <b>+__RET_NOW__%</b>
    (плюс около $__PNL_NOW__). Когда цена проседала, регулярные покупки всё равно работали.
    Когда цена выросла — результат той же дисциплины стал ещё сильнее.
  </p>
  <div class="kpis">
    <div class="kpi"><em>Вложено за __MONTHS__ мес.</em><b class="gold">$__INVESTED__</b><span>$100 каждый месяц с января 2021</span></div>
    <div class="kpi"><em>Сколько BTC накопилось</em><b class="ok">__BTC__</b><span>средняя цена покупки ~$__AVG_COST__</span></div>
    <div class="kpi"><em>Сколько это стоит сейчас</em><b class="ok">$__VALUE_NOW__</b><span>в июле 2026 было $__VALUE_OLD__</span></div>
  </div>

  <div class="box" style="margin-top:1.4rem">
    <div class="chart tall"><canvas id="chart-dca"></canvas></div>
    <p class="err" id="err-chart-dca">График не загрузился.</p>
    <p class="note">Серая линия — сколько денег вы внесли. Зелёная — сколько стоит портфель. Последняя точка зелёной пересчитана на текущий спот ~$__SPOT_NOW__.</p>
  </div>

  <h3>Что дал каждый год покупок</h3>
  <div class="box">
    <table>
      <tr><th>Год</th><th class="n">Вложили</th><th class="n">Купили BTC</th><th class="n">Средняя цена года</th><th class="n">Оценка на старом споте*</th><th class="n">Результат*</th></tr>
__YEARS_ROWS__
    </table>
    <p class="note">*Оценка на цене июля 2026 (~$65k) — как в исходном расчёте. Годы просадки купили больше монет. Смысл регулярных покупок — не поймать идеальную точку, а не выпасть из плана.</p>
  </div>

  <div class="verdict">
    <p><strong>Регулярные покупки не обещают, что каждый месяц будет плюс.</strong>
      Они обещают другое: вы системно набираете базовый актив и меньше спорите с рынком из ленты новостей.
      Это та же идея, что и с индексом: меньше героизма, больше дисциплины.</p>
  </div>
</section>

<section class="wrap" id="end">
  <h2>Собираем всё вместе</h2>
  <p>
    Спор звучал статусно: «может, отдать деньги самым умным фондам?»
    Данные ответили спокойно: <b>средний результат профессионального отбора редко бьёт широкий рыночный показатель</b>.
  </p>
  <p>
    Не потому что «индекс ничего не берёт».
    А потому что индекс отражает всю экономику и каждый цикл сам включает новых лидеров —
    от Cisco и Exxon до Apple, Amazon и Nvidia.
    Отдельные направления могут выиграть одно пятилетие и проиграть следующее.
  </p>
  <p>
    Значит, рациональная база — владеть тем, что отражает рост всего класса активов.
    В классическом мире США — широкий индекс акций. В цифровом слое портфеля для многих — биткоин.
    Как копить — регулярно, по правилам, а не от эмоции заголовка.
  </p>
  <div class="thesis">
    <p style="margin:0">
      <strong>Проще часто оказывается сильнее.</strong>
      Не потому что мир награждает лень — потому что угадывать следующего героя цикла системно труднее,
      чем просто держать рынок, в котором этот герой уже появится.
      Мы искали не удобный лозунг, а то, что повторяется в отчётах. Оно повторяется.
    </p>
  </div>
</section>

<footer class="wrap foot">
  <p><b style="color:var(--text)">Откуда цифры</b> — подробный разбор в <code>RESULTS-BY-SOURCE.md</code>, длинный список ссылок в <code>SOURCES-LONG-HORIZON.md</code>. Ссылки на исходники также стоят внутри каждого блока исследований выше.</p>
  <p class="src">Богл · Vanguard · Morningstar · SPIVA · исследования S&amp;P · открытые сводки по хедж-фондам · спор Баффета · внутренний расчёт регулярных покупок $100/мес с 2021-01.</p>
  <p style="margin-top:1.2rem">H Funds · разбор публичных данных · не персональная инвестиционная рекомендация.</p>
</footer>

<script>
const DCA = __DCA_JS__;
function boot() {
  if (typeof Chart === 'undefined') {
    document.querySelectorAll('.err').forEach(function(e){ e.style.display='block'; e.textContent='Не загрузилась библиотека графиков.'; });
    return;
  }
  Chart.defaults.color = '#8fa197';
  Chart.defaults.borderColor = 'rgba(220,235,225,.12)';
  Chart.defaults.font.family = 'Manrope';
  function mk(id, cfg) {
    var el = document.getElementById(id);
    if (!el) return;
    try { new Chart(el, cfg); }
    catch (e) {
      var err = document.getElementById('err-' + id);
      if (err) { err.style.display = 'block'; err.textContent = 'Ошибка графика: ' + e.message; }
    }
  }
  mk('spiva', {type:'bar', data:{labels:['1г','3г','5г','10г','15г','20г'], datasets:[{data:[65,85,76,84,90,92], backgroundColor:'rgba(227,93,77,.82)', borderRadius:8}]}, options:{responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{y:{max:100, ticks:{callback:function(v){return v+'%';}}}}}});
  var y = []; for (var i=0;i<11;i++) y.push(2008+i);
  var s=1e6,f=1e6,S=[],F=[];
  for (i=0;i<y.length;i++) { S.push(Math.round(s)); F.push(Math.round(f)); s*=1.071; f*=1.022; }
  mk('buffett', {type:'line', data:{labels:y, datasets:[{label:'Индекс S&P (~7.1%)', data:S, borderColor:'#2db88a', fill:true, backgroundColor:'rgba(45,184,138,.12)', tension:.25, pointRadius:2}, {label:'Проф. корзина (~2.2%)', data:F, borderColor:'#e35d4d', fill:true, backgroundColor:'rgba(227,93,77,.1)', tension:.25, pointRadius:2}]}, options:{responsive:true, maintainAspectRatio:false, scales:{y:{ticks:{callback:function(v){return '$'+(v/1e6).toFixed(1)+'M';}}}}}});
  mk('years', {type:'bar', data:{labels:['10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'], datasets:[{label:'S&P 500', data:[12.6,0,13.3,29.6,11.5,-0.7,9.8,18.7,-6.6,30.4,15.8,26.6,-19.6,26.3,25], backgroundColor:'rgba(238,246,241,.85)'}, {label:'Средний хедж-фонд', data:[10.2,-5.2,6.5,11.1,3.2,1.8,5.4,8.6,-4,10.4,11.2,10.2,-4.2,7.5,8.5], backgroundColor:'rgba(45,184,138,.85)'}]}, options:{responsive:true, maintainAspectRatio:false, scales:{y:{ticks:{callback:function(v){return v+'%';}}}}}});
  mk('chart-dca', {type:'line', data:{labels:DCA.labels, datasets:[{label:'Сколько внесли $', data:DCA.inv, borderColor:'#6b8a9a', tension:.2, pointRadius:0, borderWidth:2}, {label:'Сколько стоит портфель $', data:DCA.val, borderColor:'#2db88a', fill:true, backgroundColor:'rgba(45,184,138,.12)', tension:.2, pointRadius:0, borderWidth:2}]}, options:{responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom'}}, scales:{x:{ticks:{maxTicks:10, autoSkip:true}}, y:{ticks:{callback:function(v){return '$'+v;}}}}}});
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
else boot();
</script>
</body>
</html>
"""

repl = {
    "__DCA_JS__": dca_js,
    "__YEARS_ROWS__": years_rows,
    "__SPOT_NOW__": spot_now,
    "__RET_NOW__": ret_now,
    "__INVESTED__": invested,
    "__BTC__": btc,
    "__AVG_COST__": avg_cost,
    "__VALUE_NOW__": value_now,
    "__VALUE_OLD__": value_old,
    "__PNL_NOW__": pnl_now,
    "__SPOT_OLD__": spot_old,
    "__RET_OLD__": ret_old,
    "__MONTHS__": months,
    "__AS_OF_OLD__": as_of_old,
    "__AS_OF_NOW__": as_of_now,
}
for k, v in repl.items():
    html = html.replace(k, v)

(root / "index.html").write_text(html, encoding="utf-8")
print("Wrote", root / "index.html", "bytes", len(html.encode()))
