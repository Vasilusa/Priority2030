import pycurl
import urllib
from htmldom import htmldom
import requests
import html
import psycopg2

class DB:
    def __init__(self, url):
        try:
            self.conn = psycopg2.connect(url)
        except:
            print("Ошибка соединения с базой данных")
        
    def save_query(self, query_string, start, end):
        with self.conn.cursor() as curs:
            curs.execute('INSERT INTO "query" ("query_string", "start", "end") VALUES (%s, %s, %s) RETURNING id', (query_string, start, end))
            query_id = curs.fetchone()[0]
        self.conn.commit()
        return query_id

    def save_record(self, query_id, url, title, site, date_str, number, content):
        with self.conn.cursor() as curs:
            curs.execute('INSERT INTO "result" ("query_id", "url", "title", "site", "date_str", "number", "content") VALUES (%s, %s, %s, %s, %s, %s, %s)', (query_id, url, title, site, date_str, number, content))
        self.conn.commit()
    

QUERY_STRING = "Приоритет 2030"
START = 0
END = 100
DB_URL = 'postgresql://scan@localhost:5432/scan'
START_DATE='01.01.2017'
END_DATE='15.05.2023'

db = DB(DB_URL);

query_id = db.save_query(QUERY_STRING, START, END)
print("Запрос id=%s" % query_id)
    
start = START
number = START
while start < END:
    print ("Блок от %s\n" % start)
    start = start + 10
    tbs = urllib.parse.quote_plus('cdr:1,cd_min:' + START_DATE + ',cd_max:' + END_DATE)
    query_url = 'https://www.google.com/search?q=' + urllib.parse.quote_plus(QUERY_STRING) + '&start=' + str(start) + '&tbs=' + tbs;
    print('Query URL = ' + query_url)
    resp = requests.get(query_url, headers={'Accept': 'text/html', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0'})
    dom = htmldom.HtmlDom().createDom(resp.content.decode(resp.encoding))
    els=dom.find("div#rso div.yuRUbf")
    for el in els:
        href = el.find("a").attr("href")
        print('url=' + href)
        title = el.find("h3").text()
        print('title=' + title)
        date_str = el.parent().next().find('div')[0].find("span > span").text()
        print('date=' + date_str)
        site = el.find("span.VuuXrf").text()
        print('site=' + site)
        number = number + 1
        if not href[0:4]=='http':
            break
        subResp = requests.get(href, allow_redirects=True, verify=False, headers={'Accept': 'text/html', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0'})
        print('encoding=' + subResp.encoding)
        print('headers=' + subResp.headers)
        try:
            content = subResp.content.decode(subResp.encoding)
        except:
            print("Не удается декодировать содержимое")
            content=None
        db.save_record(query_id, href, title, site, date_str, number, content)    
        
