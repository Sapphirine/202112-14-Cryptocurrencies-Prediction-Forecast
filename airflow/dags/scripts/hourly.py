from datetime import datetime, timedelta
from textwrap import dedent
import time
import pendulum

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
#from airflow.operators.python import PythonOperator
from airflow.utils import timezone



local_tz = pendulum.timezone('US/Eastern')
today = timezone.utcnow().replace(tzinfo=local_tz)
today = today.strftime("%Y-%m-%d")


default_args = {
    'owner': 'Ho',
    'depends_on_past': False,
    'email': ['ch3561@columbia.edu'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
}


with DAG(
    'hourly',
    default_args=default_args,
    description='btc hourly model trainer',
    #schedule_interval="0 0 * * 1,2,3,4,5",
    schedule_interval=timedelta(hours=1),
    start_date=timezone.datetime(2021, 11, 30, 0, 0, tzinfo=local_tz),
    catchup=False,
    tags=['coms6895'],
) as dag:

    t1 = BashOperator(
        task_id='reddit_crawler',
        bash_command="cd /home/savik/airflow/dags/scripts; python reddit.py ",
        retries=3,
    )

    t2 = BashOperator(
        task_id='reddit_news_crawler',
        bash_command="cd /home/savik/airflow/dags/scripts; python reddit_news.py ",
        retries=3,
    )

    t3 = BashOperator(
        task_id='twitter_crawler',
        bash_command="cd /home/savik/Cryptocurrencies-Prediction-Forecast/streaming; python sparkStreaming.py ",
        retries=3,
    )

    [t1, t2]
