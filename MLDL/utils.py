import numpy as np
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, classification_report
from tensorflow.keras.utils import plot_model, model_to_dot
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import (Add, Multiply, LeakyReLU, Input, Conv1D, Dropout, Activation, BatchNormalization, MaxPooling1D, ZeroPadding1D, AveragePooling1D, Flatten, Dense)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint, Callback, EarlyStopping
import tensorflow_addons as tfa
from tensorflow.python.client import device_lib
import matplotlib.pyplot as plt
import itertools
import pandas_gbq
from settings import *


def get_available_devices():
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos]


def create_train_test(df_train, args):
    test_size = args.test_size
    window_size = args.window_size
    shift = args.shift
    threshold = args.threshold

    df_train = labelling(df_train, shift, threshold)
    if args.smooth:
        range_buy_sell(df_train, args.range_tolerance)
    print(df_train.query("Label == 1").shape, df_train.query("Label == 2").shape, df_train.query("Label == 0").shape)
    X, Y, dates= slicing(df_train, window_size=window_size)
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=0)
    dates_train = dates[:len(y_train)]
    dates_test = dates[len(y_train):]
    #One-hot encode the labels
    y_train = to_categorical(y_train)
    y_test= to_categorical(y_test)
    return X_train, y_train, X_test, y_test, dates_train, dates_test


def get_wiki():
    df_wiki = pd.read_csv(f"{data_dir}/wiki.csv")
    df_wiki = df_wiki.rename(columns={"date": "Date"}).drop(["timestamp"], axis=1).set_index("Date")
    return df_wiki


def get_trend(args):
    freq = args.freq
    df_trend = pd.read_csv(f"{data_dir}/trend.csv")
    if freq == "day":
        df_trend = df_trend.assign(Date=df_trend['datetime'].str.split(' ',expand=True)[0])
        df_trend = df_trend.groupby("Date").sum("trend")[["trend"]]
    elif freq == "1hour":
        df_trend = df_trend.set_index("timestamp").drop(["datetime"], axis=1)
    return df_trend


def get_btc(args):
    freq = args.freq
    if freq == "day":
        df_btc = pd.read_csv(f"{data_dir}/btc.csv")
        df_btc = df_btc[COLS]
        df_btc = df_btc.set_index("Date")
    elif freq == "1hour":
        cols_remove = ["trade_id", "symbol", "ignore", "time_close"]
        df_btc = pd.read_csv(f"{data_dir}/btc_1hr.csv")
        df_btc = df_btc.drop(cols_remove, axis=1)
        df_btc.time_open = (df_btc.time_open/1000).astype(int)
        df_btc = df_btc.rename(columns={"time_open": "timestamp"})
        df_btc = df_btc.set_index("timestamp")
    return df_btc


def get_text_sent():
    try:
        # Perform a query.
        QUERY = '''
            SELECT TIMESTAMP_TRUNC(time, HOUR, "UTC") AS hour, 
                avg(pos) as posAvg, 
                avg(neg) as negAvg, 
                avg(neu) as neuAvg,
                avg(compound) as compoundAvg
            FROM crypto.btc group by hour;
        '''
        rows = []
        for row in pandas_gbq.read_gbq(query=QUERY, project_id='e6893-hw0').values.tolist():
            rows.append({
                "timestamp": int(row[0].timestamp()),
                "posAvg": row[1],
                "negAvg": row[2],
                "neuAvg": row[3],
                })

        return pd.DataFrame(rows)
    except Exception as e:
        print(e)


def range_buy_sell(df, tolerance=0.03):
    buy_point = []
    sell_point = []
    for data in df.iterrows():
        price = data[1]['Close']
        label = data[1]['Label']
        if label == 1:
            buy_point.append(price)
        elif label == 2:
            sell_point.append(price)

    buy_pos = 0
    sell_pos = -1
    for i, data in df.iterrows():
        price = data['Close']
        label = data['Label']
        if label == 1:
            sell_pos += 1
            if sell_pos == len(sell_point):
                break
        elif label == 2:
            buy_pos += 1
            if buy_pos == len(buy_point):
                break
        else:
            cur_buy = buy_point[buy_pos]
            if abs(price - cur_buy)/cur_buy <= tolerance:
                df.at[i,'Label'] = 1
            if sell_pos == -1:
                continue
            cur_sell = sell_point[sell_pos]
            if abs(cur_sell - price)/cur_sell <= tolerance:
                df.at[i,'Label'] = 2


