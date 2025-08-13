import os
from dotenv import load_dotenv
load_dotenv()

apikey = os.getenv("GROK_API_KEY")
weather_apikey = os.getenv("WEATHER_API_KEY")
news_apikey = os.getenv("NEWS_API_KEY")