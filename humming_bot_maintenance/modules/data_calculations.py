import logging
import numpy as np
import pandas as pd

def calc_profit(filled_df, total_usd, total_sub, ):
    filled_df['total_sub'] = np.nan
    for row in filled_df.itertuples():
        if row.trade_type == 'buy':
            total_usd -= float(row.fee_amount)
            total_sub += float(row.amount)
            filled_df.at[row.Index, ['total_usd']] = total_usd
            filled_df.at[row.Index, ['total_sub']] = total_sub
        elif row.trade_type == 'sell':
            total_usd += float(row.quote_asset_amount)
            total_sub -= float(row.amount)
            filled_df.at[row.Index, ['total_usd']] = total_usd
            filled_df.at[row.Index, ['total_sub']] = total_sub
    try:
        total_usd_ = filled_df['total_usd'].astype(np.float64)
        total_sub_ = filled_df['total_sub'].astype(np.float64)
        price_ = filled_df['price'].astype(np.float64)
        filled_df['net_worth'] = total_usd_ + total_sub_ * price_
        calc_rel_profit = lambda current, prev: round((current - prev) * 100/prev,2)
        filled_df['global_profit_abs'] = filled_df['net_worth'] - filled_df['net_worth'][0]
        filled_df['global_profit_rel'] = calc_rel_profit(filled_df['net_worth'], filled_df['net_worth'][0])

        filled_df['prev_profit_abs'] = filled_df['net_worth'] - filled_df['net_worth'].shift(fill_value=0)
        filled_df['prev_profit_rel'] = calc_rel_profit(filled_df['net_worth'], filled_df['net_worth'].shift(fill_value=0))
        filled_df['prev_profit_abs'].at[0] = 0
        filled_df['prev_profit_rel'].at[0] = 0
    except KeyError as e:
        logging.error(f'not works {e}')
        return None
    return filled_df

def calc_fee(df):
    fee_amount = df['fee_amount'].astype(float)
    quote_asset_amount = df['quote_asset_amount'].astype(float)
    df['fee'] =  fee_amount - quote_asset_amount 
    return df