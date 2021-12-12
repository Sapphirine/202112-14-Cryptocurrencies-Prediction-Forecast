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
import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer

# tweets criteria
minAnalysisLen = 10
cryptoType = ['#btc', '#bitcoin']     #the words you should filter and do word count

# global variables
bucket = "crypto-team14"
output_directory = 'gs://{}/tweet/sentiment'.format(bucket)
# output table and columns name
output_dataset = 'crypto'                     #the name of your dataset in BigQuery
output_table = cryptoType[0][1:]
#columns_name = ['time', 'score', 'magnitude']
columns_name = ['time', 'neg', 'neu', 'pos', 'compound', 'length', 'text']
# parameter
IP = 'localhost'    # ip port
PORT = 9001       # port

STREAMTIME = 3600 * 24 * 2      # time that the streaming process runs

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
        '{dataset}.{table} {files}'.format(
            dataset=output_dataset, table=output_table, files=files
        ).split())
    output_path = sc._jvm.org.apache.hadoop.fs.Path(directory)
    output_path.getFileSystem(sc._jsc.hadoopConfiguration()).delete(
        output_path, True)

def wordCount(words):

    winSize = 60
    # Reduce last 60 seconds of data, every 60 seconds
    wordCountPerWin = words.filter(lambda word: word.lower() in targetWORD).map(lambda word: (word.lower(), 1))\
                            .reduceByKeyAndWindow(lambda x, y: x + y, lambda x, y: x - y, winSize, winSize)
    wordCountResult = wordCountPerWin.transform(lambda time, data: data.map(lambda d: (d[0], d[1], time.strftime("%Y-%m-%d %H:%M:%S"))))
    return wordCountResult

def analyze_text_sentiment(text):
    client = language.LanguageServiceClient()
    document = language.Document(content=text, type_=language.Document.Type.PLAIN_TEXT)

    response = client.analyze_sentiment(document=document)

    return (time.strftime("%Y-%m-%d %H:%M:%S"), 0.4, 0.3)

def nltk_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    result = sia.polarity_scores(text)
    return [time.strftime("%Y-%m-%d %H:%M:%S"), result['neg'], result['neu'], result['pos'], result['compound'], len(text), text]

if __name__ == '__main__':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
            '/home/sk4920/e6893-hw0-e5d0369749d2.json'
    
    conf = SparkConf()
    conf.setMaster('local[2]')
    conf.setAppName("TwitterStreamApp")
    # output_directory += '/' + str(time.time()).split('.')[0]
    print(output_directory)
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

    tweets = dataStream.flatMap(lambda line: line.split("\r\n"))\
            .filter(lambda tweet: len(tweet.split(' ')) >= minAnalysisLen and \
                                  any(crypto in tweet.lower().split(' ') for crypto in cryptoType))
    tweets.pprint()
    sentimentResults = tweets.map(nltk_sentiment)
    sentimentResults.pprint()
    
    sentimentResults.foreachRDD(lambda d: saveToStorage(d, output_directory, columns_name, mode="append"))
    # start streaming process, wait for 600s and then stop.
    ssc.start()
    time.sleep(STREAMTIME)
    ssc.stop(stopSparkContext=False, stopGraceFully=True)

    # put the temp result in google storage to google BigQuery
    saveToBigQuery(sc, output_dataset, output_table, output_directory)