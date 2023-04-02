import streamlit as st
import yahooquery as yf
import plotly.express as pe
import pandas as pd
import datetime
from stocknews import StockNews
import zmq

# Header information
st.title('Stock Information Dashboard')
st.info('This app is used to display information on a stock. You can gather \
        more information on a stock by selecting their symbol, start date, \
        and end date. More information is displayed in the tabs Stock Company \
        Info, Stock Data, and Stock News.')

# Connects to ZeroMQ pipeline and sends a request to partner's microservice
context = zmq.Context()
print("Connecting to server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:3001")
print("Sending request…")
socket.send(b"Hello")
message = socket.recv()
csv_file = message.decode()
ticker_list = pd.read_csv(csv_file)
print('Csv file received...')

# Sidebar
st.sidebar.header('Stock Selection')
ticker = st.sidebar.selectbox('Ticker', ticker_list)
start_date = st.sidebar.date_input('Start Date', datetime.date(2022, 1, 1))
end_date = st.sidebar.date_input('End Date')
st.sidebar.info('Please select a stock ticker symbol from the dropdown menu \
                and the start and end date to get information on the stock.')
ticker_symbol = yf.Ticker(ticker)
ticker_history = ticker_symbol.history(period='1d', start=start_date,
                                       end=end_date)

# Pages
stock_info, ticker_data, news = st.tabs(['Stock Company Info',
                                         'Stock Data', 'Stock News'])

# Information in the individual pages
with stock_info:
    string_name = ticker_symbol.quotes[ticker]['longName']
    st.header(string_name)
    string_summary = ticker_symbol.asset_profile[ticker]['longBusinessSummary']
    st.info(string_summary)

with ticker_data:
    data = ticker_symbol.history(start=start_date, end=end_date)
    updated_data = data.reset_index()
    line_chart = pe.line(updated_data, x=updated_data['date'],
                         y=updated_data['adjclose'], title=ticker)
    st.plotly_chart(line_chart)
    st.header('Ticker Data')
    st.write(ticker_history)

    # Seperator
    st.write('---------------------------------------')

    st.info("If you want to see more info expand the tabs below")
    with st.expander("Financial Statements"):
        balance_sheet = ticker_symbol.balance_sheet()
        income_statement = ticker_symbol.income_statement()
        cash_flow = ticker_symbol.cash_flow()
        st.header('Yearly Balance Sheet')
        st.write(balance_sheet)
        st.header('Yearly Income Statement')
        st.write(income_statement)
        st.header('Yearly Cash Flow Statement')
        st.write(cash_flow)

    with st.expander("Quarterly Valuation Report"):
        valuations = ticker_symbol.valuation_measures
        st.header('Quarterly Valuations')
        st.write(valuations)


with news:
    st.header(f'News of {ticker}')
    stock_news = StockNews(ticker, save_news=False)
    parsed_news = stock_news.read_rss()
    for i in range(5):
        articles = st.subheader(f'Articles {i+1}')
        st.write(parsed_news['published'][i])
        st.write(parsed_news['title'][i])
        st.write(parsed_news['summary'][i])
