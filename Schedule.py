import schedule
import time
from TradingView import TradingView
import requests

url = 'http://localhost:9090/api/Candles'


def job():
    tv = TradingView(symbol="FX:EURUSD")
    result = tv.do()
    print(result)
    requests.post(url, data=result)


schedule.every(1).minutes.do(job)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except:
        continue
