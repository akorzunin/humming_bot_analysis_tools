from typing import Optional, Union
from pandas import DataFrame
import pandas as pd
import asyncio
from binance.client import Client, AsyncClient
#load .env variables
import os
from dotenv import load_dotenv
load_dotenv()
# load_dotenv()
TOKEN = os.getenv('TOKEN')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

ticker_unwanted = [
    'firstId', 
    'lastId', 
    'count', 
    'lastQty', 
    'bidQty', 
    'askQty',
    'bidPrice',
    'askPrice',
    'openTime',
    'closeTime',
    'prevClosePrice',
    
]

async def get_all_pairs(client: Optional[AsyncClient] = None) -> tuple:
    if client:
        data = await client.get_ticker()
    else:
        client = get_client()
        data = client.get_ticker()
    df = pd.DataFrame(data, index=range(len(data)))
    return tuple(df['symbol'].to_numpy())

async def get_pair_ticker(pair: str, client: Optional[AsyncClient] = None, ) -> DataFrame:
    pair = pair.upper()
    if client:
        data = await client.get_ticker(
            symbol=pair,
        )
    else: 
        client = get_client()
        data = client.get_ticker(
            symbol=pair,
        )
    df = pd.DataFrame(data, index=[0])
    # remove unwanted fields
    item_list = [e for e in list(df.keys()) if e not in ticker_unwanted]
    df = df[item_list]
    return df

async def get_all_pair_ticker(client: Optional[AsyncClient] = None, ) -> DataFrame:
    if client:
        data = await client.get_ticker()
    else: 
        client = get_client()
        data = client.get_ticker()
    return pd.DataFrame(data, index=range(len(data)))

def get_client():
    return Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

async def get_async_client():
    return await AsyncClient.create(BINANCE_API_KEY, BINANCE_SECRET_KEY)

async def create_async_client():
    return AsyncClient.create(BINANCE_API_KEY, BINANCE_SECRET_KEY)


if __name__ == '__main__':
    async def main() -> None:
        client = await get_async_client() 
        df = await get_pair_ticker(
            pair='RVNUSDT'
        )
        print(df)
        await client.close_connection()
    # get RVNUSDT pair for example
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())