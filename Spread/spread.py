from sklearn.linear_model import LinearRegression
from datetime import datetime
import pandas as pd
import numpy as np
import glob
import sys
import os
import re


def parse_args():
    data_path = sys.argv
    return data_path


def get_time(entries):
    ec_date = []
    quarter_year = []

    for file in entries:
        basename = os.path.basename(file)
        quarter_f = basename[0:2]
        year_f = basename[3:7]

        quarter_year.append('{}_{}'.format(quarter_f, year_f))

        with open(file, 'r') as call:
            raw_txt = call.read()
            ec_date.extend(re.findall(r"[\d]{1,2} [ADFJMNOS]\w* [\d]{4}", raw_txt[:120]))

    ec_date = list(map(lambda x: datetime.strptime(x, '%d %B %Y'), ec_date))

    return ec_date, quarter_year


def get_trend(df_p, date, days):
    trend = []

    for i in date:
        if np.sign(days) < 0:

            price_range = df_p.iloc[df_p.index.get_loc(i) + days:df_p.index.get_loc(i), ]
        else:
            price_range = df_p.iloc[df_p.index.get_loc(i):df_p.index.get_loc(i) + days, ]

        reg = LinearRegression()
        x = np.array(range(1, abs(days) + 1)).reshape(-1, 1)
        y = price_range.values.reshape(-1, 1)

        reg.fit(x, y)

        trend.append(reg.coef_.item())

    return trend


def main():
    try:
        arg = parse_args()
        earning_dir = arg[1]
        price_dir = arg[2]
        eps_dir = arg[3]
        output_dir = arg[4]
    except:
        print('Usage: python spread.py <earning call path> <price path> <eps_path> <output path>')
        sys.exit()

    # get a list of all the files in a directory
    entries = []

    for f in glob.glob('{}/*'.format(earning_dir)):
        entries.append(f)

    ec_date, quarter_year = get_time(entries)

    df_eps = pd.read_excel(eps_dir)
    df_eps['EPS_Spread'] = df_eps['Reported_EPS'] - df_eps['Consensus_Estimate']
    df_eps['Quarter'] = df_eps['Quarter'].str.replace(' ', '_')

    df_price = pd.read_csv(price_dir, index_col='date', parse_dates=True)['close']
    trend_before = get_trend(df_price, ec_date, -5)
    trend_after = get_trend(df_price, ec_date, 5)

    df_trend = pd.DataFrame({'Quarter_Year': quarter_year, 'Trend_Before': trend_before, 'Trend_After': trend_after})
    df_trend['Trend_Spread'] = df_trend['Trend_After'] - df_trend['Trend_Before']

    df_spread = pd.merge(df_eps[['Quarter', 'EPS_Spread']], df_trend[['Quarter_Year', 'Trend_Spread']],
                         left_on="Quarter", right_on='Quarter_Year', how='left')
    df_spread = df_spread[['Quarter_Year', 'EPS_Spread', 'Trend_Spread']].dropna(axis=0)
    df_spread.to_csv('{}/spread.csv'.format(output_dir))


if __name__ == '__main__':
    main()
