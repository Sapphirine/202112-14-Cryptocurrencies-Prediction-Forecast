import time
import requests as req
from datetime import datetime
import pandas as pd
from pytrends.request import TrendReq


def fetch():
    # setup environment

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    today = datetime.today().strftime('%Y%m%d')
    url = f'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/Bitcoin/daily/20140917/{today}'
    wiki = req.get(url, headers=headers).json()


    test = (wiki['items'][0]['timestamp'])
    test = test[:-2]
    test = test[:4] + '-' + test[4:]
    test = test[:7] + '-' + test[7:]
    now = time.mktime(datetime.strptime('2015-07-01', "%Y-%m-%d").timetuple())
    now = int(now)

    all_date = []
    timestamp = []
    view = []
    for data in wiki['items']:
        date = data['timestamp']
        date = date[:-2]
        date = date[:4] + '-' + date[4:]
        date = date[:7] + '-' + date[7:]
        # print(date)
        now = time.mktime(datetime.strptime(date, "%Y-%m-%d").timetuple())
        now = int(now)
        all_date.append(date)
        timestamp.append(now)
        view.append(data['views'])
        
    all_wiki = pd.DataFrame(
        {'view': view,
         'time': all_date,
         'timestamp': timestamp
        }
    )

    all_wiki.to_csv(r'/home/savik/Cryptocurrencies-Prediction-Forecast/MLDL/data/wiki.csv', index = None, header=True)


    pytrend = TrendReq()
    # trend = pytrend.get_historical_interest(['Bitcoin'], year_start=2014, month_start=9, day_start=17, hour_start=0, year_end=int(today[:4]), month_end=int(today[4:6]), day_end=int(today[6:]), hour_end=0, cat=0, geo='', gprop='', sleep=60)
    trend = pytrend.get_historical_interest(['Bitcoin'], year_start=2021, month_start=9, day_start=17, hour_start=0, year_end=int(today[:4]), month_end=int(today[4:6]), day_end=int(today[6:]), hour_end=0, cat=0, geo='', gprop='', sleep=5)
    temp = trend.index.tolist()
    trend['datetime'] = temp
    trend['timestamp'] = trend['datetime'].apply( lambda x: int(x.value/10**9) )
    trend.to_csv (r'/home/savik/Cryptocurrencies-Prediction-Forecast/MLDL/data/trend.csv', index = None, header=True) 


if __name__ == '__main__':
    fetch()
