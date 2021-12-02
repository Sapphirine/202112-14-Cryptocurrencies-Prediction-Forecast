from pandas_datareader import data as pdr
import yfinance as yf
from sklearn.linear_model import LinearRegression
import pickle
from os.path import exists
import pandas as pd
from datetime import datetime, timedelta, date
from textwrap import dedent
import time
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
yf.pdr_override() 

Features = ["Open", "Low", "Close", "Volume"]
PredictFeature = ["High"]

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
def getDate():
    return date.today().strftime("%Y/%m/%d")

def updateModel(stock):
    modelPath = stock + '.ml'
    # read most recent record
    df_stockRecentRecord = yf.download(stock, period='10d')
    model = LinearRegression()
    x, y = df_stockRecentRecord[Features].to_numpy(), df_stockRecentRecord[PredictFeature].to_numpy()
    model.fit(x, y)
    pickle.dump(model, open(modelPath, 'wb'))

def predict(**kwargs):
    stock = kwargs['stock']
    modelPath = stock + '.ml'
    errorPath = stock + '.err'
    model_exists = exists(modelPath)
    error_exists = exists(errorPath)
    model = df_error = None
    # check model or error file existence
    if model_exists:
        model = pickle.load(open(modelPath, 'rb'))
    if error_exists:
        df_error = pd.read_csv(errorPath, index_col=0)
    # get the most recent data
    df_stockRecentRecord = yf.download(stock, period='10d')
    # update error
    if model is None or df_error is None:
        df_error = pd.DataFrame(columns = ["error"])
        df_error.loc[getDate()] = 0
    else:
        x = df_stockRecentRecord.tail(1)[Features].to_numpy()
        y = model.predict(x)[0][0]
        high_today = df_stockRecentRecord.iloc[-1, :]['High']
        relative_error = (y - high_today) / high_today
        df_error.loc[getDate()] = relative_error
    df_error.to_csv(errorPath)

# DAC show as ID in airflow
with DAG(
    'stock',
    default_args=default_args,
    description='Build stock workflow',
    schedule_interval="0 7 * * *",
    start_date=datetime(2021, 11, 24),
    catchup=False,
    tags=['stock'],
) as dag:
    
    t11 = PythonOperator(
        task_id='t11',
        python_callable=predict,
        op_kwargs={'stock': 'AAPL'}
    )
    t12 = PythonOperator(
        task_id='t12',
        python_callable=updateModel,
        op_kwargs={'stock': 'AAPL'}
    )
    t21 = PythonOperator(
        task_id='t21',
        python_callable=predict,
        op_kwargs={'stock': 'GOOGL'}
    )
    t22 = PythonOperator(
        task_id='t22',
        python_callable=updateModel,
        op_kwargs={'stock': 'GOOGL'}
    )
    t31 = PythonOperator(
        task_id='t31',
        python_callable=predict,
        op_kwargs={'stock': 'FB'}
    )
    t32 = PythonOperator(
        task_id='t32',
        python_callable=updateModel,
        op_kwargs={'stock': 'FB'}
    )
    t41 = PythonOperator(
        task_id='t41',
        python_callable=predict,
        op_kwargs={'stock': 'MSET'}
    )
    t42 = PythonOperator(
        task_id='t42',
        python_callable=updateModel,
        op_kwargs={'stock': 'MSET'}
    )
    t51 = PythonOperator(
        task_id='t51',
        python_callable=predict,
        op_kwargs={'stock': 'AMZN'}
    )
    t52 = PythonOperator(
        task_id='t52',
        python_callable=updateModel,
        op_kwargs={'stock': 'AMZN'}
    )
t11 >> t12
t21 >> t22
t31 >> t32
t41 >> t42
t51 >> t52
    