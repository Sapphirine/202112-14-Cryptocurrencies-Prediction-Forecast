#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from flask import Flask, request, render_template, g, redirect, Response, json
from flask_sse import sse
from collections import defaultdict
from threading import Thread
from time import sleep
from rethinkdb import RethinkDB
from threading import Thread
from datetime import datetime
from settings import *
import requests as req
import pandas as pd
import json
from google.cloud import pubsub_v1

whaleAlertUrl = "https://api.whale-alert.io/feed.csv"
whaleAlertCols = ["id", "timestamp", "symbol", "price", "usd", "action", "source", "dest"]
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'statics')
app = Flask(__name__, template_folder=tmpl_dir, static_folder=static_dir, static_url_path='')
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')
refreshRate = 60
credentials_path = './pubsub/credential/myFile.privateKey.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
publisher = pubsub_v1.PublisherClient()
topicWhaleAlert = 'projects/e6893-hw0/topics/whaleAlert'
alertThreshold = 1000


class FlaskThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

    def run(self):
        with self.app.app_context():
            super().run()


@app.route('/')
def index():
    #context = dict(data = data)
    context = {}
    return render_template("index.html", **context)


@app.route('/getWhale')
def getWhale():
    #context = dict(data = data)
    context = {}
    return render_template("whale.html", **context)


@app.route('/getPredict')
def getPredict():
    #context = dict(data = data)
    context = {}
    return render_template("predict.html", **context)


def fetch():
    res = req.get(whaleAlertUrl)
    recs = [rec.split(",") for rec in res.text.split("\n")]
    df = pd.DataFrame(recs)
    df = df.drop([7, 9], axis=1)
    df.columns = whaleAlertCols
    df.price = df.price.astype(float)
    df.usd = df.usd.astype(float)
    df_filtered = df[df['symbol'] == 'btc']
    if df_filtered.shape[0] == 0:
         return None
    return json.loads(df_filtered.to_json(orient="records"))


@app.route("/whaleProducer")
def whaleProducer():
  def respond_to_client():
    while True:
        rows = fetch()
        if rows:
            message = ""
            for row in rows:
                yield f"id: 1\ndata: {json.dumps(row)}\nevent: whale\n\n"
                # when the whale hits the threshold, publish the events
                if row['price'] >= alertThreshold:
                    date = datetime.fromtimestamp(int(row['timestamp']))
                    message += date.strftime("%m/%d/%Y %H:%M:%S")
                    message += ", price: {}".format(row['price'])
                    message += ", action: {}".format(row['action'])
                    message += ", source: {}".format(row['source'])
                    message += ", dest: {}".format(row['dest']) + "\n"
            if message:
                data = message.encode('utf-8')
                future = publisher.publish(topicWhaleAlert, data)
                print(f'published message id {future.result()}')
            sleep(refreshRate)
  return Response(respond_to_client(), mimetype='text/event-stream')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8222, debug=True)