import pandas as pd
import time
from datetime import datetime
import numpy as np
import sys

def combine(pred, btc, day_data, command):
    greedy_approach = False

    if not day_data:
        btc['time_open'] = btc['time_open']/1000
        btc = btc.copy()
        btc['time_open'] = btc['time_open'].astype(int)
        btc = btc[['time_open', 'Close', 'High', 'Low']]
        btc.drop_duplicates(subset=['time_open'], keep='first', inplace=True)
    else:
        btc.drop_duplicates(subset=['Date'], keep='first', inplace=True)

    pred.drop_duplicates(subset=['date'], keep='first', inplace=True)

    if command == 0:
        for i, data in pred.iterrows():
            if not day_data:
                if data['entropy'] >= 0.4:
                    pred.at[i, 'pred'] = 0
            else:
                if data['entropy'] >= 0.95:
                    # pred.at[i, 'pred'] = 0
                    pass
    elif command == 1:
        for i, data in pred.iterrows():
            if not day_data:
                if data['pred'] == 1 and data['buy'] <= 0.8:
                    pred.at[i, 'pred'] = 0
                elif data['pred'] == 2 and data['sell'] <= 0.8:
                    pred.at[i, 'pred'] = 0
            else:
                if data['pred'] == 1 and data['buy'] <= 0.35:
                    pred.at[i, 'pred'] = 0
                elif data['pred'] == 2 and data['sell'] <= 0.35:
                    pred.at[i, 'pred'] = 0

    date_set = set()
    test = {}
    for i, data in pred.iterrows():
        if data['date'] not in test:
            test[data['date']] = 1
        else:
            test[data['date']] += 1
        date_set.add(data['date'])

    if not flag:
        btc = btc[btc['time_open'].isin(date_set)]
    else:
        btc = btc[btc['Date'].isin(date_set)]

    btc.reset_index(drop=True, inplace=True)
    pred.reset_index(drop=True, inplace=True)

    res = pd.concat([pred, btc], axis=1)
    res = res[['date', 'Close', 'High', 'Low', 'pred', 'hold', 'buy', 'sell']]

    if greedy_approach:
        buy = True
        for i, data in res.iterrows():
            if data['pred'] == 1:
                if buy:
                    buy = False
                else:
                    pred.at[i, 'pred'] = 0
            elif data['pred'] == 2:
                if not buy:
                    but = True
                else:
                    pred.at[i, 'pred'] = 0

    return res


def greedy(res):
    for i, data in res.iterrows():
        label = data['pred']
        price = data['Close']
        # print(label, price)
        if label == 1 and hold >= price:
            sharehold += hold/price
            hold = 0
                
        elif label == 2 and sharehold >= 0.5:
            hold += sharehold*price
            sharehold = 0


    latest_price = res.iloc[-1]['Close']
    print('greedy result')
    print(f'original hold: 1000000')
    print(f'final hold of cash: ${hold}', )
    print(f'final hold of bitcoin: {sharehold}, which equals to {sharehold*latest_price} usd dollars')
    print(f'total: ${hold+sharehold*latest_price}')


def backtest(res, threshold, command):
    hold = 1000000
    sharehold = 0
    percentage = threshold

    for i, data in res.iterrows():
        label = data['pred']
        buy_price = data['Low']
        sell_price = data['High']
        price = data['Close']
        if command == 2:
            if label == 1:
                percentage = data['buy']*0.5
            elif label == 2:
                percentage = data['sell']*0.5
        # print(label, price)
        if label == 1 and hold >= buy_price:
            if hold*percentage < buy_price:
                hold -= buy_price
                sharehold += 1
            else:
                to_buy = hold*percentage
                hold *= (1-percentage)
                sharehold += to_buy/buy_price
                
        elif label == 2 and sharehold >= 1/(percentage*2):
            to_sell = sharehold*percentage
            sharehold -= to_sell
            hold += to_sell * sell_price


    latest_price = res.iloc[-1]['Close']
    if command == 0:
        print('final result using entropy as threshold:')
    elif command == 1:
        print('final result using output as threshold:')
    else:
        print('final result using percentage as threshold:')
    print(f'original hold: 1000000')
    print(f'final hold of cash: ${hold}')
    print(f'final hold of bitcoin: {sharehold}, which equals to {sharehold*latest_price} usd dollars')
    print(f'total: ${hold+sharehold*latest_price}')

    return (hold+sharehold*latest_price)


if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("input format: python backtest.py train.csv test.csv btc.csv")

    all_res = []
    max_val = 0
    pos = 0

    for command in range(3):
        if len(sys.argv) == 4:
            file1 = sys.argv[1]
            file2 = sys.argv[2]
            btc_file = sys.argv[3]
            flag = True
            if '1hr' in btc_file:
                flag = False 

            pred = pd.read_csv(file1)
            pred2 = pd.read_csv(file2)
            pred = pd.concat([pred, pred2], ignore_index=True, sort=False)
            btc = pd.read_csv(btc_file)

            res = combine(pred, btc, flag, command)

        else:
            file = sys.argv[1]
            btc_file = sys.argv[2]
            flag = True
            if '1hr' in btc_file:
                flag = False 

            pred = pd.read_csv(file)
            btc = pd.read_csv(btc_file)

            res = combine(pred, btc, flag, command)

        

        # greedy_res = greedy(res)
        profit = backtest(res, 1, command)
        if profit > max_val:
            max_val = profit
            pos = command
        print("\n")
        all_res.append(res)

    all_res[1].to_csv('./data/combine.csv')
