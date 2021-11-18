#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Columbia EECS E6893 Big Data Analytics
"""
This module is the spark streaming analysis process.

"""

from pyspark import SparkConf,SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SQLContext
from google.cloud import language
from importlib import reload
import sys
import requests
import time
import subprocess
import re
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
            'gs://hw2-e6893/e6893-hw0-c8eb72b6d91a.json'

# global variables
bucket = "hw2-e6893"
output_directory = 'gs://{}/hadoop/tmp/bigquery/pyspark_output/sentiment'.format(bucket)
# output table and columns name
output_dataset = 'crypto'                     #the name of your dataset in BigQuery
output_table = 'eth'
columns_name = ['time', 'text', 'score', 'magnitude']

# parameter
IP = 'localhost'    # ip port
PORT = 9001       # port

STREAMTIME = 600          # time that the streaming process runs

targetWORD = ['#eth', '#cryptocurrency']     #the words you should filter and do word count


def analyze_text_sentiment(text):
    client = language.LanguageServiceClient()
    document = language.Document(content=text, type_=language.Document.Type.PLAIN_TEXT)

    response = client.analyze_sentiment(document=document)

    sentiment = response.document_sentiment
    results = dict(
        text=text,
        score=f"{sentiment.score:.1%}",
        magnitude=f"{sentiment.magnitude:.1%}",
    )
    for k, v in results.items():
        print(f"{k:10}: {v}")
    return (time.strftime("%Y-%m-%d %H:%M:%S"), results['text'], results['score'], results['magnitude'])
        
# Helper functions
def saveToStorage(rdd, output_directory, columns_name, mode):
    """
    Save each RDD in this DStream to google storage
    Args:
        rdd: input rdd
        output_directory: output directory in google storage
        columns_name: columns name of dataframe
        mode: mode = "overwirte", overwirte the file
              mode = "append", append data to the end of file
    """
    if not rdd.isEmpty():
        (rdd.toDF( columns_name ) \
        .write.save(output_directory, format="json", mode=mode))


def saveToBigQuery(sc, output_dataset, output_table, directory):
    """
    Put temp streaming json files in google storage to google BigQuery
    and clean the output files in google storage
    """
    files = directory + '/part-*'
    subprocess.check_call(
        'bq load --source_format NEWLINE_DELIMITED_JSON '
        '--replace '
        '--autodetect '
        '{dataset}.{table} {files}'.format(
            dataset=output_dataset, table=output_table, files=files
        ).split())
    output_path = sc._jvm.org.apache.hadoop.fs.Path(directory)
    output_path.getFileSystem(sc._jsc.hadoopConfiguration()).delete(
        output_path, True)



def wordCount(words):
    """
    Calculte the count of 5 sepcial words for every 60 seconds (window no overlap)
    You can choose your own words.
    Your should:
    1. filter the words
    2. count the word during a special window size
    3. add a time related mark to the output of each window, ex: a datetime type
    Hints:
        You can take a look at reduceByKeyAndWindow transformation
        Dstream is a serious of rdd, each RDD in a DStream contains data from a certain interval
        You may want to take a look of transform transformation of DStream when trying to add a time
    Args:
        dstream(DStream): stream of real time tweets
    Returns:
        DStream Object with inner structure (word, (count, time))
    """
    winSize = 60
    # Reduce last 60 seconds of data, every 60 seconds
    wordCountPerWin = words.filter(lambda word: word.lower() in targetWORD).map(lambda word: (word.lower(), 1))\
                            .reduceByKeyAndWindow(lambda x, y: x + y, lambda x, y: x - y, winSize, winSize)
    wordCountResult = wordCountPerWin.transform(lambda time, data: data.map(lambda d: (d[0], d[1], time.strftime("%Y-%m-%d %H:%M:%S"))))
    return wordCountResult


if __name__ == '__main__':
    reload(sys)
    # sys.setdefaultencoding('utf8')
    # Spark settings
    conf = SparkConf()
    conf.setMaster('local[2]')
    conf.setAppName("TwitterStreamApp")

    # create spark context with the above configuration
    #sc = SparkContext(conf=conf)
    sc = SparkContext.getOrCreate(conf=conf)
    sc.setLogLevel("ERROR")

    # create sql context, used for saving rdd
    sql_context = SQLContext(sc)

    # create the Streaming Context from the above spark context with batch interval size 5 seconds
    ssc = StreamingContext(sc, 5)
    # setting a checkpoint to allow RDD recovery
    ssc.checkpoint("~/checkpoint_TwitterApp")

    # read data from port 9001
    dataStream = ssc.socketTextStream(IP, PORT)
    # dataStream.pprint()

    tweets = dataStream.flatMap(lambda line: line.split("\r\n"))
    tweets.pprint()
    sentimentResults = tweets.map(lambda tweet: analyze_text_sentiment(tweet))
    
    sentimentResults.foreachRDD(lambda d: saveToStorage(d, output_directory, columns_name, mode="append"))
    # start streaming process, wait for 600s and then stop.
    ssc.start()
    time.sleep(STREAMTIME)
    ssc.stop(stopSparkContext=False, stopGraceFully=True)

    # put the temp result in google storage to google BigQuery
    saveToBigQuery(sc, output_dataset, output_table, output_directory)