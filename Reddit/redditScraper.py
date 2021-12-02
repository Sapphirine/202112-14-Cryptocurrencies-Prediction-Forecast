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
import time
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

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



def fetch():
    # setup environment
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './Reddit/config/gcp_key.json'
    # get Reddit token
    response = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
    if response.status_code != 200:
        return
    TOKEN = response.json()['access_token']
    headers['Authorization'] = f'bearer {TOKEN}'
    sia = SentimentIntensityAnalyzer()
    payload = {'q': 'bitcoin', 'limit': 100, 'sort': 'relevance', 't':'hour'}
    # start scraping
    df = pd.DataFrame(columns = columns_name)
    df = df.set_index('id')
    response = requests.get('https://oauth.reddit.com/r/subreddits/search', headers=headers, params=payload)
    # requests.get('https://oauth.reddit.com/r/{}/search'.format(subreddit), headers=headers, params=payload)
    # check connection and service
    if response.status_code != 200:
        return
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

    
# DAC show as ID in airflow
with DAG(
    'reddit',
    default_args=default_args,
    description='reddit workflow',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2021, 11, 30),
    catchup=False,
    tags=['reddit'],
) as dag:
    t11 = PythonOperator(
    task_id='t11',
    python_callable=fetch
    )