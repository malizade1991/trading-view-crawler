import schedule
import time
from TradingView import TradingView
import requests
import datetime
import pytz

url = 'http://localhost:9090/api/Candles'


def job():
    tv = TradingView(symbol="FX:EURUSD")
    result = tv.do()
    requests.post(url, data=result)
    return None


schedule.every(1).seconds.do(job)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except:
        continue
