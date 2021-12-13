import os
from google.cloud import pubsub_v1

if __name__ == '__main__':
    credentials_path = './pubsub/credential/myFile.privateKey.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

    publisher = pubsub_v1.PublisherClient()
    # topic_path = 'projects/e6893-hw0/topics/whaleAlert'
    topic_path = 'projects/e6893-hw0/topics/model-prediction'

    data = '21:31:27 12,779 USDT (12,779 USD) transferred from huobi to unknown wallet'
    data = 'Predict price 9999'
    data = data.encode('utf-8')
    future = publisher.publish(topic_path, data)
    print(f'published message id {future.result()}')

