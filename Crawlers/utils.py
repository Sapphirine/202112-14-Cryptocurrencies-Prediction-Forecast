import pandas as pd
import re
import json
import abc
from pathlib import Path
from glob import glob
import asyncio
from multiprocessing import Pool
import time
import numpy as np
from datetime import datetime, timedelta
from datetime import date as date_util
from dateutil import parser as date_parser
from rethinkdb import RethinkDB
import configparser
from binance.client import Client

today = date_util.today().strftime("%Y-%m-%d")
db_binance = "Binance"
table_binance_tick = "Tick"
config = configparser.ConfigParser()
config.read("cred.config")
binance_key = config["binance"]["key"]
binance_secret = config["binance"]["key"]


def _clean_year(dt) -> str:
    year = ""
    for c in str(dt)[:4]:
        try:
            int(c)
        except ValueError:
            continue
        year += c
    return int(year)


def _clean_date(dt, paste="-", form="en") -> str:
    md = []
    chars = ""
    for c in str(dt)[::-1]:
        try:
            int(c)
        except ValueError:
            if len(chars) > 0: md.append("%02d"%int(chars[::-1]))
            chars = ""
            continue
        chars += c
        if len(chars) == 2 and len(md) < 2:
            md.append("%02d"%int(chars[::-1]))
            chars = ""
    md.append(chars[::-1])
    if form == "en":
        if len(md[2]) == 4:
            return f"{md[2]}{paste}{md[1]}{paste}{md[0]}"
        elif len(md[2]) < 4:
            return f"{int(md[2])+1911}{paste}{md[1]}{paste}{md[0]}"
    elif form == "zh":
        if len(md[2]) == 4:
            return f"{int(md[2])-1911}{paste}{md[1]}{paste}{md[0]}"
        elif len(md[2]) < 4:
            return f"{md[2]}{paste}{md[1]}{paste}{md[0]}"


def is_null_int_val(val) -> bool:
    return val is None or len(str(val)) == 0\
            or val in ["None", "-", "--", "---", "----", "N/A"]\
            or np.isnan(float(val))


def is_null_str_val(val) -> bool:
    return val is None or val in ["None", "-", "N/A"]\
            or len(str(val).strip()) == 0\
            or (not isinstance(val, str) and np.isnan(val))


def clean_float(val):
    val = re.sub(",", "", str(val))
    if "%" in val:
        val = float(re.sub("%", "", str(val)))
        val /= 100.
        return val
    try:
        if is_null_int_val(val): return
    except ValueError:
        return
    return float(val)


def clean_int(val):
    val = re.sub(",", "", str(val))
    try:
        if is_null_int_val(val): return
    except ValueError:
        return
    return int(float(val))


def clean_str(val):
    if is_null_str_val(val): return
    return str(val).strip().lower()


def clean_year(val):
    if is_null_str_val(val): return
    val = _clean_year(val)
    return int(val)


def clean_date(val, paste="-", form="en"):
    if is_null_str_val(val): return
    val = str(val)
    if len(val) < 3: return val
    val = _clean_date(val, paste=paste, form=form)
    return val


