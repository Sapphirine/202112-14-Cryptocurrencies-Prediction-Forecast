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

whaleAlertUrl = "https://api.whale-alert.io/feed.csv"
whaleAlertCols = ["id", "timestamp", "symbol", "price", "usd", "action", "source", "dest"]
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'statics')
app = Flask(__name__, template_folder=tmpl_dir, static_folder=static_dir, static_url_path='')
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')


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

#@app.route('/send')
#def send():
#    #{'action': 'transfer', 'dest': 'binance', 'id': '1744010719', 'price': '119.09', 'source': 'binance', 'symbol': 'btc', 'timestamp': '1637271425', 'usd': '6889170'}
#    sse.publish({"text": "Hello!"}, type='whaleAlert')
#    return "Message sent!"

def fetch():
    res = req.get(whaleAlertUrl)
    recs = [rec.split(",") for rec in res.text.split("\n")]
    df = pd.DataFrame(recs)
    df = df.drop([7, 9], axis=1)
    df.columns = whaleAlertCols
    df.price = df.price.astype(float)
    df.usd = df.usd.astype(float)
    print(df)
    df_filtered = df[df['symbol'] == 'eth']
    if df_filtered.shape[0] == 0:
        return None
    return json.loads(df_filtered.to_json(orient="records"))


@app.route("/whaleProducer")
def whaleProducer():
  def respond_to_client():
    while True:
        rows = fetch()
        if rows:
            for row in rows:
                print(type(row), row)
                yield f"id: 1\ndata: {json.dumps(row)}\nevent: whale\n\n"
            sleep(30)
  return Response(respond_to_client(), mimetype='text/event-stream')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8222, debug=True)