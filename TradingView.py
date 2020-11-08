from websocket import create_connection
import json
import random
import string
import re
import datetime
import pytz


class TradingView:
    def __init__(self, symbol):
        self.headers = json.dumps({'Origin': 'https://data.tradingview.com'})
        self.symbol = symbol

    def do(self):
        ws = create_connection('wss://data.tradingview.com/socket.io/websocket', headers=self.headers)
        session = self.generateSession()
        chart_session = self.generateChartSession()
        self.sendMessage(ws, "set_auth_token", ["unauthorized_user_token"])
        self.sendMessage(ws, "chart_create_session", [chart_session, ""])
        self.sendMessage(ws, "quote_create_session", [session])
        self.sendMessage(ws, "quote_set_fields",
                         [session, "ch", "chp", "current_session", "description", "local_description", "language",
                          "exchange",
                          "fractional", "is_tradable", "lp", "lp_time", "minmov", "minmove2", "original_name",
                          "pricescale",
                          "pro_name", "short_name", "type", "update_mode", "volume", "currency_code", "rchp", "rtc"])
        self.sendMessage(ws, "quote_add_symbols", [session, self.symbol, {"flags": ['force_permission']}])
        self.sendMessage(ws, "quote_fast_symbols", [session, self.symbol])

        message = json.dumps({"symbol": self.symbol, "adjustment": "splits", "session": "extended"})
        self.sendMessage(ws, "resolve_symbol",
                         [chart_session, "symbol_1",
                          "=" + message])
        self.sendMessage(ws, "create_series", [chart_session, "s1", "s1", "symbol_1", "1", 2])
        a = ""
        result = None
        while True:
            try:
                result = ws.recv()
                a = a + result + "\n"
                str = re.search('"s":\[(.+?)\}\]', a)
                if str is not None:
                    out = str.group(1)
                    x = out.split(',{\"')
                    for xi in x:
                        xi = re.split('\[|:|,|\]', xi)
                        ts = datetime.datetime.fromtimestamp(float(xi[4]), tz=pytz.UTC).strftime("%Y/%m/%d, %H:%M:%S")
                        print(ts)
                        result = {
                            'currency': self.symbol,
                            'time': ts,
                            'open': xi[5],
                            'high': xi[6],
                            'low': xi[7],
                            'close': xi[8],
                            'volume': xi[9]
                        }
                        print(result)
                        break
                    break
            except Exception as e:
                print(e)
                break
        return result

    def generateSession(self):
        string_length = 12
        letters = string.ascii_lowercase
        random_string = ''.join(random.choice(letters) for i in range(string_length))
        return "qs_" + random_string

    def generateChartSession(self):
        string_length = 12
        letters = string.ascii_lowercase
        random_string = ''.join(random.choice(letters) for i in range(string_length))
        return "cs_" + random_string

    def prependHeader(self, st):
        return "~m~" + str(len(st)) + "~m~" + st

    def constructMessage(self, func, paramList):
        return json.dumps({
            "m": func,
            "p": paramList
        }, separators=(',', ':'))

    def createMessage(self, func, paramList):
        return self.prependHeader(self.constructMessage(func, paramList))

    def sendRawMessage(self, ws, message):
        ws.send(self.prependHeader(message))

    def sendMessage(self, ws, func, args):
        ws.send(self.createMessage(func, args))
