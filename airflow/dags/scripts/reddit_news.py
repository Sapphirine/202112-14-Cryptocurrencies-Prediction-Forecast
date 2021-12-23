from google.cloud import storage
from google.cloud import bigquery
import os
import requests
import pandas as pd
from datetime import datetime, timedelta, date
import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
import subprocess
import random
# The DAG object; we'll need this to instantiate a DAG

# Operators; we need this to operate!


default_args = {
    'owner': 'tim',
    'depends_on_past': False,
    'email': ['sk4920@columbia.edu'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

subreddits = ['Trading', 'Daytrading', 'Forex', 'EliteTraders', 'finance', 'GlobalOffensiveTrade',
                  'stocks', 'StockMarket', 'algotrading', 'trading212', 'stock', 'invest', 'investing',
                  'wallstreetbets', 'personalfinance', 'cryptocurrency', 'financialindependence', 'retirement',
                   'povertyfinance', 'Bogleheads', 'PFtools', 'FinancialPlanning', 'Budget', 'fatFIRE',
                   'realestateinvesting', 'MiddleClassFinance', 'passive_income',
                    'AlgoTrading', 'PennyStocks', 'Options', 'CanadianInvestor', 'algorithmictrading',
                  'ausstocks', 'dividends', 'InvestmentClub', 'quantfinance', 'quant', 'Stock_Picks',
                  'SecurityAnalysis', 'UKInvesting', 'weedstocks']

STREAMTIME = 3600
projectId = 'e6893-hw0'
data = {'grant_type':'password',
        'username': 'tim-kao',
        'password':'$4DLtRP9ejS/B$H'}
headers = {'User-Agent': 'MyAPI/0.1'}
columns_name = ['id', 'time', 'title', 'author', 'neg', 'neu', 'pos', 'compound', 'length', 'text']
minAnalysisLen = 10
keywords = ['btc', 'bitcoin']
listing = 'random' # new, hot, best


def fetch():
    # setup environment
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/savik/airflow/dags/Reddit/config/gcp_key.json'
    # get Reddit token
    response = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
    if response.status_code != 200:
        return
    TOKEN = response.json()['access_token']
    headers['Authorization'] = f'bearer {TOKEN}'
    sia = SentimentIntensityAnalyzer()
    payload = {'q': 'bitcoin', 'limit': 100}
    # start scraping
    for subreddit in subreddits:
        df = pd.DataFrame(columns = columns_name)
        df = df.set_index('id')
        response = requests.get('https://oauth.reddit.com/r/{}/new'.format(subreddit), headers=headers, params=payload)
        # requests.get('https://oauth.reddit.com/r/{}/search'.format(subreddit), headers=headers, params=payload)
        # check connection and service
        if response.status_code != 200:
            continue
        posts = response.json()['data']['children']
        for post in posts:
            if 'data' not in post:
                continue
            postData = post['data']
            if 'selftext' not in postData or 'id' not in postData or 'author_fullname' not in postData:
                continue
            text = postData['selftext']
            if len(text) < minAnalysisLen or all(keyword not in text.lower() for keyword in keywords):
                continue
            sentimentResult = sia.polarity_scores(text)
            df.loc[postData['id']] = [datetime.utcfromtimestamp(postData['created_utc']).strftime('%Y-%m-%d %H:%M:%S'),\
                    postData['title'], postData['author_fullname'], sentimentResult['neg'],sentimentResult['neu'],\
                    sentimentResult['pos'], sentimentResult['compound'], len(text), 'text']
            
        print('number of rows: {}'.format(len(df.index)))
        if df.shape[0] == 0 or df.shape[1] != 9:
            continue
        print(df)
        fileName = 'reddit-' + str(int(datetime.timestamp(datetime.utcnow()))) + str(random.randint(0, 100)) + '.csv'
        print(df.shape)
        uploadToStorage(df, fileName, "reddit")
        print("scraping is done...now uploading to bigquery")
        uploadToBigQuery(fileName, "reddit", "reddit", "crypto")
        print("finish commitment to bigquery. Time: " + str(datetime.utcnow()) + '. File: ' + fileName)


if __name__ == '__main__':
    from settings import REDDIT_CLIENT_ID, REDDIT_SECRET_KEY
    from utils import *
    auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_SECRET_KEY)
    fetch()
