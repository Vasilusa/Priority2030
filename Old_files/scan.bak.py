import urllib
from htmldom import htmldom
import requests
from peewee import *
from datetime import *
import re
import locale
import matplotlib.pyplot as plt

locale.setlocale(locale.LC_TIME, ('ru_RU', 'UTF-8'))

QUERY_STRING = "Приоритет 2030"
START = 0
END = 1000
# DB_URL = 'postgresql://postgres:example@localhost:5432/Priority2030'
DB_URL = 'postgresql://scan@localhost:5432/scan'
START_DATE = '01.01.2017'
END_DATE = ''

THREASHOLD_1 = 100
THREASHOLD_2 = 300
THREASHOLD_3 = 500

db = PostgresqlDatabase(DB_URL)


class Query(Model):
    id = IntegerField(primary_key=True)
    query_string = CharField()
    start = IntegerField()
    end = IntegerField()
    start_date = DateField()

    class Meta:
        database = db
        db_table = 'query'


class Result(Model):
    id = IntegerField(primary_key=True)
    query_id = IntegerField()
    url = CharField()
    site = CharField()
    title = CharField()
    description = TextField()
    content = TextField()
    number = IntegerField()
    date_str = TextField()
    encoding = CharField()
    content_type = CharField()
    intensity = IntegerField()
    intensity_1 = IntegerField()
    intensity_2 = IntegerField()
    intensity_3 = IntegerField()
    intensity_composite = IntegerField()
    when = DateField()

    class Meta:
        database = db
        db_table = 'result'


