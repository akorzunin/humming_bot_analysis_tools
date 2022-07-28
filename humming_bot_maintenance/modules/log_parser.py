import contextlib
import json
import os
import pandas as pd
from datetime import datetime
from datetime import tzinfo
import logging
import pytz
import re
import humming_bot_maintenance.modules.stock_plot as sp
import humming_bot_maintenance.modules.plot_tools as pt
import humming_bot_maintenance.modules.utils as utils
import humming_bot_maintenance.modules.data_calculations as dc
tzdata_bot = pytz.timezone('UTC') 
tzdata_local = pytz.timezone('Europe/Moscow') 

        
def read_logs(FILEPATH: str) -> pd.DataFrame:
    with open(FILEPATH, 'r') as f:
        logs_df = parse_logs_from_file(f)
    return get_df_from_logs(logs_df)

def read_raw_logs(FILEPATH: str) -> pd.DataFrame:
    with open(FILEPATH, 'r') as f:
        return parse_logs_from_file(f)

def parse_symbol(sample: str) -> str:
    symbol = re.split('://|/', sample)[1]
    return ''.join(symbol.split('-'))

def get_df_from_logs(raw_logs: pd.DataFrame) -> pd.DataFrame:
    order_set = set()
    plot_data = pd.DataFrame(
        columns=[
            'start_timestamp', 
            'end_timestamp',
            'start_datetime', 
            'end_datetime',
            'order_id', 
            'end_reason', # filled / canselled 
            'amount', 
            'fee', 
            'quote_asset_amount', 
            'fee_amount',
            'trade_type', # buy or sell 
            'price',
        ], 
        # index=range(10),
    )
    for row in raw_logs.itertuples(index=1):

        if row.event_name in ['BuyOrderCreatedEvent', 'SellOrderCreatedEvent']:
            # can read: timestamp->start_time amount price trade_type
            trade_type = row.order_id.split(':')[0]

            # add order_id to set
            order_set.add(row.order_id)
            tf = pd.DataFrame(
                dict(
                    order_id=row.order_id,
                    start_timestamp=row.timestamp,
                    start_datetime=datetime.fromtimestamp(row.timestamp, tz=tzdata_local),
                    amount=row.amount,
                    price=row.price,
                    trade_type=trade_type,
                ), 
                index=[0],
            )
            plot_data = pd.concat(
                [plot_data, tf],
                ignore_index=True,
            )

        if row.event_name in ['BuyOrderCompletedEvent', 'SellOrderCompletedEvent']\
        and row.order_id in order_set:
            # find row index by order_id
            ind = plot_data.loc[plot_data['order_id'] == row.order_id].index[0]
            plot_data.at[ind, ['end_timestamp']] = row.timestamp
            plot_data.at[ind, ['end_datetime']] = datetime.fromtimestamp(row.timestamp, tz=tzdata_local)
            plot_data.at[ind, ['quote_asset_amount']] = row.quote_asset_amount
            plot_data.at[ind, ['fee_amount']] = row.fee_amount
            plot_data.at[ind, ['end_reason']] = 'filled'
        if row.event_name == 'OrderCancelledEvent'\
        and row.order_id in order_set:
            # find row index by order_id
            try:
                ind = plot_data.loc[plot_data['order_id'] == row.order_id].index[0]
                plot_data.at[ind, ['end_timestamp']] = row.timestamp
                plot_data.at[ind, ['end_datetime']] = datetime.fromtimestamp(row.timestamp, tz=tzdata_local)
                plot_data.at[ind, ['quote_asset_amount']] = row.quote_asset_amount
                plot_data.at[ind, ['end_reason']] = 'canselled'
            except AttributeError as e:
                logging.error(f'Unable to find attr {e}')
    not_canselled = plot_data.loc[pd.isnull(plot_data['end_timestamp'])]
    for row in not_canselled.iterrows():
        plot_data.at[row[0], ['end_reason']] = 'not_canselled'
    return plot_data