def collect_peaks(data, threshold, price_col="Close"):
    peaks = set()
    price_max = 0
    price_min = float('inf')
    date_start = data.head(1).index[0]
    profit = 0
    for d in data.iterrows():
        date = d[0]
        price = d[1][price_col]
        rise = (price - price_min) / price_min
        #print(date, price, price_min, rise)
        if price < price_min:
            price_min = price
            profit = (price_max - price_min) / price_min
            if profit >= threshold:
                peaks.add(date_start)
        elif price > price_max or rise >= threshold:
            price_min = price
            price_max = price
            date_start = date
    return sorted(list(peaks))
    
    
def collect_valleys(data, threshold, price_col="Close"):
    valleys = set()
    price_max = 0
    price_min = float('inf')
    date_start = data.head(1).index[0]
    profit = 0
    for d in data.iterrows():
        date = d[0]
        price = d[1][price_col]
        drop = (price_max - price) / price
        if price > price_max:
            price_max = price
            profit = (price_max - price_min) / price_min
            if profit >= threshold:
                valleys.add(date_start)
        elif price < price_min or drop >= threshold:
            price_min = price
            price_max = price
            date_start = date
    return sorted(list(valleys))


def collect_labels(data, threshold):
    peaks = collect_peaks(data, threshold)
    valleys = collect_valleys(data, threshold)
    flats = sorted(list(set(data.index) - set(peaks) - set(valleys)))
    peaks = pd.DataFrame({"Date": peaks, "Label": PeakLabel})
    valleys = pd.DataFrame({"Date": valleys, "Label": ValleyLabel})
    flats = pd.DataFrame({"Date": flats, "Label": FlatLabel})
    return pd.concat([peaks, valleys, flats], axis=0).sort_values("Date").set_index("Date")


def labelling(data, shift, threshold):
    labels = collect_labels(data, threshold)
    df = data.join(labels)
    df = df.sort_index()
    if shift:
        df = df.assign(y=df["Label"].shift(shift)).dropna().drop(["Label"], axis=1)
        df = df.rename(columns={"y": "Label"})
        df.Label = df.Label.astype(int)
    return df


def slicing(data, label_col="Label", window_size=30):
    X = []
    Y = []
    dates = []
    
    for i in range(len(data) - window_size + 1):
        x = data.iloc[i: i+window_size]
        y = x.tail(1)[label_col]
        X.append(x.drop([label_col], axis=1).to_numpy())
        Y.append(y.to_numpy())
        dates.append(x.tail(1).index[0])
        
    return np.array(X), np.array(Y), dates


def build_model(sequence_length, nb_features, args):
    n_filters = args.n_filters 
    filter_width = args.filter_width 
    learning_rate = args.learning_rate
    max_dilation = args.max_dilation
    dilation_rates = [i for i in range(1, max_dilation+1)]
    
    history_seq = Input(shape=(sequence_length, nb_features))
    x = history_seq
    
    skips = []
    for dilation_rate in dilation_rates:
    
        # preprocessing - equivalent to time-distributed dense
        x = Conv1D(16, 1, padding='same', activation=LeakyReLU())(x)
    
        # filter
        x_f = Conv1D(filters=n_filters,
                     kernel_size=filter_width, 
                     padding='same',
                     dilation_rate=dilation_rate)(x)
        x_f = LeakyReLU()(x_f)
        x_f = BatchNormalization()(x_f)
    
        # gate
        x_g = Conv1D(filters=n_filters,
                     kernel_size=filter_width, 
                     padding='same',
                     dilation_rate=dilation_rate)(x)
        # combine filter and gating branches
        z = Multiply()([Activation('tanh')(x_f),
                        Activation('sigmoid')(x_g)])
    
        # postprocessing - equivalent to time-distributed dense
        z = Conv1D(16, 1, padding='same', activation=LeakyReLU())(z)
    
        # residual connection
        x = Add()([x, z])    
    
        # collect skip connections
        skips.append(z)
    
    # add all skip connection outputs 
    out = Activation(LeakyReLU())(Add()(skips))
    
    out = Flatten()(out)
    
    #Final dense layer
    out = Dense(len(class_names), activation="softmax")(out)
    
    model = Model(history_seq, out)
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    
    # https://www.tensorflow.org/addons/api_docs/python/tfa/metrics/F1Score#
    #f1_score = tfa.metrics.F1Score(num_classes=3, threshold=None)
    
    model.compile(loss="categorical_crossentropy", optimizer=optimizer, metrics=('accuracy'))
    return model


