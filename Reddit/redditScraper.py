from google.cloud import storage
from google.cloud import bigquery
import os
import requests
import pandas as pd
from datetime import datetime
import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
import subprocess
import time

STREAMTIME = 3600
projectId = 'e6893-hw0'
CLIENT_ID = '-fxi7oqz2MXx7O4VQxC2aw'
SECRET_KEY = 'hXNaWiX79YtU3kFh_l0OKiSTpSVpFA'
auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)
data = {'grant_type':'password',
        'username': 'tim-kao',
        'password':'$4DLtRP9ejS/B$H'}
headers = {'User-Agent': 'MyAPI/0.1'}
columns_name = ['id', 'time', 'title', 'author', 'neg', 'neu', 'pos', 'compound', 'length', 'text']
minAnalysisLen = 10
keywords = ['btc', 'bitcoin']
listing = 'random' # new, hot, best

def uploadToStorage(df, fileName):
    client = storage.Client()
    bucket = client.get_bucket("crypto-team14")
    bucket.blob('reddit/' + fileName).upload_from_string(df.to_csv(), 'text/csv')
    
def uploadToBigQuery(fileName):
    subprocess.check_call(
        'bq load --autodetect=true --allow_quoted_newlines=true '
        '--project_id=e6893-hw0 --format=csv '
        '{dataset}.{table} {files}'.format(
            dataset='crypto', table='reddit', files='gs://crypto-team14/reddit/' + fileName    
        ).split())

def get_timestamp(date_time_instance):
    return int(datetime.datetime.timestamp(date_time_instance))

if __name__ == '__main__':
    # setup environment
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './Reddit/config/gcp_key.json'
    # get Reddit token
    response = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
    if response.status_code != 200:
        exit
    TOKEN = response.json()['access_token']
    headers['Authorization'] = f'bearer {TOKEN}'
    sia = SentimentIntensityAnalyzer()
    payload = {'q': 'bitcoin', 'limit': 100, 'sort': 'relevance', 't':'hour'}
    # start scraping
    while True:
        df = pd.DataFrame(columns = columns_name)
        df = df.set_index('id')
        response = requests.get('https://oauth.reddit.com/r/subreddits/search', headers=headers, params=payload)
        # requests.get('https://oauth.reddit.com/r/{}/search'.format(subreddit), headers=headers, params=payload)
        # check connection and service
        if response.status_code != 200:
            break
        posts = response.json()['data']['children']
        for post in posts:
            postData = post['data']
            text = postData['selftext']
            if len(text) < minAnalysisLen or all(keyword not in text.lower() for keyword in keywords):
                continue
            sentimentResult = sia.polarity_scores(text)
            row = [datetime.utcfromtimestamp(int(postData['created_utc'])).strftime('%Y-%m-%d %H:%M:%S'),\
                    postData['title'], postData['author_fullname'], sentimentResult['neg'],sentimentResult['neu'],\
                    sentimentResult['pos'], sentimentResult['compound'], len(text), text]
            df.loc[postData['id']] = row
        print('number of rows: {}'.format(len(df.index)))
        fileName = 'reddit-' + str(int(datetime.timestamp(datetime.utcnow()))) + '.csv'
        uploadToStorage(df, fileName)
        print("scraping is done...now uploading to bigquery")
        uploadToBigQuery(fileName)
        print("finish commitment to bigquery. Time: " + str(datetime.utcnow()) + '. File: ' + fileName)
        time.sleep(STREAMTIME)
    