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
<title>H Funds — простые индексы против дорогих фондов</title>
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
h1{font-family:Spectral,Georgia,serif;font-size:clamp(2rem,5vw,3.2rem);line-height:1.12;margin:0 0 1.1rem;max-width:18ch}
.lead{font-size:1.16rem;color:var(--muted);max-width:60ch;margin:0 0 1.6rem}
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
h3{font-size:1.1rem;margin:1.45rem 0 .5rem}
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
</style>
</head>
<body>
<nav class="toc"><div class="wrap">
  <b style="color:var(--text)">H Funds</b>
  <a href="#thesis">Главная мысль</a>
  <a href="#problem">О чём спор</a>
  <a href="#evidence">Цифры</a>
  <a href="#fees">Комиссии</a>
  <a href="#why">Почему так</a>
  <a href="#btc">Биткоин</a>
  <a href="#dca">Как копить</a>
  <a href="#end">Вывод</a>
</div></nav>

<header class="hero wrap">
  <div class="badge">Разбор на 50 лет данных · без рекламы фондов</div>
  <h1>Дорогие управляющие против простого рынка</h1>
  <p class="lead">
    Многие думают: «отдам деньги умным людям в фонд — они точно обыграют рынок».
    Мы проверили, что показывают большие отчёты за десятилетия.
    Картина повторяется снова и снова: <b style="color:var(--text)">большинство профессионалов не обгоняет простой рыночный индекс</b>.
    Ниже — простым языком, с цифрами и без сказки «я точно умнее рынка».
  </p>

  <div class="gloss">
    <b>Короткий словарик.</b>
    <b>Индекс</b> — это «средний портфель» большого рынка. Самый известный в США — S&amp;P 500: корзина примерно из 500 крупнейших американских компаний.
    Купить индексный фонд = купить сразу почти весь этот рынок дёшево.
    <b>Активный фонд / хедж-фонд</b> — команда, которая сама выбирает бумаги и берёт за это плату.
    Часто слышите «2 и 20»: около 2% от ваших денег каждый год + 20% от прибыли сверху.
  </div>

  <div class="thesis" id="thesis">
    <h2 style="margin-top:0">Главная мысль</h2>
    <p>
      <strong>Самая рабочая схема для обычного человека — покупать широкий рынок дёшево и держать долго.</strong>
      Не потому что управляющие «глупые». А потому что комиссии, конкуренция и исчезновение неудачных фондов
      делают победу над индексом редкой на дистанции 10–20 лет.
    </p>
    <p style="margin-bottom:0" class="muted">
      Отсюда практический вывод для крипты: базой копим биткоин (как «главный актив» цифрового рынка),
      а не гоняемся за чужими «фондами-гениями». Копим регулярно — по плану, небольшими суммами (DCA).
      DeFi — это уже надстройка: как заставить капитал работать, а не замена самой покупки.
    </p>
  </div>

  <div class="kpis">
    <div class="kpi"><em>За 20 лет (отчёт SPIVA)</em><b>~92%</b><span>крупных активных фондов США проиграли простому индексу S&amp;P 500</span></div>
    <div class="kpi"><em>Спор Баффета, 10 лет</em><b>2.2% vs 7.1%</b><span>профессиональные «фонды фондов» после всех платежей vs индекс — в среднем за год</span></div>
    <div class="kpi"><em>Покупка биткоина по $100/мес с 2021</em><b class="ok">+__RET_NOW__%</b><span>пересчёт на цену ~$__SPOT_NOW__ на 23.09.2026</span></div>
  </div>
</header>

