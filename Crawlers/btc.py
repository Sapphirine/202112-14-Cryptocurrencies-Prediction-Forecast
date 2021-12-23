from utils import *
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='dataset and model params.')
    parser.add_argument('-f', '--freq', dest='freq', default="1hour", type=str)
    parser.add_argument('-d', '--dir_path', dest='dir_path', default="/home/savik/Cryptocurrencies-Prediction-Forecast/MLDL/data", type=str)
    args = parser.parse_args()

    freq = args.freq 
    crawler = BinanceTick()
    crawler.get_data("BTCTUSD", "BTC", freq, gen_id=False)
    crawler.clean_date(freq)
    if freq == "1hour":
        crawler.dump_csv(args.dir_path, f"btc_{args.freq}")
    elif freq == "day":
        crawler.dump_csv(args.dir_path, f"btc")
    #dirName = f"btc_{freq}"
    #fileName = str(int(datetime.timestamp(datetime.utcnow()))) + str(random.randint(0, 100)) + '.csv'
    #dataset = "crypto"
    #table = f"btc_{freq}"
    #uploadToStorage(df, fileName, dirName)
    #uploadToBigQuery(fileName, dirName, table, dataset)
