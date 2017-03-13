import csv
from wallstreet import Stock, Call, Put
import pdb
import datetime

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

  return (sym, stock.price, price, put.price, call.price, put.expiration, call.expiration)

with open("earnings-3-20-2017.csv", "r") as csvfile:
  reader = csv.reader(csvfile)
  date = datetime.datetime.strptime("03/20/2017", "%m/%d/%Y") + datetime.timedelta(days = 1)
  with open("straddles.csv", "w") as outcsv:
    writer = csv.writer(outcsv)
    writer.writerow(("Sym", "Price", "Strike", "Put", "Call", "PutExp", "CallExp"))
    for row in reader:
      name, sym, _, _, _ = row
      try:
        data = get_options(sym, date)
        print(data)
        writer.writerow(data)
      except LookupError:
        print(f"No options for {sym}")
      except ValueError:
        print(f"Date not available for {sym}")
