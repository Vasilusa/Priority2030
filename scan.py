import urllib
from htmldom import htmldom
import requests
from peewee import *
from datetime import *
import re
import locale

locale.setlocale(locale.LC_TIME, ('ru_RU', 'UTF-8'))

QUERY_STRING = "Приоритет 2030"
START = 0
END = 1000
DB_URL = 'postgresql://postgres:example@localhost:5432/Priority2030'
START_DATE='01.01.2017'
END_DATE=''

db = PostgresqlDatabase(DB_URL)


class Query(Model):
    id = IntegerField(primary_key=True)
    query_string = CharField()
    start = IntegerField()
    end = IntegerField()
    start_date = DateField()
    class Meta:
        database=db
        db_table='query'
    
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
    class Meta:
        database=db
        db_table='result'
        
def search(start, end):
    query = Query.create(
        query_string=QUERY_STRING, 
        start=start, 
        end=end
    )
    query.save()
    print("Запрос id=%s" % query.id)
    
    start = START
    number = START
    while start < end:
        print ("Блок от %s\n" % start)
        start = start + 10
        tbs = urllib.parse.quote_plus('cdr:1,cd_min:' + START_DATE + ',cd_max:' + END_DATE)
        query_url = 'https://www.google.com/search?q=' + urllib.parse.quote_plus(QUERY_STRING) + '&start=' + str(start) + '&tbs=' + tbs + '&filter=0';
        print('Query URL = ' + query_url)
        resp = requests.get(query_url, headers={'Accept': 'text/html', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0'})
        dom = htmldom.HtmlDom().createDom(resp.content.decode(resp.encoding))
        els=dom.find("div#search div.yuRUbf")
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
                query_id = query.id,
                url = url,
                title = title,
                site = site,
                date_str = date_str,
                number = number,
            )
            result.save()
    return query
        
def apply(query_id, callback):
    for result in Result.select().where(Result.query_id == query_id):
        try:
            callback(result)
        except:
            print('Ошибка в callback функции')


def download(result):
    print (result.id, result.url)
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
    print (result.id, result.url)
    if (result.content != None):
        for keyword in keywords:
            r = re.findall(keyword, result.content, re.IGNORECASE);
            value = value + len(r)
    result.intensity_1 = value
    result.save()

def calc_intensity_3(result):
    value = 0
    keywords = ['Приоритет\\s2030', 'Приоритет\\-2030']
    print (result.id, result.url)
    if (result.content != None):
        for keyword in keywords:
            r = re.findall(keyword, result.title, re.IGNORECASE);
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
    print (result.id, result.url)
    if (result.content != None):
        for keyword in keywords:
            r = re.findall(keyword, result.content, re.IGNORECASE);
            value = value + len(r)
    result.intensity_2 = value
    result.save()
            
def calc_intensity_composite(result):
    result.intensity_composite = result.intensity_1*10 + result.intensity_2+result.intensity_3*100
    result.save()

def calc_intensity(result):
    THREASHOLD_1=100
    THREASHOLD_2=300
    THREASHOLD_3=500
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


def fill_date(result):
    q = Query.get(Query.id==result.query_id)
    d = parse_date(result.date_str, q.start_date)
    if d is not None:
        result.when = d
        result.save()

query = search(0, 1000)    
query_id = query.id
apply(query_id, download)
apply(query_id, calc_intensity_1)
apply(query_id, calc_intensity_2)
apply(query_id, calc_intensity_3)
apply(query_id, calc_intensity_composite)
apply(query_id, calc_intensity)
apply(query_id, fill_date)
