# Cryptocurrencies-Prediction-Forecast
EECS E6893: Big Data Analytics Team14 project

## Contributors
- [Cheng-Hao Ho(ch3561)](https://github.com/chho33)
- [Shuoting Kao(sk4920)](https://github.com/tim-kao)	
- [Wei-Ren Lai(wl2777)](https://github.com/swallen000)

## Architecture

![image](https://github.com/tim-kao/Cryptocurrencies-Prediction-Forecast/blob/main/images/architecture-new.png)

## [Project Proposal](https://github.com/tim-kao/Cryptocurrencies-Prediction-Forecast/blob/main/project%20proposal/EECS%20E6893_%20Big%20Data%20Analytics%20Project%20Proposal.docx)

## [Project proposal slides](https://github.com/tim-kao/202112-14-Cryptocurrencies-Prediction-Forecast/blob/main/slides/Cryptocurrencies%20Prediction%20%26%20Forecast.pdf)

## [Progress report](https://github.com/tim-kao/Cryptocurrencies-Prediction-Forecast/blob/main/progress%20report/progress_report_group14.pdf)

## [Presentation final slides](https://github.com/tim-kao/202112-14-Cryptocurrencies-Prediction-Forecast/blob/main/slides/Cryptocurrencies%20Prediction%20%26%20Forecast-final.pdf)

## Prerequisite

### Install Python packages through pip
- git clone repo and install all necessary packages (either onto system or in virtual environment)
   using [requirements.txt](https://github.com/tim-kao/Cryptocurrencies-Prediction-Forecast/blob/main/requirements.txt)

        `pip install -r requirements.txt`

### Configuration Files
- [requirements.txt](https://github.com/tim-kao/Cryptocurrencies-Prediction-Forecast/blob/main/requirements.txt)
    
    Put your GCP credentials at ./pubsub/credential/myFile.privateKey.json and ./credential/gcp_key.json
    
### Install Java runtime
- Install the Java runtime through apt: run `sudo apt install default-jdk`.
- Set JAVA_HOME variable in the environment. To find the correct java path, run `sudo update-alternatives --config java`.


## Services/Methods
To run our services/methods, please go to the corresponding directories first.

### Web Application
#### Directory: **app**
- **sse.py**: flask endpoints along with frontends
- To run the server, run: `python3 sse.py`
- Once running, you can use a browser to access the URL http://URL:8222/

### Data Scrapers
#### Directories: **Crawlers**, **Reddit**, **streaming**
- **Crawlers/btc.py**: Bitcoin transactions scraper.
   - This scraper crawl the data by Binance API. To use this API, please register an account and get the credential. The detail is descirbed at https://binance-docs.github.io/apidocs/spot/en/.
   - Once getting the credential, set the corresponding key and secret in **cred.config** (you might need to create a new file). Please refer to **cred.config.example**.
   - Usage: `python btc.py --freq [1hour|day] --dir_path DATA_PATH_YOU_WANT_TO_STORE`.
   - Example, Scrape all historical daily data and store in the `data` directory: `python btc.py --freq day --dir_path ./data`.

- **Reddit/\*.py** Reddit scraper.
   - Usage: `python *.py`.

- **streaming/\*.py** twitter streaming scraper.
   - To run the twitter in real-time manner, please run `python twitterHTTPClient.py` first.
   - Then run: `python sparkStreaming.py`.

### Pub/Sub
#### Directory: **pubsub**
- To see the example code of the pubsub publisher and subscriber, please refer to **publisher.py**, **subscriber.py**.
- To see the email sender code, please refer to **sender.py**.

### Machine Learning
#### Directory: **MLDL**
This directory if for machine learning model training, predicting, and backtesting. There are two models availabe: WaveNet and Convolutional vision Transformer (CvT).
- **args.py**: The arguments for setting hyper-parameter for the models. The explanation is as below:
   - threshold: Type: Float. Range: 0 - 1. This value is used for our labelling algorithm. When it iterates the data points, it will "look back" the previous "peak" (highest price point) or "valley" (lowest price point) and see the different between itself and those look-back value. Once the difference percentage exceeds the threshold, it will record the look-back points.
   - freq: Type: String. Decide the data type (ie. daily or hourly data.)
   - shift: Type: Integer. To decide the labelling position. Eg. if would like to predict tomorrow's label, then set the shift as 1.
   - smooth: Type: Integer. Range: \[0, 1\]. Increase the data points or not.
   - window_size: Type: Integer. Set the input dimensions by the time (days/hours.)
   - test_size: Type: Float. Range: 0 - 1. Set the test data size (in percentage.)
   - valid_size: Type: Float. Range: 0 - 1. Set the validation data size (in percentage.)
   - dataset: Type: String. Range: \[btc, btc_trend, btc_wiki, btc_trend_wiki\]. Decide the dataset to train.
   - range_tolerance: Type: Float. For smoothing algorithm. The threshold for allowing more data points to be labeled as buying or selling.
   - epochs: Type: Integer. Training epochs.
   - batch_size: Type: Integer. Training batch size.
   - patience: Type: Integer. For early stopping. Once the performance doesn't improve for this value epochs, the training stops.
   - device: Type: String. Range:\[cpu, gpu\]. To decide to use cpu or gpu to train the model.
   - max_dilation: Type: Integer. The max dilation value for CNN.
   - n_filters: Type: Integer. The kernel size for CNN.
   - filter_width: Type: Integer. The filter width for CNN.
   - learning_rate: Type: Float. The learning rate for traing a model.
   - auto_loss_weight: Type: Integer. Range: \[0, 1\]. To decide whether allocates the loss panelty to rare data by a ratio of data size between huge and rare data or not.
- **main.py**: The entry point of training the WaveNet model. Can be ran with the arguments described above. After training, it also predicts the result, draws the training process, as well as the confusion matrix, and store in outputs directory. Note that different hyper-parameter will generate the different sub-directory in outputs to distinguish the different runs.
- **main_cvt.py**: The entry point of training the CvT model. Can be ran with the arguments described above.
- **pred.py**: Can dry-run the prediction. Same logic with **main.py**.
- **utils.py**: Common utilities.
- **settings.py**: Common settings.
- **cvt.py, cvt_module.py**: CvT model related.
- **backtest.py**: execute back testing. Usage: `python backtest.py train.csv test.csv btc.csv`. train.csv means the model prediction on training dataset, while test.csv means the testing dataset. btc.csv means the original input data.

### Airflow
#### Directory: **airflow**
Before running the airflow, please:
- Move this directory to the path: ~/airflow. `cd airflow ~/`.
- See the tutorial to install the airflow and run it: google airflow installation.
- Get the Reddit scraping API: https://www.reddit.com/dev/api and set the corresponding CLIENT_ID and SECRET_KEY in the **cred.config** file. (You may need to create the file by yourself.) Please refer to the **cred.config.example**.
You will find all the DAG in **dag/scripts** directory. The main entry points are: **hourly.py**, which manages hourly routines, and **daily.py**, which manages daily routines.

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
