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
from gevent.pywsgi import WSGIServer


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

@app.route('/send')
def send_alert():
    def update():
        r = RethinkDB()
        conn = r.connect(host=host_rtk, port=port_rtk)
        conn.repl()
        for change in r.db(db).table(table_whaler_alert).changes().run(conn):
            if change["new_val"] and not change["old_val"]:
                data = change["new_val"]
                dt = int(data["timestamp"])
                dt = datetime.fromtimestamp(dt).strftime("%Y-%m-%d %H:%M:%S")
                source = data['source'] if len(data['source']) > 0 else 'unknown'
                dest = data['dest'] if len(data['dest']) > 0 else 'unknown'
                text = f"{dt} {data['price']} {data['symbol']} ({data['usd']} USD) from {source} to {dest}"
                yield text
                sse.publish({"text": text}, type='whaleAlert')
                
    return Response(update(), mimetype='text/event-stream')
                


if __name__ == "__main__":
    
    http_server = WSGIServer(("localhost", 8222), app)
    http_server.serve_forever()

    '''
    import click
    
    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8222, type=int)
    def run(debug, threaded, host, port):
        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    print("thred")
    #FlaskThread(target=send_alert).start()
    print("run")
    run()
    '''