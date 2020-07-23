"""
This script retrieves a quarterly snapshot of the constituents of the S&P 500 back to Q1 2008, from
Wikipedia, and saves each of them as a csv file into a local /data/ folder.

It stops at 2008 because before then, Wikipedia did not have a table of tickers for the S&P 500.

This can be used to create a delisted database of S&P 500 companies back to 2008.

This can be used for rough backtesting of stock picking strategies when combined with 
point-in-time financials scraped from EDGAR, as long as the strategy uses quarterly rebalancing.

"""

import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def main():
    df = pd.read_csv('sp500_wiki_links.csv')
    df.QTR_START = pd.to_datetime(df.QTR_START)
    df.QTR_NAME = df.QTR_START.apply(get_q_num)
    df.WIKI_LINK.astype(str)
    for i in df.index:
        qtr = df.QTR_NAME[i]
        update = str(df.ACTUAL_DATE[i])
        data = pd.read_html(df.WIKI_LINK[i])
        df_table = data[0]
        keep_columns = ['Symbol', 'Ticker symbol', 'Security', 'Company']
        columns = [column for column in df_table.columns if column in keep_columns]
        df_new = df_table[columns]
        if 'Symbol' in df_new.columns:
            df_new.rename(columns = {'Symbol':'TICKER'}, inplace = True)
        elif 'Ticker symbol' in df_new.columns:
            df_new.rename(columns = {'Ticker symbol':'TICKER'}, inplace = True)
        elif 'Security' in df_new.columns:
            df_new.rename(columns = {'Security':'COMPANY'}, inplace = True)
        elif 'Company' in df_new.columns:
            df_new.rename(columns = {'Company':'COMPANY'}, inplace = True)
        df_new.to_csv(f'data/sp500_{qtr}_updated_{update}.csv')
        print(qtr+' done.')
    print('Scraping complete.')

def get_q_start(datetime_object):
    current_date = datetime_object
    current_quarter = round((current_date.month - 1) / 3 + 1)
    first_date = datetime(current_date.year, 3 * current_quarter - 2, 1)
    return first_date.date()

#def get_q_end(datetime_object):
#    current_date = datetime_object
#    current_quarter = round((current_date.month - 1) / 3 + 1)
#    last_date = datetime(current_date.year, 3 * current_quarter + 1, 1)\
#            + timedelta(days=-1)
#    return last_date.date()

def get_q_num(datetime_object):
    output = ''
    year = str(get_q_start(datetime_object).year)
    if get_q_start(datetime_object).month == 1:
        output = '1Q'+year
    elif get_q_start(datetime_object).month == 4:
        output = '2Q'+year
    elif get_q_start(datetime_object).month == 7:
        output = '3Q'+year
    elif get_q_start(datetime_object).month == 10:
        output = '4Q'+year
    return output

if __name__ == "__main__":
    main()