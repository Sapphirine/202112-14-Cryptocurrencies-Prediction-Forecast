import requests

getTransactionsUrl = 'https://blockchain.info/unconfirmed-transactions?format=json'
exploreTransactionUrl = 'https://blockchain.info/rawtx/'

# populuate data into bigquery
# while True:
if True:
    response = requests.get(getTransactionsUrl)
    if response.status_code == 200:
        transactions = response.json()['txs']
        for transaction in transactions:
            transExploreResponse = requests.get(exploreTransactionUrl + transaction['hash'])
            if transExploreResponse.status_code == 200:
                print('save the transaction: ' + transaction['hash'] + ' into bigquery')
                transactionDetail = transExploreResponse.json()
                print(transactionDetail['inputs'])
                # hash, time, fee, input amount, output amount, from, to
                # to: transactionDetail['inputs'][0]['prev_out']['addr']
                # to: transactionDetail['out'][1]['addr]