<section class="wrap" id="problem">
  <h2>О чём вообще этот спор</h2>
  <p>
    В США вокруг денег сильная культура «умных управляющих». Кажется логичным:
    раз человек целый день смотрит рынок — он же обыграет «тупой» индекс.
    К концу 2025 года в хедж-фондах крутилось уже больше <span class="num">$5 триллионов</span>.
    Но большой объём денег — это не доказательство, что средний клиент богатеет быстрее рынка.
  </p>
  <p>Мы честно делим вопрос на два:</p>
  <div class="two">
    <div class="box">
      <h3>Вопрос 1. Навык</h3>
      <p class="muted" style="margin:0">Даже если никто не берёт с вас огромную комиссию — часто ли профессионалы обыгрывают простой индекс?</p>
    </div>
    <div class="box">
      <h3>Вопрос 2. Реальные деньги клиента</h3>
      <p class="muted" style="margin:0">А если сверху ещё 2% в год и 20% от прибыли — остаётся ли смысл вместо дешёвого индекса?</p>
    </div>
  </div>
  <p class="callout">Где данных мало — говорим прямо. Полноценной «истории хедж-фондов на 50 лет» нет: нормальная статистика индустрии начинается примерно с 1990-х. Зато по обычным активным фондам акций США есть десятки лет отчётов.</p>
</section>

<section class="wrap" id="evidence">
  <h2>Что показывают цифры</h2>
  <p class="muted">Ниже — не мнения блогеров, а крупные исследования. Подробные ссылки — в файлах рядом с сайтом.</p>

  <h3>1. Джон Богл (основатель Vanguard): 1970 → 2001</h3>
  <p>Он посмотрел сотни американских фондов акций на длинном отрезке.</p>
  <div class="box">
    <table>
      <tr><th>Что смотрели</th><th class="n">Результат</th></tr>
      <tr><td>Сколько фондов стартовало</td><td class="n">355</td></tr>
      <tr><td>Сколько закрылось по дороге</td><td class="n">197 (больше половины)</td></tr>
      <tr><td>Средняя доходность тех, кто выжил</td><td class="n">10.4% в год</td></tr>
      <tr><td>Доходность индекса S&amp;P 500</td><td class="n">11.8% в год</td></tr>
      <tr><td>Отставание «выживших»</td><td class="n">−1.4 пункта в год</td></tr>
      <tr><td>Если учесть закрывшиеся фонды</td><td class="n">примерно −2.9 пункта в год</td></tr>
    </table>
    <p class="note">Смысл простой: в красивых таблицах часто остаются только «живые». Мёртвые исчезают — и кажется, что все крутые.</p>
  </div>

  <h3>2. Vanguard: 50 лет индексного фонда</h3>
  <p>
    Первый массовый индексный фонд почти один в один повторяет рынок полвека:
    около <span class="num">11.4%</span> в год при рынке около <span class="num">11.7%</span>.
    Активные фонды при этом дороже обслуживать. И на каждом пятилетнем отрезке заметная доля фондов просто исчезает.
  </p>

  <h3>3. Morningstar: кто выжил и реально обогнал дешёвый аналог</h3>
  <div class="two">
    <div class="box">
      <p>Считают жёстко: фонд должен <b>не умереть</b> и <b>обогнать</b> средний дешёвый фонд своего типа.</p>
      <ul>
        <li>Все активные, 10 лет: успех примерно у <b>29%</b></li>
        <li>Крупные смешанные США, 10 лет: около <b>15%</b></li>
        <li>Те же, 15 лет: около <b>9%</b></li>
        <li>«Ростовые» крупные, 15 лет: около <b>3.5%</b></li>
      </ul>
    </div>
    <div class="box">
      <p class="muted" style="margin:0">На одном годе иногда почти 50/50. На 10–20 годах шансы «я победил рынок и не закрылся» резко падают. Из стартовавших за 20 лет в large-blend доживает примерно треть.</p>
    </div>
  </div>

  <h3>4. SPIVA: самый прямой ответ «кто проиграл индексу»</h3>
  <p>Ежегодный отчёт S&amp;P: сравнивают активные фонды США с индексом.</p>
  <div class="two">
    <div class="box">
      <div class="chart"><canvas id="spiva"></canvas></div>
      <p class="err" id="err-spiva">График не загрузился — обновите страницу.</p>
      <p class="note">Доля крупных активных фондов, которые заработали меньше, чем S&amp;P 500.</p>
    </div>
    <div class="box">
      <table>
        <tr><th>Срок</th><th class="n">Проиграли индексу</th></tr>
        <tr><td>1 год</td><td class="n">65%</td></tr>
        <tr><td>3 года</td><td class="n">85%</td></tr>
        <tr><td>5 лет</td><td class="n">76%</td></tr>
        <tr><td>10 лет</td><td class="n">84%</td></tr>
        <tr><td>15 лет</td><td class="n">90%</td></tr>
        <tr><td>20 лет</td><td class="n">~92%</td></tr>
      </table>
      <p class="note">Чем дольше смотрим — тем меньше «победителей». На 20 годах примерно 9 из 10 не догоняют индекс.</p>
    </div>
  </div>

  <h3>5. Ещё один отчёт S&amp;P за 2001–2020</h3>
  <p>
    За 20 календарных лет большинство крупных активных фондов обогнало индекс только в <b>трёх годах из двадцати</b>.
    Накопительно рынок вырос примерно на <span class="num">+322%</span>, средний активный фонд — около <span class="num">+257%</span>.
  </p>

  <h3>6. Хедж-фонды: когда они «выглядят умнее»</h3>
  <p>
    Если сравнивать средний хедж-фонд с S&amp;P 500 по годам, индекс чаще впереди в сильный рост.
    Хедж-фонды чаще выглядят лучше в плохие годы — когда рынок падает, а они падают меньше.
    Это другая задача: не «выжать максимум», а «меньше трястись в кризис».
  </p>
  <div class="box">
    <div class="chart tall"><canvas id="years"></canvas></div>
    <p class="err" id="err-years">График не загрузился.</p>
    <p class="note">2010–2024. Светлые столбцы — доходность S&amp;P за год. Зелёные — приближение среднего хедж-фонда по открытым сводкам.</p>
  </div>
  <ul>
    <li>За roughly 2010–2025 средний хедж-фонд обгонял S&amp;P примерно в <b>3</b> годах из 16.</li>
    <li>В одном 10-летнем срезе «глобальный» индекс хедж-фондов давал около <b>1.5%</b> в год при S&amp;P около <b>13%</b>.</li>
  </ul>

  <h3>7. Самый известный публичный матч: спор Баффета</h3>
  <p>
    Уоррен Баффет поспорил, что за 10 лет обычный фонд на индекс S&amp;P 500 обгонит корзину из пяти «фондов фондов»
    (деньги через кучу профессиональных хедж-фондов, уже после всех оплат).
    С 2008 по 2017 индекс победил всухую.
  </p>
  <div class="two">
    <div class="box">
      <div class="chart tall"><canvas id="buffett"></canvas></div>
      <p class="err" id="err-buffett">График не загрузился.</p>
      <p class="note">Как рос бы условный миллион долларов: ~7.1% в год у индекса против ~2.2% у профессиональной корзины.</p>
    </div>
    <div class="box">
      <ul>
        <li>Индекс: примерно <b>+126%</b> за 10 лет</li>
        <li>Профессиональная корзина: примерно <b>+36%</b></li>
        <li>Среднегодовая: <b>7.1%</b> против <b>2.2%</b></li>
        <li>Из пяти «фондов фондов» индекс обогнал <b>все пять</b></li>
      </ul>
      <p class="muted">Это не один неудачный менеджер. Это отбор команд, который всё равно проиграл дешёвому рынку после комиссий.</p>
    </div>
  </div>