def parse_logs_from_file(file, filename: str = None) -> pd.DataFrame:
    data = file.readlines()

    raw_json = []
    for line in data:
        split_line = line.split(' - ')
        if 'EVENT_LOG' in split_line:
            raw_json.append(
                json.loads(split_line[-1])
            )
    raw_logs = pd.DataFrame(raw_json)
    del_col_list = [
        # 'order_id',
        'exchange_order_id',
        'event_source',
        'position',
        'order_type',
    ]
    for i in del_col_list:
        with contextlib.suppress(KeyError):
            del raw_logs[i]
    try:
        raw_logs = raw_logs.loc[
            raw_logs['event_name'].isin([
                'OrderFilledEvent', 
                'OrderCancelledEvent',
                'BuyOrderCompletedEvent',
                'SellOrderCompletedEvent', 
                'BuyOrderCreatedEvent',
                'SellOrderCreatedEvent',
            ])
        ]
        raw_logs['Date'] = raw_logs['timestamp'].to_frame().applymap(lambda time_: datetime.fromtimestamp(time_))
    except KeyError:
        logging.warning(f'Log file {filename} does not have events')
        return pd.DataFrame()
    return raw_logs


def generate_log_filenames(main_log: str, dates: list[str]) -> list[str]:
    log_filenames = [f'{main_log}.{date}' for date in dates]
    log_filenames.append(main_log)
    return log_filenames

def localize_df(
    df: pd.DataFrame, 
    tzdata_bot: tzinfo, 
    tzdata_local: tzinfo
) -> pd.DataFrame:
    with contextlib.suppress(ValueError):
        df['start_datetime'] = df['start_datetime'].map(lambda x: tzdata_bot.localize(x).astimezone(tzdata_local))
        df['end_datetime'] = df['end_datetime'].map(lambda x: x if pd.isnull(x) else tzdata_bot.localize(x).astimezone(tzdata_local))
    return df

def get_df_timelimits(df: pd.DataFrame) -> tuple[datetime, datetime]: 
    '''Return start_time,  end_time'''
    start_time = pd.Timestamp(df.loc[[0], 'start_datetime'].values[0])
    if pd.isnull(df.loc[[len(df)-1], 'end_datetime']).bool():
        # if end_datetime is NaN
        end_time = pd.Timestamp(df.loc[[len(df)-1], 'start_datetime'].values[0])
    else:
        end_time = pd.Timestamp(df.loc[[len(df)-1], 'end_datetime'].values[0])
        
    return start_time, end_time

# TODO: add typing
def get_df_klines(
    start: datetime,
    end: datetime,
    symbol: str,
    interval: str,
    client # TODO find the type
):
    klines = client.get_historical_klines(
        symbol=symbol,
        interval=interval, 
        start_str=str(start),
        end_str=str(end),
    )
    data = pd.DataFrame(klines)
    # create colums name
    data.columns = ['open_time','open', 'high', 'low', 'close', 'volume','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol', 'ignore']
    # change the timestamp
    data.index = [datetime.fromtimestamp(x/1000.0) for x in data.close_time]
    data=data.reset_index()
    data.columns = ['Date', *data.columns[1:]]
    data['Date'] = data['Date'].map(lambda x: tzdata_local.localize(x).astimezone(tzdata_local))
    return data

# TODO move to pt
def get_klines_plot(data, interval, symbol):
    col_names = dict(
        open_col  = 'open',
        high_col = 'high',
        low_col = 'low',
        close_col = 'close',
        date_col = 'Date',
    )

    return sp.plot_graph(
        df=data,
        interval=interval,
        symbol=symbol,
        **col_names,
        settintgs_override=dict(
            add_trades=0,
        )
    )

def parse_df_by_type(
    df: pd.DataFrame
) -> tuple[
    pd.DataFrame, 
    pd.DataFrame, 
    pd.DataFrame
]:
    df_filed_buy = df.loc[df['end_reason'] == 'filled'].loc[df['trade_type'] == 'buy']
    df_filed_sell = df.loc[df['end_reason'] == 'filled'].loc[df['trade_type'] == 'sell']
    df_canselled = df.loc[df['end_reason'] == 'canselled']
    return df_filed_buy, df_filed_sell, df_canselled