class ETL(metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.data = None
        self.int_cols = []
        self.float_cols = []
        self.date_cols = []
        self.str_cols = []

    def dump_csv(self, dump_dir, filename, data=None, index=False):
        self.dump_dir = dump_dir
        Path(self.dump_dir).mkdir(parents=True, exist_ok=True)
        if data is not None:
            data.to_csv(f"{self.dump_dir}/{filename}.csv", index=index)
        else:
            self.data.to_csv(f"{self.dump_dir}/{filename}.csv", index=index)
        print(f"{self.dump_dir}/{filename}.csv dumped")

    def dump_json(self, dump_dir, filename, data=None, orient="records"):
        self.dump_dir = dump_dir
        Path(self.dump_dir).mkdir(parents=True, exist_ok=True)
        if data is not None:
            data.to_json(f"{self.dump_dir}/{filename}.json", orient=orient)
        else:
            self.data.to_json(f"{self.dump_dir}/{filename}.json", orient=orient)
        print(f"{self.dump_dir}/{filename}.json dumped")

    @abc.abstractmethod
    def get_data(self):
        return NotImplemented

    @abc.abstractmethod
    def unify_cols(self):
        return NotImplemented

    @abc.abstractmethod
    def gen_id(self):
        return NotImplemented

    @abc.abstractmethod
    def map_vals(self, x):
        return NotImplemented

    def do_map_vals(self):
        if isinstance(self.data, pd.DataFrame) or isinstance(self.data, pd.Series):
            self.do_map_vals_pd()
        elif isinstance(self.data, list):
            self.do_map_vals_records()

    def do_map_vals_records(self):
        for col in self.date_cols:
            for d in self.data:
                if col in d: d[col] = clean_date(d[col])
        for col in self.str_cols:
            for d in self.data:
                if col in d: d[col] = clean_str(d[col])
        for col in self.int_cols:
            for d in self.data:
                if col in d: d[col] = clean_int(d[col])
        for col in self.float_cols:
            for d in self.data:
                if col in d: d[col] = clean_float(d[col])

    def do_map_vals_pd(self):
        for col in self.date_cols:
            try:
                self.data[col] = list(map(lambda x:clean_date(x), self.data[col]))
            except KeyError:
                pass
        for col in self.str_cols:
            try:
                self.data[col] = list(map(lambda x:clean_str(x), self.data[col]))
            except KeyError:
                pass
        for col in self.float_cols:
            try:
                self.data[col] = list(map(lambda x:clean_float(x), self.data[col]))
            except KeyError:
                pass
        for col in self.int_cols:
            try:
                self.data[col] = list(map(lambda x:clean_int(x), self.data[col]))
            except KeyError:
                pass


class ETLRtk(ETL):
    def __init__(self, **kwargs):
        super(ETLRtk, self).__init__(**kwargs)
        self.r = RethinkDB()
        self.loop = asyncio.get_event_loop()
        self.__dict__.update(kwargs)
        self.insert_type = "error"
        self.count = 0

    def get_data(self):
        pass

    def unify_cols(self):
        pass

    def gen_id(self):
        pass

    def map_vals(self, x):
        pass

    def insert_db(self, data=None, rec_count=True):
        if data is None:
            data = self.data
        if data is None: return
        self.r.set_loop_type('')
        with self.r.connect(host, port) as conn:
            self.r.db(self.db).table(self.table)\
               .insert(data, conflict=self.insert_type).run(conn)

        self.count += len(data)
        if rec_count:
            self.log_count(key=f"rtk.{self.db}.{self.table}")


class BinanceTickBase(ETLRtk):
    def __init__(self, **kwargs):
        super(BinanceTickBase, self).__init__(**kwargs)
        self.data = None

    def get_data(self, gen_id=True, to_json=True):
        self.unify_cols()
        self.map_vals()
        self.unify_data(gen_id=gen_id, to_json=to_json)

    def unify_data(self, gen_id=True, to_json=True):
        if gen_id: self.data = self.data.assign(id=self.data.apply(lambda x: self.gen_id(x), axis=1))
        if to_json: self.data = json.loads(self.data.to_json(orient="records"))

    def gen_id(self, x):
        hash_key = f"{x['trade_id']}_{x['time_open']}"
        return hash_key

    def unify_cols(self):
        pass

    def map_vals(self):
        self.do_map_vals()


class BinanceTick(BinanceTickBase):
    def __init__(self, **kwargs):
        super(BinanceTick, self).__init__(**kwargs)
        self.name = "binance_Tick"
        self.db = db_binance
        self.table = table_binance_tick
        self.data = None
        self.client = Client(binance_key, binance_secret)
        self.cols = [
            "time_open",
            "open",
            "high",
            "low",
            "close",
            "vol",
            "time_close",
            "vol_quote_asset",
            "number_of_trades",
            "vol_taker_buy_base_asset",
            "vol_taker_buy_quote_asset",
            "ignore"
        ]
        self.float_cols = [
            "open",
            "high",
            "low",
            "close",
            "vol",
            "vol_quote_asset",
            "vol_taker_buy_base_asset",
            "vol_taker_buy_quote_asset",
        ]
        self.int_cols = [
            "number_of_trades",
            "ignore",
        ]

    def _get_data(self, trade_id, symbol, date_start, date_end):
        klines = self.client.get_historical_klines(trade_id,\
                Client.KLINE_INTERVAL_1HOUR, date_start, date_end)
        self.data = pd.DataFrame.from_records(klines)
        if self.data.empty: return
        self.data.columns = self.cols
        self.data = self.data.assign(trade_id = trade_id)
        self.data = self.data.assign(symbol = symbol)


    def get_data(self, trade_id, symbol, date_start="2017-01-01", date_end=today, gen_id=True, to_json=True):
        date_start = date_parser.parse(date_start).strftime("%d %B, %Y")
        date_end = date_parser.parse(date_end).strftime("%d %B, %Y")
        self._get_data(trade_id, symbol, date_start, date_end)
        if self.data is None:
            self.logger.info(f"{trade_id} {date_start} {date_end}")
            return
        if len(self.data) == 0:
            self.logger.info(f"{trade_id} {date_start} {date_end}")
            return
        super(BinanceTick, self).get_data(gen_id=gen_id, to_json=to_json)
