import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Financial Data Dashboard", layout="centered")

# 📌 Google Drive Direct Links (Replace with your File IDs)
MERGED_CRYPTO_CSV_ID = "102W-f_u58Jvx9xBAv4IaYrOY6txk-XKL"
MERGED_STOCK_CSV_ID = "YOUR-STOCK-DATA-FILE-ID"

# 📌 Local File Paths for Downloaded CSVs
MERGED_CRYPTO_CSV = "reddit_merged_crypto.csv"
MERGED_STOCK_CSV = "stock_data.csv"

# 🔹 Function to Download CSV from Google Drive
@st.cache_data
def download_csv(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output, quiet=False)

# 🔹 Function to Load Data
@st.cache_data
def load_data():
    # 🔹 Load Crypto Data
    if not os.path.exists(MERGED_CRYPTO_CSV):
        download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)
    df_crypto = pd.read_csv(MERGED_CRYPTO_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # 🔹 Load Stock Data
    if not os.path.exists(MERGED_STOCK_CSV):
        download_csv(MERGED_STOCK_CSV_ID, MERGED_STOCK_CSV)
    df_stock = pd.read_csv(MERGED_STOCK_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    return df_crypto, df_stock

# 📌 Load Data
df_crypto, df_stock = load_data()

# 📊 **Multi-Tab Navigation**
tab_home, tab_crypto, tab_stocks = st.tabs(["🏠 Home", "📈 Crypto Data", "💹 Stock Data"])

# 🔹 **🏠 HOME (README)**
with tab_home:
    st.title("📊 Reims Crypto Scraper!")
    st.markdown("""
        **This dashboard provides insights into financial data on Reddit:**
        - 📈 **Cryptocurrencies:** Sentiment Analysis, Activity & Trends  
        - 💹 **Stock Market:** Price Trends, Volatility & Market Analysis  
        
        Use the tabs to explore different datasets!  
        """)

# 🔹 **📈 CRYPTOCURRENCY ANALYSIS**
with tab_crypto:
    st.title("📈 Crypto Sentiment Dashboard")

    if df_crypto.empty:
        st.warning("⚠️ No Crypto Data Available.")
    else:
        st.subheader("🔥 Top 10 Most Mentioned Cryptocurrencies")
        crypto_counts = df_crypto["crypto"].value_counts().head(10)
        st.bar_chart(crypto_counts)

        st.subheader("💡 Sentiment Distribution of Cryptos")
        sentiment_distribution = df_crypto.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
        st.bar_chart(sentiment_distribution)

        st.subheader("📅 Sentiment Trend Over Time")
        crypto_options = df_crypto["crypto"].unique().tolist()
        selected_crypto = st.selectbox("Choose a Cryptocurrency:", crypto_options, index=0)
        
        df_filtered = df_crypto[(df_crypto["crypto"] == selected_crypto) & (df_crypto["sentiment"] != "neutral")]
        df_time = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)

        st.line_chart(df_time)

# 🔹 **💹 STOCK MARKET ANALYSIS**
with tab_stocks:
    st.title("💹 Stock Market Analysis")

    if df_stock.empty:
        st.warning("⚠️ No Stock Data Available.")
    else:
        st.subheader("📊 Top Performing Stocks")
        stock_counts = df_stock["stock"].value_counts().head(10)
        st.bar_chart(stock_counts)

        st.subheader("📈 Stock Price Trends")
        stock_options = df_stock["stock"].unique().tolist()
        selected_stock = st.selectbox("Choose a Stock:", stock_options, index=0)
        
        df_stock_filtered = df_stock[df_stock["stock"] == selected_stock]
        df_price_time = df_stock_filtered.groupby(["date"])["price"].mean()

        st.line_chart(df_price_time)

    st.write("🔄 Dashboard is regularly updated with new data!")