# TODO move to plot tolls
def parse_hover(df: pd.DataFrame) -> list[str]:
    def hover_format(x): 
        x = iter(x)
        return f'''
        <b>order_id: {next(x)}</b><br>
        end_reason: {next(x)} {next(x)}<br>
        price: {next(x)}<br>
        amount: {next(x)}<br>
        quote_asset_amount: {next(x)}<br>
        start_datetime: {next(x)}<br>
        end_datetime: {next(x)}<br>
        '''
    hover_list = [
        hover_format((
            order_id, 
            trade_type,
            end_reason,
            price,
            amount,
            quote_asset_amount,
            start_datetime,
            end_datetime,

        )) 
        for order_id, 
            trade_type, 
            end_reason,
            price,
            amount,
            quote_asset_amount,
            start_datetime,
            end_datetime,

        in zip(
            df['order_id'], 
            df['trade_type'], 
            df['end_reason'],
            df['price'],
            df['amount'],
            df['quote_asset_amount'],
            df['start_datetime'],
            df['end_datetime'],
        )
    ]
    assert len(df) == len(hover_list)
    return hover_list

def parse_log_dates(log_path: str) -> tuple[list[str], str]:
    '''return date_list, strategy_name'''
    abs_log_path = os.path.abspath(log_path)
    dir_abs_path = os.path.dirname(abs_log_path)
    arr = os.listdir(dir_abs_path)
    date_list = []
    strategy_name = None
    base_file_name = os.path.basename(abs_log_path)
    for i in arr:
        if base_file_name in i:
            postfix = i.split('.')[-1]
            if postfix != 'log':
                date_list.append(postfix)
            else:
                strategy_name = base_file_name.split('.')[0]
    date_list.sort(reverse=False)
    if not date_list and not strategy_name:
        raise ValueError
    return date_list, strategy_name

#TODO move to data calc
def calc_fee(df):
    fee_amount = df['fee_amount'].astype(float)
    quote_asset_amount = df['quote_asset_amount'].astype(float)
    df['fee'] =  fee_amount - quote_asset_amount 
    return df

def read_data_from_logs(LATEST_LOG_FILEs, client, INTERVAL, init_usd=100, init_sub=0):
    logs_data = {}
    figs_data = {}
    for LATEST_LOG_FILE in LATEST_LOG_FILEs:
        fig, df = pt.view_log_trades(
            latest_log=LATEST_LOG_FILE,
            # log_dates=LOG_DATES,
            # SYMBOL=SYMBOL,
            INTERVAL=INTERVAL,
            client=client,
        )
        filled_df = utils.get_filled_df(df)
        filled_df = dc.calc_profit(filled_df, init_usd, init_sub)
        logs_data[LATEST_LOG_FILE.split("_")[-1]] = filled_df
        figs_data[LATEST_LOG_FILE.split("_")[-1]] = fig
    return logs_data, figs_data

def get_folder_logs(
    folder_path: str, 
    bot_instances: list, 
    alg_prefix: str
) -> list[str]:
    folder_abs_path = os.path.abspath(folder_path)
    valid_bot_folders = [
        i for i in os.listdir(folder_abs_path) if i in bot_instances
    ]  # bot_instances
    latest_logs = []
    for bot_folder in valid_bot_folders:
        bot_log_folders = os.path.join(folder_abs_path, bot_folder)
        try:
            latest_logs.append(
                os.path.join(
                    bot_log_folders,
                    'logs',
                    [
                        log_name
                        for log_name in os.listdir(os.path.join(bot_log_folders, "logs"))
                        if alg_prefix in log_name and log_name.split(".")[-1] == "log"
                    ][0]
                )
            )
        except IndexError as e:
            logging.warning(f'No logs found for bot: {bot_folder}, alg: {alg_prefix} {e}')
    return latest_logs
