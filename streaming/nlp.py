
from google.cloud import language
import sys
import requests
import time
import subprocess
import re
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
        
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './streaming/e6893-hw0-c8eb72b6d91a.json'
text = "Ethereum is the second most popular cryptocurrency after Bitcoin. But did you know that Ethereum is a blockchain platform that also has its own currency called ETH?"
analyze_text_sentiment(text)