def search(query_string, start, end):
    query = Query.create(
        query_string=query_string,
        start=start, 
        end=end
    )
    query.save()
    print("Запрос id=%s" % query.id)
    
    current = start
    number = start
    while current < end:
        print("Блок от %s\n" % start)
        current = current + 10
        tbs = urllib.parse.quote_plus('cdr:1,cd_min:' + START_DATE + ',cd_max:' + END_DATE)
        query_url = 'https://www.google.com/search?q=' + urllib.parse.quote_plus(QUERY_STRING) + '&start=' + str(start) + '&tbs=' + tbs
        print('Query URL = ' + query_url)
        resp = requests.get(query_url, headers={'Accept': 'text/html', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0'})
        dom = htmldom.HtmlDom().createDom(resp.content.decode(resp.encoding))
        els = dom.find("div#search div.yuRUbf")
        for el in els:
            url = el.find("a").attr("href")
            print('url=' + url)
            title = el.find("h3").text()
            print('title=' + title)
            date_str = el.parent().next().find('div')[0].find("span > span").text()
            print('date=' + date_str)
            site = el.find("span.VuuXrf").text()
            print('site=' + site)
            number = number + 1
            result = Result.create(
                query_id=query.id,
                url=url,
                title=title,
                site=site,
                date_str=date_str,
                number=number,
            )
            result.save()
    return query


def apply(query_id, callback):
    query = Query.select().where(Query.id == query_id).get()
    if query is not None:
        for result in Result.select().where(Result.query_id == query.id):
            try:
                callback(result, query)
            except:
                print('Ошибка в callback функции')


def download(result):
    print(result.id, result.url)
    resp = requests.get(result.url, allow_redirects=True, verify=False, headers={'Accept': 'text/html', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0'})
    result.encoding = resp.encoding
    result.content_type = resp.headers['Content-Type']
    result.save()
    try:
        result.content = resp.content.decode(resp.encoding)
        result.save()
    except:
        print("Не удается декодировать содержимое")


def calc_intensity_1(result):
    value = 0
    keywords = ['Приоритет\\s2030', 'Приоритет\\-2030']
    print(result.id, result.url)
    if result.content is not None:
        for keyword in keywords:
            r = re.findall(keyword, result.content, re.IGNORECASE)
            value = value + len(r)
    result.intensity_1 = value
    result.save()


def calc_intensity_3(result):
    value = 0
    keywords = ['Приоритет\\s2030', 'Приоритет\\-2030']
    print(result.id, result.url)
    if result.content is not None:
        for keyword in keywords:
            r = re.findall(keyword, result.title, re.IGNORECASE)
            value = value + len(r)
    result.intensity_3 = value
    result.save()


def calc_intensity_2(result):
    value = 0
    keywords = [
        'программа', 
        'Приоритет-2030', 
        'ресурсы', 
        'вклад', 
        'университеты', 
        'национальные цели', 
        'развитие', 
        'Российская Федерация', 
        'научно-образовательный потенциал', 
        'научные организации', 
        'образовательные организации', 
        'высшее образование', 
        'социально-экономическое развитие', 
        'цифровые технологии', 
        'кадровое обеспечение', 
        'инновации', 
        'межинституциональное взаимодействие', 
        'международное сотрудничество', 
        'конкурс', 
        'экспертиза', 
        'грант', 
        'российские университеты', 
        'прогрессивные современные университеты', 
        'научно-технологическое развитие', 
        'страна', 
        'программа развития', 
        'университет', 
        '2021-2030 годы', 
        'реализация', 
        'стратегическое академическое лидерство', 
        'Министерство науки и высшего образования', 
        'отбор', 
        'участие', 
        'цифровые кафедры', 
        'цифровая кафедра', 
        'программа', 
        'Приоритет 2030', 
        'цель', 
        'университеты', 
        'лидеры', 
        'научное знание', 
        'технологии', 
        'разработки', 
        'российская экономика', 
        'социальная сфера', 
        'высшее образование', 
        'практики', 
        'научно-исследовательская деятельность', 
        'инновации', 
        'образовательная деятельность', 
        'привлекательность', 
        'регионы России', 
        'иностранные студенты', 
        'зарубежные ученые', 
        'навыки', 
        'умения', 
        'рынок труда', 
        'научно-технологический прогресс', 
        'государственная поддержка', 
        'конкурентоспособность', 
        'трансформация', 
        'мировой рынок', 
        'интеграция', 
        'личностный потенциал', 
        'качество жизни', 
        'самореализация', 
        'задачи', 
        'исследования', 
        'разработки', 
        'кадровое обеспечение', 
        'инновационный потенциал', 
        'экономика страны', 
        'субъекты Российской Федерации', 
        'научно-технологический потенциал', 
        'продукты', 
        'сетевое взаимодействие', 
        'международное сотрудничество', 
        'цифровые компетенции', 
        'ИТ-специальности', 
        'образовательные услуги', 
        'научно-технические услуги', 
        'социальные услуги'
    ]
    print(result.id, result.url)
    if result.content is not None:
        for keyword in keywords:
            r = re.findall(keyword, result.content, re.IGNORECASE)
            value = value + len(r)
    result.intensity_2 = value
    result.save()


def calc_intensity_composite(result):
    result.intensity_composite = result.intensity_1*10 + result.intensity_2+result.intensity_3*100
    result.save()


def calc_intensity(result):
    if result.intensity_composite > THREASHOLD_3:
        result.intensity = 3
    elif result.intensity_composite > THREASHOLD_2:
        result.intensity = 2
    elif result.intensity_composite > THREASHOLD_1:
        result.intensity = 1
    else:
        result.intensity = 0
    result.save()


def parse_date(s, base_date):
    print(s)
    r = re.match('^(\\d+)\\s(\\w{3}).+(\\d{4})', s)
    if r is not None:
        return datetime.strptime(r.group(1) + ' ' + r.group(2) + ' ' + r.group(3), '%d %b %Y')
    r = re.match('^(\\d+)\\s(день|дня|дней)\\s(назад)', s)
    if r is not None:
        d = timedelta(days=int(r.group(1)))
        return base_date - d
    r = re.match('^(\\d+)\\s(час|часа|часов)\\s(назад)', s)
    if r is not None:
        d = timedelta(hours=int(r.group(1)))
        return datetime.now() - d
    r = re.match('^(\\d+)\\s(минута|минуты|минут)\\s(назад)', s)
    if r is not None:
        d = timedelta(minutes=int(r.group(1)))
        return datetime.now() - d


def fill_date(result, query):
    d = parse_date(result.date_str, query.start_date)
    if d is not None:
        result.when = d
        result.save()


def get_hist_data(query_id):
    dates = []
    dates_1 = []
    dates_2 = []
    dates_3 = []
    for result in Result.select().where(Result.query_id == query_id):
        dates.append(result.when)
        if result.intensity == 1:
            dates_1.append(result.when)
        elif result.intensity == 2:
            dates_2.append(result.when)
        elif result.intensity == 3:
            dates_3.append(result.when)
    return dates, dates_1, dates_2, dates_3


def get_plot_data(query_id, start_date, end_date):
    dates = []
    values = []
    values_3 = []
    values_2 = []
    values_1 = []
    current_date = start_date
    while current_date < end_date:
        dates.append(current_date)
        values.append(0)
        values_1.append(0)
        values_2.append(0)
        values_3.append(0)
        current_date = increment(current_date)
    for result in Result.select().where(Result.query_id == query_id):
        if result.when is not None:
            interval = diff(result.when, start_date)
            if 0 <= interval < len(dates):
                values[interval] += 1
                if result.intensity == 1:
                    values_1[interval] += 1
                elif result.intensity == 2:
                    values_2[interval] += 1
                elif result.intensity == 3:
                    values_3[interval] += 1

    return dates, values, values_1, values_2, values_3


def increment(date1):
    d = date1.day
    m = date1.month
    y = date1.year
    if m == 12:
        m = 1
        y += 1
    else:
        m += 1
    return date(y, m, d)


def diff(date2, date1):
    m = 12 * (date2.year - date1.year) + (date2.month - date1.month)
    if date2.day >= date1.day:
        return m
    else:
        return m - 1


# query = search(QUERY_STRING, START, END)
# query_id = query.id
# apply(query_id, fill_date)
# apply(query_id, download)
# apply(query_id, calc_intensity_1)
# apply(query_id, calc_intensity_2)
# apply(query_id, calc_intensity_3)
# apply(query_id, calc_intensity_composite)
# apply(query_id, calc_intensity)

hist_data = get_hist_data(148)

# plt.hist(hist_data[0], 50)
plt.hist(
    hist_data,
    24,
    label=['Всего упоминаний', 'Упоминаний в интенсивностью 1', 'Упоминаний в интенсивностью 2', 'Упоминаний в интенсивностью 3'],
    color=['black', 'lightgreen', 'blue', 'red']
)

# data = get_plot_data(148, date(2017,1,1), date(2023,5,1))
#
# print(data)
# # plt.plot(data[0], data[1], label='Всего упоминаний')
# # plt.plot(data[0], data[2], label='Упоминаний в интенсивностью 1')
# # plt.plot(data[0], data[3], label='Упоминаний в интенсивностью 2')
# # plt.plot(data[0], data[4], label='Упоминаний в интенсивностью 3')
# plt.bar(data[0], data[1], label='Всего упоминаний')
# plt.bar(data[0], data[2], label='Упоминаний в интенсивностью 1')
# plt.bar(data[0], data[3], label='Упоминаний в интенсивностью 2')
# plt.bar(data[0], data[4], label='Упоминаний в интенсивностью 3')
plt.xlabel('Дата')
plt.ylabel('Количество упоминаний')
plt.yscale('log')
plt.legend()
plt.show()