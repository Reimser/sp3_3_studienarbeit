import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Financial Data Dashboard", layout="centered")

# 📌 Google Drive Direct Links (Replace with your File ID for Crypto Data)
MERGED_CRYPTO_CSV_ID = "102W-f_u58Jvx9xBAv4IaYrOY6txk-XKL"

# 📌 Local File Paths for Downloaded CSVs
MERGED_CRYPTO_CSV = "reddit_merged_crypto.csv"

# 🔹 Function to Download CSV from Google Drive
@st.cache_data
def download_csv(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output, quiet=False)

# 🔹 Function to Load Data
@st.cache_data
def load_crypto_data():
    # 🔹 Load Crypto Data
    if not os.path.exists(MERGED_CRYPTO_CSV):
        download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)

    df_crypto = pd.read_csv(MERGED_CRYPTO_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # 🔹 Ensure "date" column exists
    if "date" not in df_crypto.columns:
        if "date_x" in df_crypto.columns:
            df_crypto["date"] = df_crypto["date_x"]
        elif "date_y" in df_crypto.columns:
            df_crypto["date"] = df_crypto["date_y"]
        else:
            raise KeyError("⚠️ No valid 'date' column found! Check the CSV.")

    df_crypto["date"] = pd.to_datetime(df_crypto["date"], errors="coerce")

    # 🔹 Convert Sentiment to Numerical Values
    sentiment_mapping = {"positive": 1, "neutral": 0, "negative": -1, "bullish": 1, "bearish": -1}
    df_crypto["sentiment_score"] = df_crypto["sentiment"].map(sentiment_mapping).fillna(0)

    return df_crypto

# 📌 Load Crypto Data
df_crypto = load_crypto_data()

# 📊 **Multi-Tab Navigation**
tab_home, tab_crypto, tab_stocks = st.tabs(["🏠 Home", "📈 Crypto Data", "💹 Stock Data"])

# 🔹 **🏠 HOME (README)**
with tab_home:
    st.title("📊 Reims Financial Dashboard")
    st.markdown("""
        **This dashboard provides insights into financial data on Reddit:**
        - 📈 **Cryptocurrencies:** Sentiment Analysis, Activity & Trends  
        - 💹 **Stock Market:** (Coming Soon)  
        
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

        if "date" in df_filtered.columns:
            df_time = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
            st.line_chart(df_time)
        else:
            st.error("⚠️ 'date' column is missing, check data processing.")

# 🔹 **💹 STOCK MARKET ANALYSIS (Coming Soon)**
with tab_stocks:
    st.title("💹 Stock Market Analysis")
    st.subheader("🚧 This section is under construction. 🚧")
    st.markdown("""
        The stock market analysis feature is currently in development.  
        Stay tuned for future updates! 📈
        """)
