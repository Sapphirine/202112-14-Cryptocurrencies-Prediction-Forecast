# Cryptocurrencies-Prediction-Forecast
EECS E6893: Big Data Analytics Team14 project

## Contributors
- [Cheng-Hao Ho(ch3561)](https://github.com/chho33)
- [Shuoting Kao(sk4920)](https://github.com/tim-kao)	
- [Wei-Ren Lai(wl2777)](https://github.com/swallen000)

## Architecture

![image](https://github.com/tim-kao/Cryptocurrencies-Prediction-Forecast/blob/main/images/architecture.png)

## [Project Proposal](https://github.com/tim-kao/Cryptocurrencies-Prediction-Forecast/blob/main/project%20proposal/EECS%20E6893_%20Big%20Data%20Analytics%20Project%20Proposal.docx)

## [Project proposal slides](https://github.com/tim-kao/202112-14-Cryptocurrencies-Prediction-Forecast/blob/main/slides/Cryptocurrencies%20Prediction%20%26%20Forecast.pdf)

## [Progress report](https://github.com/tim-kao/Cryptocurrencies-Prediction-Forecast/blob/main/progress%20report/progress_report_group14.pdf)

## [Presentation final slides](https://github.com/tim-kao/202112-14-Cryptocurrencies-Prediction-Forecast/blob/main/slides/Cryptocurrencies%20Prediction%20%26%20Forecast-final.pdf)

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

## Result
### Confusion matrix
- daily
   - dataset: BitCoin + Google Trend + Wiki
   - shift: 1 (to predict tomorrow’s label)
   - window_size: 30 (30 days as input)
   - n_filters: 32
   - filter_width: 2
   - max_dilation: 5
   - batch_size: 16
   - epochs: 300
   - training data result:
      - <img src="https://imgur.com/hOQ6stW.jpg" width="350" height="350">
   - test data result: 
      - <img src="https://imgur.com/YiQMIXM.jpg" width="350" height="350">
- hourly
   - dataset: BitCoin + Google Trend
   - shift: 0 (to predict today’s label)
   - window_size: 100 (100 hours as input)
   - n_filters: 64
   - filter_width: 2
   - max_dilation: 3
   - batch_size: 16
   - epochs: 20
   - training data result:
      - <img src="https://imgur.com/Mr8YS4Z.jpg" width="350" height="350">
   - test data result: 
      - <img src="https://imgur.com/4mk0b8K.jpg" width="350" height="350">


### Back testing
- Our model is used to predict buy points and sell points, the result in confusion matrix doesn't fully explain our model at all. Therefore, we used back testing to see whether our model can help people to earn model.
- We designed three methods in back testing based on the probability distribution in our result:
   - Used entropy as threshold: Calculate the Sharnon’s Entropy of the probability distribution. If it’s too huge (close to 1), then reject the model prediction.
   - Used percentage as threshold: To see if the highest probability among three exceeds a threshold or not. If not, reject the model prediction.
   - Used difference as threshold: To see if the difference between the highest and the second highest probability exceeds a threshold or not. If not, reject the model prediction.
- Suppose we have 1,000,000 dollars at the beggining (2021-03-04), the result below is how much we have at the end (2021-12-17)
- Daily:
   - Model1: BitCoin
      - *Use entropy as threshold: $1,064,388*
      - *Use percentage as threshold: $1,021,007*
      - *Use difference as threshold: $998,756*
   - Model2: BitCoin + Google Trend
      - *Use entropy as threshold: $1,369,306*
      - *Use percentage as threshold: $1,215,603*
      - *Use difference as threshold: $1,162,341*
   - Model3: BitCoin + Wiki
      - *Use entropy as threshold: $1,143,567*
      - *Use percentage as threshold: $1,032,401*
      - *Use difference as threshold: $982,564* 
   - Model4: BitCoin + Google Trend + Wiki
      - ***Use entropy as threshold: $2,122,670 (the best)***
      - *Use percentage as threshold: $1570829* 
      - *Use difference as threshold: $1177225* 
- Hourly:
   - Model1: BitCoin
      - *Use entropy as threshold: $1145321* 
      - *Use percentage as threshold: $1032654* 
      - *Use difference as threshold: $9821547* 
   - Model2: BitCoin + Google Trend
      - *Use entropy as threshold: $1183372* 
      - *Use percentage as threshold: $1282376* 
      - *Use difference as threshold: $1014512* 
 
      

 



  
