import requests
from dotenv import load_dotenv
import os
import datetime as dt
from twilio.rest import Client

load_dotenv()

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

# Datetime config
today = dt.datetime.now().date()

yesterday = today - dt.timedelta(days=1)
yesterday_str = yesterday.strftime('%Y-%m-%d')

yesterday_minus_1 = today - dt.timedelta(days=2)
yesterday_minus_1_str = yesterday_minus_1.strftime('%Y-%m-%d')

# Alpha Vantage API Details
av_api_key = os.environ['AV_API_KEY']

av_url = 'https://www.alphavantage.co/query'
av_params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK,
    'apikey': av_api_key,
}

# News API Details
news_api_key = os.environ['NEWS_API_KEY']

news_url = "https://newsapi.org/v2/everything"
news_params = {
    'qInTitle': COMPANY_NAME,
    'from': yesterday_str,
    'pageSize': 3,
    'apiKey': news_api_key,
}

# Twilio Client Details
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']

# Phone numbers
txt_out_no = os.environ['TXT_OUT']
txt_in_no = os.environ['TXT_IN']

# Stock data request
av_r = requests.get(av_url, params=av_params)
av_r.raise_for_status()
stock_data = av_r.json()

yesterday_close = float(stock_data['Time Series (Daily)'][f'{yesterday_str}']['4. close'])
yesterday_minus_1_close = float(stock_data['Time Series (Daily)'][f'{yesterday_minus_1_str}']['4. close'])

# Percentage change calculation
price_delta = round(((yesterday_close / yesterday_minus_1_close) - 1) * 100, 2)

if abs(price_delta) >= 5:
    # News data request
    news_r = requests.get(news_url, params=news_params)
    news_r.raise_for_status()
    news_data = news_r.json()

    headline = news_data['articles'][0]['title']
    brief = news_data['articles'][0]['description']

    # Send an SMS with the percentage change & each article's title & description to a predefined phone number
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"{COMPANY_NAME}: {price_delta}%\nHeadline: {headline}\nBrief: {brief}",
        from_=txt_out_no,
        to=txt_in_no
    )
    print(message.status)
