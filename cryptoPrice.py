import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import json
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
#---------------------------------#
# New feature (make sure to upgrade your streamlit library)
# pip install --upgrade streamlit

#---------------------------------#
# Page layout
## Page expands to full width
st.set_page_config(layout="wide")
#---------------------------------#
# Title

image = Image.open('crypto_set.jpg')

st.image(image, width = 600)

st.title('Crypto Price App')
st.markdown("""
This app retrieves cryptocurrency prices for the top 500 cryptocurrency from the **CoinMarketCap**!
""")
#---------------------------------#
# About
expander_bar = st.expander("About")
expander_bar.markdown("""
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, BeautifulSoup, requests, json, time
* **Data source:** [CoinMarketCap](http://coinmarketcap.com).
* **Source of code:** I used my previous project from github *[Extracting Crypto Data With API](https://github.com/MegaPudding/DataScience_Portfolio/blob/main/Crypto%20API%20Pull.ipynb)* 
""")


#---------------------------------#
# Page layout (continued)
## Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
col1 = st.sidebar
col2, col3 = st.columns((2,1))

#---------------------------------#
# Sidebar + Main panel
col1.header('Input Options')

## Sidebar - Currency price unit
currency_price_unit = col1.selectbox('Currency for price', ('USD','',''))

# Web scraping of CoinMarketCap data
@st.cache
def load_data():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
      'start':'1',
      'limit':'500',
      'convert':'USD'
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': '6c326d9d-7fee-490d-8a07-4e9590c37d9e',
    }

    session = Session()
    session.headers.update(headers)

    try:
      response = session.get(url, params=parameters)
      data = json.loads(response.text)
      #print(data)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
      print(e)
    listings = data['data']

    coin_name = []
    coin_symbol = []
    market_cap = []
    percent_change_1h = []
    percent_change_24h = []
    percent_change_7d = []
    price = []
    volume_24h = []

    for i in listings:
      coin_name.append(i['slug'])
      coin_symbol.append(i['symbol'])
      price.append(i['quote']['USD']['price'])
      percent_change_1h.append(i['quote']['USD']['percent_change_1h'])
      percent_change_24h.append(i['quote']['USD']['percent_change_24h'])
      percent_change_7d.append(i['quote']['USD']['percent_change_7d'])
      market_cap.append(i['quote']['USD']['market_cap'])
      volume_24h.append(i['quote']['USD']['volume_24h'])

    df = pd.DataFrame(columns=['coin_name', 'coin_symbol', 'market_cap', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d', 'price', 'volume_24h'])
    df['coin_name'] = coin_name
    df['coin_symbol'] = coin_symbol
    df['price'] = price
    df['percent_change_1h'] = percent_change_1h
    df['percent_change_24h'] = percent_change_24h
    df['percent_change_7d'] = percent_change_7d
    df['market_cap'] = market_cap
    df['volume_24h'] = volume_24h
    return df

df = load_data()
## Sidebar - Cryptocurrency selections
sorted_coin = sorted( df['coin_symbol'] )
selected_coin = sorted_coin

df_selected_coin = df[ (df['coin_symbol'].isin(selected_coin)) ] # Filtering data

## Sidebar - Number of coins to display
num_coin = col1.slider('Display Top N Coins', 1, 100, 50)
df_coins = df_selected_coin[:num_coin]

## Sidebar - Percent change timeframe
percent_timeframe = col1.selectbox('Percent change time frame',
                                    ['7d','24h', '1h'])
percent_dict = {"7d":'percent_change_7d',"24h":'percent_change_24h',"1h":'percent_change_1h'}
selected_percent_timeframe = percent_dict[percent_timeframe]

## Sidebar - Sorting values
sort_values = col1.selectbox('Sort values?', ['Yes', 'No'])

col2.subheader('Price Data of Selected Cryptocurrency')
col2.write('Data Dimension: ' + str(df_selected_coin.shape[0]) + ' rows and ' + str(df_selected_coin.shape[1]) + ' columns.')

col2.dataframe(df_coins)



#---------------------------------#
# Preparing data for Bar plot of % Price change
col3.subheader('Table of % Price Change')
df_change = pd.concat([df_coins.coin_symbol, df_coins.percent_change_1h, df_coins.percent_change_24h, df_coins.percent_change_7d], axis=1)
df_change = df_change.set_index('coin_symbol')
df_change['positive_percent_change_1h'] = df_change['percent_change_1h'] > 0
df_change['positive_percent_change_24h'] = df_change['percent_change_24h'] > 0
df_change['positive_percent_change_7d'] = df_change['percent_change_7d'] > 0
col3.write('Data Dimension: ' + str(df_change.shape[0]) + ' rows and ' + str(df_change.shape[1]) + ' columns.')
col3.dataframe(df_change)

# Conditional creation of Bar plot (time frame)
col2.subheader('Bar plot of % Price Change')

if percent_timeframe == '7d':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_7d'])
    col2.write('*7 days period*')
    plt.figure(figsize=(10,5))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['percent_change_7d'].plot(kind='bar', color=df_change.positive_percent_change_7d.map({True: 'g', False: 'r'}))
    col2.pyplot(plt)
elif percent_timeframe == '24h':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_24h'])
    col2.write('*24 hour period*')
    plt.figure(figsize=(10,5))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['percent_change_24h'].plot(kind='bar', color=df_change.positive_percent_change_24h.map({True: 'g', False: 'r'}))
    col2.pyplot(plt)
else:
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_1h'])
    col2.write('*1 hour period*')
    plt.figure(figsize=(10,5))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['percent_change_1h'].plot(kind='bar', color=df_change.positive_percent_change_1h.map({True: 'g', False: 'r'}))
    col2.pyplot(plt)