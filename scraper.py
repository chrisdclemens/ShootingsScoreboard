from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
from dateutil.parser import parse
import datetime, pickle

def get_soup(url):
    page = uReq(url)
    html = page.read()
    page_soup = soup(html, 'html.parser')
    return page_soup

def create_date(date, year):
    if len(date.split(' ')) == 3: date = date.split(' ')[0].replace('.',' ')
#    print(date + ' ' + year)
#    print(parse(date + ' ' + year))
    return parse(date + ' ' + year)

def strip_bs(number):
    if number == '\nUnknown, Hundreds\n': return 200
    if '.' in number: return int(number.split('.')[0])
    if len(number.split('\n')) == 1: return int(number)
    if '–' in number: return int(number.split('–')[0])
    print(number)
    return int(number.split('\n')[1])

page_soup = get_soup('https://en.wikipedia.org/wiki/List_of_school_massacres_by_death_toll')
table = page_soup.find('table', {'class': 'wikitable'})
lines = table.findAll('tr')
keys = [k.text for k in lines.pop(0).findAll('th')]
shootings = []
for line in lines:
    shooting = {}
    for i in range(len(keys)):
        shooting[keys[i]] = line.findAll('td')[i].text
    shootings.append(shooting)

countries = {}

for shooting in shootings:
    date = create_date(shooting['Date'], shooting['Year'])
    if date < datetime.datetime(1999, 4, 20): continue
    if 'F' not in shooting['W']: continue
    country = shooting['Country']
    if country not in countries.keys():
        countries[country] = {'last': datetime.datetime(1980,1,1),
                'deaths': 0,
                'shootings': 0,
                'injuries': 0
                }
    countries[country]['last'] = max(date, countries[country]['last'])
    countries[country]['shootings'] += 1
    countries[country]['deaths'] += strip_bs(shooting['Killed'])
    countries[country]['injuries'] += strip_bs(shooting['Injured'])

try:
    code_lookup = pickle.load(open('code_lookup.p', 'rb'))
except:
    code_lookup = {}

def make_date_string(date):
    return str(date.year) + ', ' + str(date.month - 1) + ', ' + str(date.day)

for country_title in countries.keys():
    country = countries[country_title]
    if country_title not in code_lookup.keys():
        code_lookup[country_title] = input(country_title + ': ')
    pickle.dump(code_lookup, open('code_lookup.p', 'wb'))
    f = open('_countries/'+code_lookup[country_title]+'.html', 'w')
    f.write('---\n')
    f.write('title: ' + country_title + '\n')
    f.write('layout: scoreboard\n')
    f.write('shootings: ' + str(country['shootings']) + '\n')
    f.write('kills: ' + str(country['deaths']) + '\n')
    f.write('injuries: ' + str(country['injuries']) + '\n')
    f.write('last_shooting: ' + make_date_string(country['last']) + '\n')
    f.write('---')
    f.close()
