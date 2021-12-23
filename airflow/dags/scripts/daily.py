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
    'daily',
    default_args=default_args,
    description='btc daily model trainer',
    #schedule_interval="0 0 * * 1,2,3,4,5",
    schedule_interval="0 0 * * *",
    start_date=timezone.datetime(2021, 11, 30, 0, 0, tzinfo=local_tz),
    catchup=False,
    tags=['coms6895'],
) as dag:

    t1 = BashOperator(
        task_id='btc_crawler_day',
        bash_command="cd /home/savik/Cryptocurrencies-Prediction-Forecast/Crawlers; python btc.py -f day ",
        retries=3,
    )

    t2 = BashOperator(
        task_id='btc_crawler_hour',
        bash_command="cd /home/savik/Cryptocurrencies-Prediction-Forecast/Crawlers; python btc.py -f 1hour ",
        retries=3,
    )

    t3 = BashOperator(
        task_id='wiki_trend_crawler',
        bash_command="cd /home/savik/airflow/dags/scripts; python wiki_trend_day.py ",
        retries=3,
    )

    t4 = BashOperator(
        task_id='train_and_predict_day',
        bash_command="cd /home/savik/Cryptocurrencies-Prediction-Forecast/Crawlers; python main.py -f day -d btc_trend_wiki",
        retries=3,
    )

    t5 = BashOperator(
        task_id='train_and_predict_hour',
        bash_command="cd /home/savik/Cryptocurrencies-Prediction-Forecast/Crawlers; python main.py -f 1hour -d btc_trend",
        retries=3,
    )

    [t1, t2, t3] >> t4 >> t5
