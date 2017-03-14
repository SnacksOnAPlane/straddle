from wallstreet import Stock, Call, Put
import pdb
import datetime
from google_sheet import GoogleSheet
from datetime import date, timedelta
from bs4 import BeautifulSoup
from urllib.request import urlopen
from concurrent.futures import ProcessPoolExecutor, as_completed
import ssl

# https://biz.yahoo.com/research/earncal/20170320.html

def format_date(day):
  retme = datetime.datetime.strptime(day, "%d-%m-%Y")
  return retme.date().isoformat()

def get_closest(price, strikes):
  return min(strikes, key=lambda x:abs(x - price))

def get_options(sym, strike_date):
  put = Put(sym, d=strike_date.day, m=strike_date.month, y=strike_date.year, strict=True, source='yahoo')
  call = Call(sym, d=strike_date.day, m=strike_date.month, y=strike_date.year, strict=True, source='yahoo')
  stock = Stock(sym)
  price = get_closest(stock.price, put.strikes)
  put.set_strike(price)
  call.set_strike(price)

  return [sym, stock.price, price, put.price, put.volume, call.price, call.volume, format_date(put.expiration), format_date(call.expiration)]

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
    if row[2] == "N/A":
      continue
    yield name, sym

sheet = GoogleSheet('1GCsHow61O6eXPCaviTCqUenlW4W8MGkl47CtIOhNUH4',1490010073)

def try_get_options(sym, name, day):
  try:
    data = get_options(sym, date(2017,3,17))
    print(sym, day, data)
    return [[sym, name, date.today().isoformat(), day.isoformat()] + data]
  except LookupError:
    print("No options for %s" % sym)
  except ValueError:
    print("Date not available for %s" % sym)

today = date.today()
two_weeks = today + timedelta(14)
with ProcessPoolExecutor(max_workers=4) as executor:
  for i in range(1,22): # 3 weeks
    fdata = []
    daydata = []
    day = today + timedelta(i)
    if day.weekday() in [5,6]:
      continue
    print(day)
    for name, sym in get_earnings_reports(day):
      if sym == '' or sym[0].isdigit() or '.' in sym:
        continue
      fdata.append(executor.submit(try_get_options, sym, name, day))

    for future in as_completed(fdata):
      try:
        data = future.result()
        if data:
          daydata.append(data)
      except ssl.SSLError:
        pass
      except ConnectionResetError:
        pass
    sheet.update(daydata)