</section>

<section class="wrap" id="fees">
  <h2>Почему комиссии часто решают исход</h2>
  <p>
    Представьте: рынок за год вырос на 10%. Дешёвый индекс почти всё это оставляет вам.
    А классический хедж-фонд сначала забирает около 2% «за управление», а потом ещё примерно пятую часть прибыли.
    Если сверху ещё «фонд фондов» — слоёв оплаты становится больше.
  </p>
  <div class="two">
    <div class="box">
      <div class="chart"><canvas id="chart-fees"></canvas></div>
      <p class="err" id="err-chart-fees">График не загрузился.</p>
      <p class="note">Одинаковый «грязный» рост 10% в год до выплат. Зелёный — почти без расходов. Жёлтый и красный — после типичных комиссий фонда.</p>
    </div>
    <div class="box">
      <p>Даже если управляющий в среднем зарабатывает «примерно как рынок», вам после оплаты часто остаётся меньше индекса.</p>
      <p class="muted" style="margin-bottom:0">Отдельный честный случай: некоторые стратегии полезны как «подушка» в кризис. Но это уже не обещание «я точно сделаю вам больше, чем S&amp;P».</p>
    </div>
  </div>
</section>

<section class="wrap" id="why">
  <h2>Почему индекс выигрывает «по устройству»</h2>
  <div class="two">
    <div class="box">
      <h3>1. Внутри рынка активные менеджеры играют друг против друга</h3>
      <p class="muted">До комиссий их общий результат примерно равен рынку. После комиссий — рынок минус плата. Индекс почти не платит этот налог.</p>
    </div>
    <div class="box">
      <h3>2. В витрине остаются победители</h3>
      <p class="muted">Провалившиеся фонды закрывают. Вы смотрите на выживших — и кажется, что «все успешные».</p>
    </div>
  </div>
  <div class="two">
    <div class="box">
      <h3>3. Путают «я умный» и «просто рынок вырос»</h3>
      <p class="muted">Часть красивой доходности — это просто движение всего рынка акций, а не сверхнавык управляющего.</p>
    </div>
    <div class="box">
      <h3>4. Время убивает случайную удачу</h3>
      <p class="muted">За один год кому-то везёт. За 20 лет отчёты показывают: большинство остаётся позади индекса.</p>
    </div>
  </div>
  <div class="verdict">
    <p><strong>Итог двух вопросов один.</strong>
      Без огромных комиссий большинство не обгоняет индекс. С комиссиями — ещё труднее.
      Значит, база для длинных денег: держать широкий рынок дёшево.</p>
  </div>