def train_model(X_train, y_train, model, args):
    batch_size = args.batch_size
    epochs = args.epochs
    patience = args.patience
    valid_size = args.valid_size
    device = args.device

    model_name = get_model_name(args)
    checkpoint = ModelCheckpoint(f"{model_name}.h5", monitor='val_loss', verbose=1, save_best_only=True, mode='max')
    
    early_stopping = EarlyStopping(monitor='val_loss', patience=patience)
    
    sample_weight = None
    if args.auto_loss_weight:
        weight_val = len(np.where(y_train == np.array([1,0,0]))[0]) / len(np.where(y_train != np.array([1,0,0]))[0])
        sample_weight = np.ones(shape=(len(y_train),))
        sample_weight[np.where(y_train != np.array([1,0,0]))[0]] = weight_val
    
    with tf.device(device):
        train_history = model.fit(X_train, y_train,
            steps_per_epoch=len(X_train)//batch_size,
            epochs=epochs,
            sample_weight=sample_weight,
            shuffle=True,
            verbose=1, validation_split=valid_size,
            callbacks=[early_stopping, checkpoint]
            )
    return train_history, model


def show_final_history(history, dataset, args):
    window_size = args.window_size
    shift = args.shift
    plt.style.use("ggplot")
    fig, ax = plt.subplots(1,2,figsize=(15,5))
    ax[0].set_title('Loss')
    ax[1].set_title('Accuracy')
    ax[0].plot(history.history['loss'],label='Train Loss')
    ax[0].plot(history.history['val_loss'],label='Validation Loss')
    ax[1].plot(history.history['accuracy'],label='Train Accura|cy')
    ax[1].plot(history.history['val_accuracy'],label='Validation Accuracy')
    
    ax[0].legend(loc='upper right')
    ax[1].legend(loc='lower right')
    
    out_dir = get_out_dir(args)
    plt.savefig(f"{out_dir}/history.png")


def plot_confusion_matrix(cm, classes, title='Confusion Matrix', cmap=plt.cm.Blues):
    cm = cm.astype('float')/cm.sum(axis=1)[:,np.newaxis]
    plt.figure(figsize=(10,10))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes,rotation=45)
    plt.yticks(tick_marks, classes)
    
    fmt = '.2f'
    thresh = cm.max()/2.
    for i,j in itertools.product(range(cm.shape[0]),range(cm.shape[1])):
        plt.text(j,i,format(cm[i,j],fmt),
                horizontalalignment="center",
                color="white" if cm[i,j] > thresh else "black")
    
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')


def dump_confusion_matrix(model, x, y, dates, data_type, args):
    window_size = args.window_size
    shift = args.shift
    dataset = args.dataset

    pred = model.predict(x)
    pred = np.argmax(pred, axis=1)
    actual = np.argmax(y, axis=1)
    cnf_mat = confusion_matrix(actual, pred)
    np.set_printoptions(precision=2)
    
    plt.figure()
    plot_confusion_matrix(cnf_mat,classes=class_names)
    plt.grid(None)

    out_dir = get_out_dir(args)
    plt.savefig(f"{out_dir}/confusiont_{data_type}.png")
    dump_pred(model, x, dates, data_type, args, pred)


def dump_pred(model, x, dates, data_type, args, pred=None):
    out_dir = get_out_dir(args)
    if pred is None:
        pred = model.predict(x)
        pred = np.argmax(pred, axis=1)
    df_pred = pd.DataFrame(list(zip(dates, pred)), columns=["date", "pred"])
    df_pred = df_pred.set_index("date")
    df_pred.to_csv(f"{out_dir}/pred_{data_type}.csv")


def load_model(args):
    model_name = get_model_name(args)
    return tf.keras.models.load_model(f"{model_name}.h5")


def get_out_dir(args):
    global output_dir
    out_dir = f"{output_dir}/{args.dataset}/{args.freq}_thr_{args.threshold}_autow_{args.auto_loss_weight}_win_{args.window_size}_sh_{args.shift}_lr_{args.learning_rate}_bch_{args.batch_size}_ep_{args.epochs}_filt_{args.n_filters}_{args.filter_width}_mdil_{args.max_dilation}"
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    return out_dir


def get_model_name(args):
    global model_dir
    if not os.path.isdir(f"{model_dir}/{args.dataset}"):
        os.makedirs(f"{model_dir}/{args.dataset}")
    model_name = f"{model_dir}/{args.dataset}/{args.freq}_thr_{args.threshold}_autow_{args.auto_loss_weight}_win_{args.window_size}_sh_{args.shift}_lr_{args.learning_rate}_bch_{args.batch_size}_ep_{args.epochs}_filt_{args.n_filters}_{args.filter_width}_mdil_{args.max_dilation}"
    return model_name
