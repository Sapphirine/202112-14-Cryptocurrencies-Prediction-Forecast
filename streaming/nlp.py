
from google.cloud import language
import os

def analyze_text_sentiment(text):
    client = language.LanguageServiceClient()
    document = language.Document(content=text, type_=language.Document.Type.PLAIN_TEXT)

    response = client.analyze_sentiment(document=document)

    sentiment = response.document_sentiment
    results = dict(
        text=text,
        score=f"{sentiment.score:.1%}",
        magnitude=f"{sentiment.magnitude:.1%}",
    )
    
    #['text', 'score', 'magnitude']
    for k, v in results.items():
        print(v)
        #print(f"{k:10}: {v}")
    
    # response = client.documents.classifyText(document=document)
    # print(response)
    
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
            './streaming/e6893-hw0-e5d0369749d2.json'
text = "RT @WhaleStats: 🐳🐳Daily analysis of the top 1000 ETH wallets 🐳🐳\
Top 10 most used smart contracts:\
🥇 #ETH\
🥈 $USDT\
🥉 $USDC\
4⃣ $LINK\
5⃣ $UNI…\
"
analyze_text_sentiment(text)
