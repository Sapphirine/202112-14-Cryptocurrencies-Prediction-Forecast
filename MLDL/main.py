from utils import *
import argparse

# check devices
print(get_available_devices()) 
physical_devices = tf.config.list_physical_devices('GPU')
print("Num GPUs:", len(physical_devices))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='dataset and model params.')
    # dataset params
    parser.add_argument('-t', '--threshold', dest='threshold', default=0.1, type=float)
    # shift 1: predict yesterday. -1: predict tomorrow
    parser.add_argument('-s', '--shift', dest='shift', default=0, type=int)
    parser.add_argument('-w', '--window_size', dest='window_size', default=30, type=int)
    parser.add_argument('-ts', '--test_size', dest='test_size', default=0.1, type=float)
    parser.add_argument('-vs', '--valid_size', dest='valid_size', default=0.1, type=float)
    parser.add_argument('-d', '--dataset', dest='dataset', default='btc', choices=['btc', 'btc_trend', 'btc_wiki', 'btc_trend_wiki', 'btc_text', 'all'])
    # model params
    parser.add_argument('-ep', '--epochs', dest='epochs', default=300, type=int)
    parser.add_argument('-b', '--batch_size', dest='batch_size', default=16, type=int)
    parser.add_argument('-p', '--patience', dest='patience', default=100, type=int)
    parser.add_argument('-dv', '--device', dest='device', default='cpu', choices=['cpu', 'gpu'])
    parser.add_argument('-md', '--max_dilation', dest='max_dilation', default=7, type=int)
    parser.add_argument('-nf', '--n_filters', dest='n_filters', default=64, type=int)
    parser.add_argument('-fd', '--filter_width', dest='filter_width', default=2, type=int)
    parser.add_argument('-lr', '--learning_rate', dest='learning_rate', default=3e-6, type=float)
    parser.add_argument('-lw', '--auto_loss_weight', dest='auto_loss_weight', default=1, type=int)
    
    args = parser.parse_args()
    dataset = args.dataset

    if args.device == 'cpu': args.device = "/cpu:0"
    elif args.device == 'gpu': args.device = "/gpu:0"
    
    df_btc = get_btc()
    if dataset == 'btc':
        df_train = df_btc 
    elif dataset == 'btc_trend':
        df_trend = get_trend()
        df_train = df_btc.join(df_trend).dropna()
    elif dataset == 'btc_wiki':
        df_wiki = get_wiki()
        df_train = df_btc.join(df_wiki).dropna()
    elif dataset == 'btc_trend_wiki':
        df_wiki = get_wiki()
        df_trend = get_trend()
        df_train = df_btc.join(df_wiki).join(df_trend).dropna()
    
    X_train, y_train, X_test, y_test, dates_train, dates_test = create_train_test(df_train, args)
    sequence_length = X_train.shape[1]
    nb_features = X_train.shape[-1]
    model = build_model(sequence_length, nb_features, args)
    #model.summary()
    train_history, model = train_model(X_train, y_train, model, args)
    show_final_history(train_history, dataset, args)
    dump_confusion_matrix(model, X_train, y_train, dates_train, "train", args)
    dump_confusion_matrix(model, X_test, y_test, dates_test, "test", args)
