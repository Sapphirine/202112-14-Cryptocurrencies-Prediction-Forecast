# Cryptocurrencies-Prediction-Forecast
EECS E6893: Big Data Analytics Team14 project

## Contributors
- [Cheng-Hao Ho(ch3561)](https://github.com/chho33)
- [Shuoting Kao(sk4920)](https://github.com/tim-kao)	
- [Wei-Ren Lai(wl2777)](https://github.com/swallen000)

## Architecture

![image](https://github.com/tim-kao/Cryptocurrencies-Prediction-Forecast/blob/main/images/architecture.png)

## [Project Proposal](https://github.com/tim-kao/Cryptocurrencies-Prediction-Forecast/blob/main/project%20proposal/EECS%20E6893_%20Big%20Data%20Analytics%20Project%20Proposal.docx)

## [Progress report](https://github.com/tim-kao/Cryptocurrencies-Prediction-Forecast/blob/main/progress%20report/progress_report_group14.pdf)

## [Presentation slides](https://github.com/tim-kao/202112-14-Cryptocurrencies-Prediction-Forecast/blob/main/slides/Cryptocurrencies%20Prediction%20%26%20Forecast.pdf)

## Service/Methods
- app/sse.py flask endpoints along with frontends
- Crawlers/*.py btc price scraper
- MLDL deep learning model
- pubsub publisher and subscriber example code
- Reddit/*.py Reddit scraper
- streaming/*.py twitter streaming

## Build, run, test instructions of a service

### Build
- git clone repo and install all necessary packages (either onto system or in virtual environment)
   using [requirements.txt](https://github.com/tim-kao/Cryptocurrencies-Prediction-Forecast/blob/main/requirements.txt)

        pip install -r requirements.txt

### Configuration Files
- [requirements.txt](https://github.com/tim-kao/Cryptocurrencies-Prediction-Forecast/blob/main/requirements.txt)
    
    Put your GCP credentials at ./pubsub/credential/myFile.privateKey.json and ./credential/gcp_key.json

### Run
- python3 ./app/sse.py
- Once running, you can use a browser to access the URL http://URL:8222/