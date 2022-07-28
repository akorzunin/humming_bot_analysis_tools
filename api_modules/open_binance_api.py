'''a module that receives data about cryptocurrency from an open binance api'''
import json
from pandas.core.frame import DataFrame
import requests
from datetime import datetime
import pandas as pd

class OpenBinanceApi():
    @staticmethod
    def get_data(pair: str, interval: str, limit: int) -> list:
        resource = requests.get(f"https://api.binance.com/api/v1/klines?symbol=%s&interval={interval}&limit={limit}" % (pair))
        return json.loads(resource.text)

    @staticmethod
    def server_time() -> int:
        r = requests.get('https://api.binance.com/api/v1/time')
        return json.loads(r.text)['serverTime']


    @staticmethod
    def get_df(pair: str, interval: str, limit: int) -> DataFrame:
        data = OpenBinanceApi.get_data(pair, interval, limit)
        Date_list = []
        Open_list = []
        High_list = []
        Low_list = []
        Close_list = []

        for i in data:
            Date_list.append(i[0])
            Open_list.append(i[1])
            High_list.append(i[2])
            Low_list.append(i[3])
            Close_list.append(i[4])

        df = pd.DataFrame()
        df['Date'] = Date_list 
        # datetime objects
        df['Date'] = df['Date'].to_frame().applymap(lambda time_: datetime.fromtimestamp(time_/1000.0))
        # candlestick data
        df['Open'] = Open_list
        df['High'] = High_list
        df['Low'] = Low_list
        df['Close'] = Close_list 
        # unix time
        df['Real_Date'] = Date_list 

        return df


if __name__ == '__main__':
    p = OpenBinanceApi.get_data(
        pair = 'RVNUSDT',
        interval = '5m',
        limit = 1000,
    )
    print(p)
    df = OpenBinanceApi.get_df(
        pair = 'RVNUSDT',
        interval = '5m',
        limit = 1000,
    )
    print(df)
