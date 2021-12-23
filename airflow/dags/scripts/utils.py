import subprocess
from google.cloud import storage
from google.cloud import bigquery


def uploadToStorage(df, fileName, dirName):
    client = storage.Client()
    bucket = client.get_bucket("crypto-team14")
    bucket.blob(f'{dirName}/{fileName}').upload_from_string(df.to_csv(), 'text/csv')


def uploadToBigQuery(fileName, dirName, table, dataset):
    subprocess.check_call(
        'bq load --autodetect=true --allow_quoted_newlines=true '
        '--project_id=e6893-hw0 --format=csv '
        f'{dataset}.{table} gs://crypto-team14/{dirName}/{fileName}'.split()
    )


def get_timestamp(date_time_instance):
    return int(datetime.datetime.timestamp(date_time_instance))
