import copy
import logging
import os
import random

from dotenv import load_dotenv

load_dotenv()
PWD = os.getenv('PWD')
import sys

sys.path.insert(1, os.path.join(PWD, 'modules'))

import os
from collections import namedtuple

import pandas as pd
import plotly.graph_objects as go
from alg_modules.alg_ma import AlgMa
from api_modules.open_binance_api import OpenBinanceApi as OBA
from plotly.graph_objs._figure import Figure


class CandlePlot():
    # add ma lines separately
    # add flags separately
    # draw profit
    def __init__(self, **kwargs):
        super().__init__()

        self.df = kwargs.get('df', None)
        # df kwargs
        self.open_col  = kwargs.pop('open_col', 'Open')
        self.high_col = kwargs.pop('high_col', 'High')
        self.low_col = kwargs.pop('low_col', 'Low')
        self.close_col = kwargs.pop('close_col', 'Close')
        self.date_col = kwargs.pop('date_col', 'Date')
    
    def init_plot(self) -> Figure:
        df = self.df
        fig =  go.Figure(data=[
                go.Candlestick(
                    x=df[self.date_col],
                    legendgroup="klines",
                    legendgrouptitle_text="Klines Group Title",
                    name='pepe',
                    showlegend=True,
                )
                ])
        fig.update_layout(
            hovermode='x unified',
        )
        return fig

    def candle_plot(self, **kwargs):
        # sourcery skip: unwrap-iterable-construction
        '''kwargs:
            \ntitle
            \npair
            \ninterval
            \nlimit
            \nGO_HEIGHT
            \nGO_WIDTH'''
        df = self.df
        title = kwargs.get('title', 'MA plot')
        pair = kwargs.pop('pair', 'N/A')
        interval = kwargs.pop('interval', 'N/A')
        limit = kwargs.pop('limit', 'N/A')
        GO_HEIGHT = kwargs.pop('GO_HEIGHT', None)
        GO_WIDTH = kwargs.pop('GO_WIDTH', None)

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df[self.date_col],
                    open=df[self.open_col],
                    high=df[self.high_col],
                    low=df[self.low_col],
                    close=df[self.close_col], 
                    name=f'{pair}',
                    legendgroup="klines",
                )
            ]
        )

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="minute", stepmode="backward"),
                    dict(count=15, label="15m", step="minute", stepmode="backward"),
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=4, label="4h", step="hour", stepmode="backward"),
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        fig.update_layout(
            title=f'{title}     Interval: {interval}, Limit: {limit}',
            yaxis_title=f'{pair} Stock',
            xaxis_title='Time',
            height=GO_HEIGHT,
            width=GO_WIDTH,
            hovermode='x unified',
        )
        return fig
    
    def upd_range(self, fig_):
        fig_.update_yaxes(range=[
            self.df[self.date_col].iloc[0], 
            self.df[self.date_col].iloc[-1]
            ]
        )
        print(self.df[self.date_col].iloc[0], self.df[self.date_col].iloc[-1])
        return fig_

    def add_MA_lines(self, fig, **kwargs):
        df = self.df

        LINE_COLOR = [
            '#4EC5F1',
            '#8c3d9e',
            '#0df2c9',
            '#5dd459',
            '#c15c5c',
            ]   

        MA_list = kwargs.pop('MA_list', [0])
        # MA_2 = kwargs.pop('MA_2', 25)
        # MA_3 = kwargs.pop('MA_3', 100)

        LINE_WIDTH = kwargs.pop('WIDTH', 2)

        mov_avg = AlgMa.alg_main(df[self.open_col], MA_list=MA_list, )
        self.mov_avg = mov_avg

        for num, i in enumerate(MA_list):
            fig.add_trace(
                go.Scattergl(
                    x=df[self.date_col], 
                    y=mov_avg[num], 
                    legendgroup="MA lines",
                    name=f'MA {i}', 
                    line=dict(color=LINE_COLOR[num] if len(LINE_COLOR) > num else\
                        "#{:06x}".format(random.randint(0, 0xFFFFFF)), 
                    width=LINE_WIDTH))
                )

        return fig

    def add_trades(self, fig, **kwargs):
        
        FLAG_OPACITY = kwargs.pop('FLAG_OPACITY', 0.6)
        
        # try to get MA_list from class variable
        MA_list = kwargs.pop('MA_list', [0]) # None
        
        df = self.df
        assert len(df) > 1
        # in case we don't have MA values we need to calculate them
        try:
            mov_avg = self.mov_avg
        except AttributeError:
            mov_avg = AlgMa.alg_main(df[self.open_col], MA_list=MA_list, )
        self.MA_ints = AlgMa.find_intersections(df[self.date_col], mov_avg1=mov_avg[1].to_list(), mov_avg2=mov_avg[2].to_list())

        MA_ints = kwargs.pop('MA_ints', self.MA_ints)
        trade_data = kwargs.pop('trade_data', None)

        def remap(x: float, max_val: float, min_val: float, out_min: float, out_max: float ):
            return (x - min_val) * (out_max - out_min) / (max_val - min_val) + out_min
        
        min_val = float(min(
            df[self.open_col].min(), 
            df[self.high_col].min(), 
            df[self.low_col].min(), 
            df[self.close_col].min()
            ))
        max_val = float(max(
            df[self.open_col].max(), 
            df[self.high_col].max(), 
            df[self.low_col].max(), 
            df[self.close_col].max()
            ))
        self.candle_plot_min_val = min_val
        self.candle_plot_max_val = max_val


        if trade_data is None:
            self.draw_annotations_dep(fig, FLAG_OPACITY, MA_ints, remap, min_val, max_val)
        else:
            self.draw_annotations_from_df(fig, FLAG_OPACITY, trade_data, remap, min_val, max_val)

        return fig

    def draw_annotations_from_df(self, fig, FLAG_OPACITY, trade_data, remap, min_val, max_val):
        '''draw line and annotation to each element in df created from trade algoritm\n
        
        '''

        trade_flags = trade_data.itertuples(name='Row', index=False)

        rvn_usd = lambda x: 'RVN' #if x == 'sell' else 'USD'
        get_price = lambda x: x.sell_price if x.type == 'sell' else x.buy_price
        def_map = lambda i: remap(i.buy_price if i.type == 'buy' else i.sell_price, max_val, min_val, 0, 1)
        try:
            trade_flags_ = copy.deepcopy(trade_flags)
        except TypeError: 
            # somehow got an error that cant copy a generator 
            # but works fine w/ deepcopy in other cases
            logging.debug('[CANDLE PLOT] NO deepcopy')
            trade_flags_ = trade_data.itertuples(name='Row', index=False)
        fig.update_layout(
            legend=dict(
                yanchor="top",
                y=0.22,
                xanchor="left",
                x=0.01
            ),
            showlegend=True,
            xaxis_rangeslider_visible=True,        
            # draw ticks
            shapes = [dict(
                x0=i.timestamp, 
                x1=i.timestamp, 
                #pos of vertical line 
                y0=0 if i.type == 'buy' else def_map(i),
                y1=def_map(i) if i.type == 'buy' else 1, 
                xref='x', 
                yref='paper', 
                line_width=1, 
                opacity=FLAG_OPACITY,) for i in trade_flags ],
            annotations=[dict(
                x=i.timestamp, 
                y=(0.99 if i.type == 'sell' else 0.01), 
                xref='x', 
                yref='paper', 
                showarrow=False, 
                xanchor='left', 
                text=f'{i.type}',
                bgcolor='red' if i.type == 'buy' else 'green') for i in trade_flags_],
            hovermode='x unified',
        )

    def draw_annotations_dep(self, fig, FLAG_OPACITY, MA_ints, remap, min_val, max_val):
        '''draw line and annotation text on each element in MA_ints obect wich heve contain val, timestamp and time property
        \nshould not be used in future
        '''
        fig.update_layout(
                legend=dict(
                    yanchor="top",
                    y=0.22,
                    xanchor="left",
                    x=0.01
                ),
                showlegend=True,
                xaxis_rangeslider_visible=True,        
                # draw ticks
                shapes = [dict(
                    x0=i.timestamp, 
                    x1=i.timestamp, 
                    y0=0 if i.type == 'fall' else remap(i.val, max_val, min_val, 0, 1), 
                    y1=remap(i.val, max_val, min_val, 0, 1) if i.type == 'fall' else 1, 
                    xref='x', 
                    yref='paper', 
                    line_width=1, 
                    opacity=FLAG_OPACITY,) for i in MA_ints ],
                annotations=[dict(
                    x=i.timestamp, 
                    y=0.01 if i.type == 'fall' else 0.99 , 
                    xref='x', 
                    yref='paper', 
                    showarrow=False, 
                    xanchor='left', 
                    text=i.type, 
                    bgcolor='red' if i.type == 'fall' else 'green') for i in MA_ints],
                hovermode='x',
            )

    def add_profit(self, fig, **kwargs):
        trade_data = kwargs.get('trade_data')
        to_prof_s = 0
        to_prof_b = 0
        x0, x1 = (None, )*2
        for i in trade_data.itertuples(name='Row', index=False):
            if i.type == 'buy':
                x1= i.timestamp
                to_prof_b = i.buy_price
            elif i.type == 'sell' and x1 is not None:
                x0= i.timestamp
                to_prof_s = i.sell_price
            if x0 is not None and x1 is not None:
                fig.add_vrect(
                    x0=x0, 
                    x1=x1,
                    fillcolor="green"if (to_prof_s - to_prof_b)>0 else "LightSalmon", 
                    opacity=0.1,
                    layer="below", 
                    line_width=0,
                )
                x0, x1 = (None, )*2
        return fig

    def profit_annotations(self, fig, **kwargs):
        trade_data = kwargs.get('trade_data')

        def inverse(val):
            def inv_blink():
                nonlocal val 
                val = not val
                return val
            return inv_blink
        # simple blink function that returns true or false consequentially after each call
        inv = inverse(1)

        fig.update_layout(
            annotations=[dict(
                x=i.timestamp, 
                y=1 if inv() else 0.95, 
                xref='x', 
                yref='paper', 
                showarrow=False, 
                xanchor='left', 
                text=f'{round(i.profit_rel, 1)}%',
                bgcolor='green' if i.profit_rel > 0 else 'red',
                # verbose description when hover mouse on annotations
                hovertext=f'''[PROFIT] rel: {round(i.profit_abs, 4)
                    },abs: {i.profit_rel
                    }%, amount: {round(i._6, 2)}''',
                textangle=-45,
            ) for i in trade_data.itertuples(name='Row', index=False)
            ]
        )


        return fig

    def amplitude(self, fig, **kwargs):
        df = self.df
        def remap(x: float, max_val: float, min_val: float, out_min: float, out_max: float ):
            return (x - min_val) * (out_max - out_min) / (max_val - min_val) + out_min

        min_val = df['amplitude'].min()
        max_val = df['amplitude'].max()
        out_min = 0
        out_max = float(max(
            df['open_'].max(), 
            df['high_'].max(), 
            df['low_'].max(), 
            df['close_'].max()
            )) * 0.4
        df['map_amp'] = df['amplitude'].apply(lambda x : remap(x, max_val, min_val, out_min, out_max))

        for i, row in df.iterrows():
            df.loc[i, 'candle_type'] = 'open' if row['open_'] < row['close_'] else 'close'
        df_close, df_open = [x for _, x in df.groupby(df['candle_type'] == 'open')]

        amp_str = lambda x: f'Amplitude: {round(x, 2)}%'

        bar_settings = dict(
                name='Amplitude',
                offsetgroup='amp_bar',
                xperiodalignment='start',
                hoverinfo='all',
        )
        #positive amplitude bars
        fig.add_trace(
            go.Bar(
                x=df_open['date_created'],
                y=df_open['map_amp'],
                marker_color='green',
                hovertext=df_open['amplitude'].apply(amp_str).to_list(),
                **bar_settings,
            ),
        )
        #negative amplitude bars
        fig.add_trace(

            go.Bar(
                x=df_close['date_created'],
                y=df_close['map_amp'],
                marker_color='red',
                hovertext=df_close['amplitude'].apply(amp_str).to_list(),
                **bar_settings,
            )
        )

        return fig

    def MACD_lines(self, fig, **kwargs):
        
        return fig
    
    def use_settings(self, **kwargs):
        settings = {
            'candle_plot': False,
            'MA_lines': False,
            'add_trades': False,
            'add_profit': False,
            'profit_annotations': False,
            'amplitude': False,
            'MACD_lines': False,
            'EMA_lines': False,
        }

        settings |= kwargs['settings']
        fig = self.init_plot()
        if settings['candle_plot']:
            fig = self.candle_plot(**kwargs)
        if settings['MA_lines']:
            fig = self.add_MA_lines(fig, **kwargs)
        if settings['add_trades']:
            fig = self.add_trades(fig, **kwargs)
        if settings['add_profit']:
            fig = self.add_profit(fig, **kwargs)
        if settings['profit_annotations']:
            self.profit_annotations(fig, **kwargs)
        if settings['amplitude']:
            self.amplitude(fig, **kwargs)
        # if settings['MACD_lines']:
        #     self.MACD_lines(fig, **kwargs)
        # if settings['EMA_lines']:
        #     self.EMA_lines(fig, **kwargs)
        return fig

if __name__ == '__main__':

    CandlePlot.make_graph(
        pair = 'RVNUSDT',
        interval = '5m',
        limit = 1000,
        GO_HEIGHT=1000,
        GO_WIDTH=1000,
    )
