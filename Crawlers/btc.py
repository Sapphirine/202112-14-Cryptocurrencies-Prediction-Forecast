from utils import *

if __name__ == '__main__':
    crawler = BinanceTick()
    crawler.get_data("BTCTUSD", "BTC", gen_id=False)
    df = pd.DataFrame(crawler.data)
    df.to_csv("./btc_1hr.csv", index=False)
