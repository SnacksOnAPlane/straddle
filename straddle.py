import csv
from wallstreet import Stock, Call, Put
import pdb
import datetime
from google_sheet import GoogleSheet
from datetime import date, timedelta
from bs4 import BeautifulSoup
from urllib.request import urlopen
import lxml

# https://biz.yahoo.com/research/earncal/20170320.html

def get_closest(price, strikes):
  return min(strikes, key=lambda x:abs(x - price))

def get_options(sym, strike_date):
  put = Put(sym, d=strike_date.day, m=strike_date.month, y=strike_date.year, strict=False)
  call = Call(sym, d=strike_date.day, m=strike_date.month, y=strike_date.year, strict=False)
  stock = Stock(sym)
  price = get_closest(stock.price, put.strikes)
  put.set_strike(price)
  call.set_strike(price)

  return [stock.price, price, put.price, call.price, put.expiration, call.expiration]

def get_earnings_reports(day):
  # 20170320
  day_str = day.strftime("%Y%m%d")
  url = "https://biz.yahoo.com/research/earncal/%s.html" % day_str
  soup = BeautifulSoup(urlopen(url).read(), 'lxml')
  tr = soup.find('tr', bgcolor='a0b8c8')
  table = tr.parent
  trs = table.find_all("tr")[2:-1]
  for tr in trs:
    row = [td.text for td in tr.find_all("td")]
    name = row[0]
    sym = row[1]
    yield name, sym

sheet = GoogleSheet()
today = date.today()
two_weeks = today + timedelta(14)
for i in range(1,22): # 3 weeks
  day = today + timedelta(i)
  sheet_vals = []
  for name, sym in get_earnings_reports(day):
    print(sym)
    try:
      data = get_options(sym, two_weeks)
      print(data)
      sheet_vals.append([sym, date.today().strftime("%d-%m-%Y"), day.strftime("%d-%m-%Y")] + data)
    except LookupError:
      print(f"No options for {sym}")
    except ValueError:
      print(f"Date not available for {sym}")
  sheet.update(sheet_vals)
