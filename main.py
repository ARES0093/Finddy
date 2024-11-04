import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Set page configuration
st.set_page_config(page_title="Finddy Stock Analyzer", layout="centered")

# Improved CSS styling for a more aesthetic appearance
st.markdown("""
    <style>
        /* Background color */
        body {
            background-color: #f0f2f6;
        }

        /* Title styling */
        h1, h2, h3 {
            color: #343a40;
            text-align: center;
            font-family: 'Arial Black', sans-serif;
            margin-bottom: 15px;
        }

        /* Input field styling */
        .centered-input {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 10px 0;
        }

        .stTextInput>div>input {
            background-color: #ffffff;
            color: #495057;
            padding: 10px;
            font-size: 18px;
            border-radius: 8px;
            border: 1px solid #ced4da;
            width: 100%;
        }

        /* Styling for the sidebar */
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }

        /* Stock price output with a card-like style */
        .result-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
            color: #343a40;
            font-size: 18px;
            text-align: center;
        }

        /* History box styling */
        .history-box {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            font-size: 16px;
            color: #343a40;
        }

        /* Center the image (stock price graph) */
        .center-img {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 80%;
        }

        /* Footer styles */
        footer {
            color: #6c757d;
            font-size: 12px;
            text-align: center;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title('📈 Finddy 😎❤️ - Stock Analysis Assistant')

# Initialize an empty list to store the stock query history
if 'stock_history' not in st.session_state:
    st.session_state['stock_history'] = []

# Create a centered input bar for the stock ticker
with st.container():
    st.markdown('<div class="centered-input">', unsafe_allow_html=True)
    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", value="AAPL").upper()
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar configuration for analysis options
st.sidebar.title("Stock Analyzer Options")
analysis_type = st.sidebar.selectbox(
    "Choose Analysis Type",
    ["Get Stock Price", "Simple Moving Average (SMA)", "Exponential Moving Average (EMA)",
     "Relative Strength Index (RSI)", "Moving Average Convergence Divergence (MACD)", "Plot Stock Price"]
)

# Parameters for moving averages (SMA, EMA)
if analysis_type in ["Simple Moving Average (SMA)", "Exponential Moving Average (EMA)"]:
    window = st.sidebar.slider("Select Moving Average Window (days)", min_value=5, max_value=200, value=50)

# Functions for fetching data and analysis
def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period='1d')
    return str(hist['Close'].iloc[-1])

def get_historical_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period='1y')
    return hist

def calculate_SMA(ticker, window):
    data = get_historical_data(ticker)['Close']
    sma = data.rolling(window=window).mean().iloc[-1]
    return str(sma)

def calculate_EMA(ticker, window):
    data = get_historical_data(ticker)['Close']
    ema = data.ewm(span=window, adjust=False).mean().iloc[-1]
    return str(ema)

def calculate_RSI(ticker):
    data = get_historical_data(ticker)['Close']
    delta = data.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ema_up = up.ewm(com=14 - 1, adjust=False).mean()
    ema_down = down.ewm(com=14 - 1, adjust=False).mean()
    rs = ema_up / ema_down
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    return str(rsi)

def calculate_MACD(ticker):
    data = get_historical_data(ticker)['Close']
    short_ema = data.ewm(span=12, adjust=False).mean()
    long_ema = data.ewm(span=26, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=9, adjust=False).mean()
    macd_histogram = macd - signal
    return f'MACD: {macd.iloc[-1]}, Signal: {signal.iloc[-1]}, Histogram: {macd_histogram.iloc[-1]}'

def plot_stock_price(ticker):
    data = get_historical_data(ticker)
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Close'], label='Close Price', color='#6c5ce7')
    plt.title(f'{ticker} Stock Price Over Last Year')
    plt.xlabel('Date')
    plt.ylabel('Stock Price ($)')
    plt.grid(True)
    plt.savefig('stock_price.png')
    st.image('stock_price.png', use_column_width=True)
    plt.close()

# Display results in a card-style main area
st.header(f"Analysis Results for {ticker}")
result_container = st.empty()

# Results and history storage
if ticker:
    if analysis_type == "Get Stock Price":
        price = get_stock_price(ticker)
        result_container.markdown(f'<div class="result-card">Latest Stock Price for {ticker}: ${price}</div>', unsafe_allow_html=True)
        st.session_state['stock_history'].append(f"{ticker} - Stock Price: ${price}")

    elif analysis_type == "Simple Moving Average (SMA)":
        sma = calculate_SMA(ticker, window)
        result_container.markdown(f'<div class="result-card">SMA for {ticker} over {window} days: {sma}</div>', unsafe_allow_html=True)
        st.session_state['stock_history'].append(f"{ticker} - SMA ({window} days): {sma}")

    elif analysis_type == "Exponential Moving Average (EMA)":
        ema = calculate_EMA(ticker, window)
        result_container.markdown(f'<div class="result-card">EMA for {ticker} over {window} days: {ema}</div>', unsafe_allow_html=True)
        st.session_state['stock_history'].append(f"{ticker} - EMA ({window} days): {ema}")

    elif analysis_type == "Relative Strength Index (RSI)":
        rsi = calculate_RSI(ticker)
        result_container.markdown(f'<div class="result-card">RSI for {ticker}: {rsi}</div>', unsafe_allow_html=True)
        st.session_state['stock_history'].append(f"{ticker} - RSI: {rsi}")

    elif analysis_type == "Moving Average Convergence Divergence (MACD)":
        macd = calculate_MACD(ticker)
        result_container.markdown(f'<div class="result-card">MACD for {ticker}: {macd}</div>', unsafe_allow_html=True)
        st.session_state['stock_history'].append(f"{ticker} - MACD: {macd}")

    elif analysis_type == "Plot Stock Price":
        st.subheader(f"{ticker} Stock Price Over the Last Year")
        plot_stock_price(ticker)

# Display stock query history in the sidebar
st.sidebar.header("Stock Query History")
if st.session_state['stock_history']:
    st.sidebar.markdown('<div class="history-box">', unsafe_allow_html=True)
    for entry in st.session_state['stock_history']:
        st.sidebar.write(entry)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Footer
st.sidebar.markdown("----")
st.sidebar.write("Created with ❤️ by ARES")
