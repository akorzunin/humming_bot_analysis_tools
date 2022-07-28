
import pandas as pd
from dateutil.parser import parse
import humming_bot_maintenance.modules.candle_plot as candle_plot
from datetime import datetime

import pytz
import humming_bot_maintenance.modules.binance_api_handler as bah
client = bah.get_client()

tzdata_bot = pytz.timezone('UTC') 
tzdata_local = pytz.timezone('Europe/Moscow') 

def parse_df(df, interval):
    df['Timestamp'] = df['Timestamp'].map(lambda x: parse(x))
    df['Timestamp'] = df['Timestamp'].map(lambda x: tzdata_bot.localize(x).astimezone(tzdata_local))
    df
    global start_date
    global end_date
    start_date = df.Timestamp[0]
    end_date = df.Timestamp[len(df)-1]

    time_dict = dict(
        start_date=start_date,
        end_date=end_date,
        total_time= end_date - start_date,
    )
    time_dict
    # type	sell_price	buy_price	fee	RVN	USD	_amount	timestamp
    global trade_data
    trade_data = pd.DataFrame(df)
    trade_data.rename(
        columns=dict(
            Timestamp='timestamp',
            Side='type',
            Amount='_amount',
            Price='sell_price',
        ),
        inplace=True,
    )
    trade_data['buy_price'] = trade_data['sell_price']


    client.get_server_time()
    dd= client.get_klines(
        symbol='RVNUSDT',
        interval=interval,
        startTime=int(datetime.timestamp(start_date) * 1000),
        endTime=int(datetime.timestamp(end_date) * 1000),
    )

    stock_data = pd.DataFrame(
        dd, 
        columns=['Timestamp', 'Open', 'High', 'Low', 'Close', *range(5,12)],
    )
    stock_data['Date'] = stock_data['Timestamp'].to_frame().applymap(lambda time_: datetime.fromtimestamp(time_/1000.0))
    return stock_data

def plot_graph(
    df, 
    settintgs_override: dict = dict(),      
    interval=None,      
    start_date=None,        
    end_date=None,      
    trade_data=None,        
    symbol=None,
    **kwargs):      
    plot = candle_plot.CandlePlot(
        df=df,
        **kwargs,
    )

    settings = {
        'candle_plot': 1,
        # 'MA_lines': 1,
        'add_trades': 1,
        # 'add_profit': 1,
        # 'profit_annotations': 0, 
        # 'amplitude': 0, 
        # 'MACD_lines': True, # to do
        # 'EMA_lines': True, # to do
    }
    settings |= settintgs_override
    fig = plot.use_settings(
        settings=settings,
        # GO_WIDTH=1300,
        # GO_HEIGHT=750,
        title='Humming bot data',
        pair=symbol,
        interval=interval,
        limit=f'{start_date} to {end_date}',
        MA_list=(2, 25, 100, 200),
        trade_data=trade_data,
    )
    fig.update_yaxes(fixedrange=False)
    return fig