</section>

<section class="wrap" id="btc">
  <h2>Как это связано с биткоином</h2>
  <p>
    Мы не говорим «биткоину нарисована вечная зелёная свеча».
    Мы переносим уже проверенный принцип: <b>держать главный актив класса, а не платить среднему «гению» за обещание сверхдоходности</b>.
  </p>
  <p>
    В обычных деньгах США таким «главным показателем» десятилетиями был широкий индекс акций.
    В цифровых активах для многих роль базового актива занимает биткоин:
    понятное ограниченное предложение, мировые торги, нет совета директоров, который может внезапно «напечатать» ещё.
  </p>
  <p>
    DeFi здесь — не вместо покупки, а <b>поверх</b>: как заставить уже купленный капитал приносить доход
    (с оговоркой про риски смарт-контрактов и ликвидаций). Сначала позиция. Потом — вопрос, работает ли капитал, пока рынок набирает ход.
  </p>
  <p class="callout">В логике еженедельных сводок то же самое: основной капитал уже в рынке, докупки по плану, регулярность важнее эмоций от заголовка.</p>
</section>

<section class="wrap" id="dca">
  <h2>Как копить: регулярные покупки (DCA)</h2>
  <div class="gloss">
    <b>DCA</b> — dollar-cost averaging: каждый месяц (или неделю) покупаете на одну и ту же сумму.
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
    <p class="note">Серая линия — сколько денег вы внесли. Зелёная — сколько стоит портфель. Последняя точка зелёной пересчитана на текущий спот ~$84 065.</p>
  </div>

  <h3>Что дал каждый год покупок</h3>
  <div class="box">
    <table>
      <tr><th>Год</th><th class="n">Вложили</th><th class="n">Купили BTC</th><th class="n">Средняя цена года</th><th class="n">Оценка на старом споте*</th><th class="n">Результат*</th></tr>
__YEARS_ROWS__    </table>
    <p class="note">*Оценка на цене июля 2026 (~$65k) — как в исходном расчёте. Годы просадки купили больше монет. Смысл DCA — не поймать идеальную точку, а не выпасть из плана.</p>
  </div>

  <div class="verdict">
    <p><strong>DCA не обещает, что каждый месяц будет плюс.</strong>
      Он обещает другое: вы системно набираете базовый актив и меньше спорите с рынком из ленты новостей.
      Это та же идея, что и с индексом: меньше героизма, больше дисциплины.</p>
  </div>
