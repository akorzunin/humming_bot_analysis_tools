
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import logging
import ipywidgets as widgets

import humming_bot_maintenance.modules.stock_plot as sp
import humming_bot_maintenance.modules.log_parser as lp
import humming_bot_maintenance.modules.utils as utils

def plot_trades(fig, df, ):

    RECT_OPACITY = 0.4
    MAX_KNILNE_MP = 1.01
    MIN_KNILNE_MP = 0.99
    DF_MAX_PRICE = max(
        float(fig.data[0].high.max()), 
        float(df.price.max())
    ) * MAX_KNILNE_MP
    DF_MIN_PRICE = min(
        float(fig.data[0].low.min()), 
        float(df.price.min())
    ) * MIN_KNILNE_MP
    def get_bar_color(end_reason: str, trade_type: str) -> str:
        if end_reason == 'filled':
            if trade_type == 'sell': return "LightGreen" 
            if trade_type == 'buy': return "LightPink" 
        if end_reason == 'canselled': return "Gold"
        if end_reason == 'not_canselled': return "#9c9c9c"   
        return 'Red'
    def is_unique():
        trade_type = set()
        def check_trade_type(given_type: str):
            if given_type in trade_type: return False
            trade_type.add(given_type)
            return True
        return check_trade_type

    unique = is_unique()
    # Add shapes
    for row in df.itertuples():
        x0=row.start_datetime
        x1=row.end_datetime if not pd.isnull(row.end_datetime)\
            else df.start_datetime[-1:].values[0]
        y0=float(row.price) if row.trade_type == 'buy' else DF_MAX_PRICE
        y1=DF_MIN_PRICE if row.trade_type == 'buy' else float(row.price)
        fig.add_trace(
            go.Scatter(
                x=[x0,x0,x1,x1,x0], 
                y=[y0,y1,y1,y0,y0], 
                fill="toself",
                fillcolor=get_bar_color(row.end_reason, row.trade_type),
                mode='lines',
                line_color="LightSlateGrey",
                opacity=RECT_OPACITY,
                legendgroup="trade_bars",
                legendgrouptitle_text="Trade Bars",
                name=row.end_reason,
                legendrank=1002,
                showlegend=unique(str(row.trade_type) + str(row.end_reason)),
            )
        )

    my_list = lp.parse_df_by_type(df)
    def add_annotation_trace(df_, figure, name, color):

        figure.add_trace(
            go.Scatter(
                x=df_["end_datetime"], 
                y=df_["price"].astype(float), 
                mode='markers',
                name=name,
                hovertext=lp.parse_hover(df_),
                legendgroup="trades",
                legendgrouptitle_text="Trades",
                # name='annotations',
                showlegend=True,
                legendrank=1001,
                # hoveron='toself',
                marker=dict(
                    color=color,
                    size=4,
                    line=dict(
                        color='lightgrey',
                        width=1
                    )
                ),
            )
        )
        return figure
    name_list = ['filled_buy', 'filled_sell', 'canselled']
    color_list = ['red', 'green', 'yellow']
    name_color_gen = zip(name_list, color_list)
    for i in my_list: 
        fig = add_annotation_trace(i, fig, *next(name_color_gen))

    fig.update_layout(
        legend= {'itemsizing': 'constant'}
    )
    return fig

def view_df_trades(df, INTERVAL, client):
    df_start_time, df_end_time = lp.get_df_timelimits(df)

    if SYMBOL is None: SYMBOL = lp.parse_symbol(df.order_id[0])
    df_klines = lp.get_df_klines(df_start_time, df_end_time, SYMBOL, INTERVAL, client)
    fig = lp.get_klines_plot(df_klines, INTERVAL, SYMBOL)
    fig = plot_trades(fig, df)
    return fig, locals()

def view_log_trades(latest_log, INTERVAL, client, SYMBOL=None, log_dates=None):
    if log_dates is None:
        log_dates, strategy_name = lp.parse_log_dates(latest_log)
        logging.warning(f'Strategy: {strategy_name}')
    log_names = lp.generate_log_filenames(latest_log, log_dates)

    df_raw = pd.concat(
        [lp.read_raw_logs(log_name) for log_name in log_names]
    ).reset_index(drop=1)

    df = lp.get_df_from_logs(df_raw)
    df = lp.calc_fee(df)
    # find earliest and latest date
    df_start_time, df_end_time = lp.get_df_timelimits(df)

    if SYMBOL is None: SYMBOL = lp.parse_symbol(df.order_id[0])
    df_klines = lp.get_df_klines(df_start_time, df_end_time, SYMBOL, INTERVAL, client)
    fig = lp.get_klines_plot(df_klines, INTERVAL, SYMBOL)
    fig = plot_trades(fig, df)
    return fig, df

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

def plot_widget(figs_data: dict, tab):
    # tab = widgets.Tab()
    tab.children = [
        utils.plot_fig(figs_data[list(figs_data)[i]]) for i in range(len(figs_data))
    ]
    tab.titles = [
        tab.set_title(i, str(name))
        for i, name in zip(range(len(figs_data)), figs_data.keys())
    ]
    return tab

def plot_profit(filled_df):
    return px.line(
        filled_df,
        x="start_datetime",
        y=filled_df.columns[
            min(
                filled_df.columns.get_loc("global_profit_abs"),
                filled_df.columns.get_loc("global_profit_rel"),
                filled_df.columns.get_loc("prev_profit_abs"),
                filled_df.columns.get_loc("prev_profit_rel"),
            ) : max(
                filled_df.columns.get_loc("global_profit_abs"),
                filled_df.columns.get_loc("global_profit_rel"),
                filled_df.columns.get_loc("prev_profit_abs"),
                filled_df.columns.get_loc("prev_profit_rel"),
            )
            + 1
        ],
    )

def plot_df_widget(logs_data):
    tab = widgets.Tab()
    tab.children = [
        utils.setup_ui(logs_data[list(logs_data)[i]]) for i in range(len(logs_data))
    ]
    tab.titles = [
        tab.set_title(i, str(name))
        for i, name in zip(range(len(logs_data)), logs_data.keys())
    ]
    return tab