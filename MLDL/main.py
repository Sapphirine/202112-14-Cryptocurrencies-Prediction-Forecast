from utils import *

# check devices
print(get_available_devices()) 
physical_devices = tf.config.list_physical_devices('GPU')
print("Num GPUs:", len(physical_devices))


if __name__ == '__main__':
    from args import args

    if args.device == 'cpu': args.device = "/cpu:0"
    elif args.device == 'gpu': args.device = "/gpu:0"
    
    df = get_dataset(args)
    X_train, y_train, X_test, y_test, dates_train, dates_test = create_train_test(df, args)
    sequence_length = X_train.shape[1]
    nb_features = X_train.shape[-1]
    model = build_model(sequence_length, nb_features, args)
    #model.summary()
    train_history, model = train_model(X_train, y_train, model, args)
    show_final_history(train_history, dataset, args)
    dump_confusion_matrix(model, X_train, y_train, dates_train, "train", args)
    dump_confusion_matrix(model, X_test, y_test, dates_test, "test", args)