</section>

<section class="wrap" id="end">
  <h2>Собираем всё вместе</h2>
  <p>
    Спор звучал статусно: «может, отдать деньги самым умным фондам?»
    Данные ответили спокойно: <b>средний результат после всех оплат редко бьёт дешёвый рыночный показатель</b>.
  </p>
  <p>
    Значит, рациональная база — владеть тем, что отражает рост всего класса активов.
    В классическом мире США — широкий индекс акций. В цифровом слое портфеля для многих — биткоин.
    Как копить — регулярно, по правилам, а не от эмоции заголовка.
  </p>
  <div class="thesis">
    <p style="margin:0">
      <strong>Проще часто оказывается сильнее.</strong>
      Не потому что мир награждает лень — потому что сложность обычно продаёт услугу,
      а после комиссий большинству остаётся меньше, чем дал бы простой рынок.
      Мы искали не удобный лозунг, а то, что повторяется в отчётах. Оно повторяется.
    </p>
  </div>
</section>

<footer class="wrap foot">
  <p><b style="color:var(--text)">Откуда цифры</b> — подробный разбор в <code>RESULTS-BY-SOURCE.md</code>, длинный список ссылок в <code>SOURCES-LONG-HORIZON.md</code>.</p>
  <p class="src">Bogle · Vanguard · Morningstar · SPIVA · исследования S&amp;P · открытые сводки по хедж-фондам · спор Баффета · внутренний расчёт DCA $100/мес с 2021-01.</p>
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
  var feeYears=[]; for (i=0;i<16;i++) feeYears.push(2010+i);
  var a=100,b=100,c=100,A=[],B=[],C=[];
  for (i=0;i<feeYears.length;i++) { A.push(+a.toFixed(1)); B.push(+b.toFixed(1)); C.push(+c.toFixed(1)); a*=1.10; var g=10; b*=1+(g-2-0.2*(g-2))/100; c*=1+(g-2-0.3*(g-2))/100; }
  mk('chart-fees', {type:'line', data:{labels:feeYears, datasets:[{label:'Почти без комиссий (~10%)', data:A, borderColor:'#2db88a', tension:.25, pointRadius:0}, {label:'После 2% + 20%', data:B, borderColor:'#d4a017', tension:.25, pointRadius:0}, {label:'После 2% + 30%', data:C, borderColor:'#e35d4d', tension:.25, pointRadius:0}]}, options:{responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom'}}}});
  mk('chart-dca', {type:'line', data:{labels:DCA.labels, datasets:[{label:'Сколько внесли $', data:DCA.inv, borderColor:'#6b8a9a', tension:.2, pointRadius:0, borderWidth:2}, {label:'Сколько стоит портфель $', data:DCA.val, borderColor:'#2db88a', fill:true, backgroundColor:'rgba(45,184,138,.12)', tension:.2, pointRadius:0, borderWidth:2}]}, options:{responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom'}}, scales:{x:{ticks:{maxTicks:10, autoSkip:true}}, y:{ticks:{callback:function(v){return '$'+v;}}}}}});
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
else boot();
</script>
</body>
</html>
"""

repl = {
    "__RET_NOW__": ret_now,
    "__SPOT_NOW__": spot_now,
    "__AS_OF_OLD__": as_of_old,
    "__AS_OF_NOW__": as_of_now,
    "__SPOT_OLD__": spot_old,
    "__INVESTED__": invested,
    "__BTC__": btc,
    "__VALUE_OLD__": value_old,
    "__VALUE_NOW__": value_now,
    "__RET_OLD__": ret_old,
    "__PNL_NOW__": pnl_now,
    "__MONTHS__": months,
    "__AVG_COST__": avg_cost,
    "__YEARS_ROWS__": years_rows,
    "__DCA_JS__": dca_js,
}
for k, v in repl.items():
    html = html.replace(k, v)

(root / "index.html").write_text(html, encoding="utf-8")
print("wrote", root / "index.html", "bytes", len(html.encode()))
