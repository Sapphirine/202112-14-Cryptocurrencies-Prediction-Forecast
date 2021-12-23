import configparser


config = configparser.ConfigParser()
config.read("cred.config")
REDDIT_CLIENT_ID = config["reddit"]["CLIENT_ID"]
REDDIT_SECRET_KEY = config["reddit"]["SECRET_KEY"] 
