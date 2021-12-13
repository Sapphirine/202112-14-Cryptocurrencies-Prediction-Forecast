from utils import *

# check devices
print(get_available_devices()) 
physical_devices = tf.config.list_physical_devices('GPU')
print("Num GPUs:", len(physical_devices))


if __name__ == '__main__':
    from args import args
    dataset = args.dataset
    if args.device == 'cpu': args.device = "/cpu:0"
    elif args.device == 'gpu': args.device = "/gpu:0"
    
    df_btc = get_btc(args)
    if dataset == 'btc':
        df_train = df_btc 
    elif dataset == 'btc_trend':
        df_trend = get_trend(args)
        df_train = df_btc.join(df_trend).dropna()
    elif dataset == 'btc_wiki':
        df_wiki = get_wiki()
        df_train = df_btc.join(df_wiki).dropna()
    elif dataset == 'btc_trend_wiki':
        df_wiki = get_wiki()
        df_trend = get_trend(args)
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
