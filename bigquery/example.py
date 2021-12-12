import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './config/gcp_key.json'
import pandas_gbq


def query():
    try:
        # Perform a query.
        QUERY = 'SELECT * FROM crypto.btc LIMIT 1000;'
        rows = pandas_gbq.read_gbq(query=QUERY, project_id='e6893-hw0').values.tolist()
        # rows is a list of liist
        for row in rows:
            print(row)
        
    except Exception as e:
        print(e)

if __name__ == '__main__':
    query()
