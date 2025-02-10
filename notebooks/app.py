import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Financial Data Dashboard", layout="centered")

# 📌 Google Drive File ID for the latest dataset
MERGED_CRYPTO_CSV_ID = "10Ft5DpBI-B3tBfU5wOVzGRj_vwT7TNxa"
MERGED_STOCK_CSV_ID = "STOCK_FILE_ID"  # Replace when stock data is available

# 📌 Local filenames
MERGED_CRYPTO_CSV = "reddit_merged_crypto.csv"
MERGED_STOCK_CSV = "stock_data.csv"

# 🔹 Function to Download CSV from Google Drive
@st.cache_data
def download_csv(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output, quiet=False)

# 🔹 Function to Load Crypto Data
@st.cache_data
def load_crypto_data():
    if not os.path.exists(MERGED_CRYPTO_CSV):
        download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)

    df_crypto = pd.read_csv(MERGED_CRYPTO_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # 🔹 Keep both date columns
    if "date_x" in df_crypto.columns:
        df_crypto["comment_date"] = pd.to_datetime(df_crypto["date_x"], errors="coerce")
    else:
        raise KeyError(f"⚠️ No valid 'date_x' column found! Available columns: {df_crypto.columns.tolist()}")

    if "date_y" in df_crypto.columns:
        df_crypto["post_date"] = pd.to_datetime(df_crypto["date_y"], errors="coerce")
    else:
        raise KeyError(f"⚠️ No valid 'date_y' column found! Available columns: {df_crypto.columns.tolist()}")

    # Convert Sentiment Labels into Numeric Scores
    df_crypto["sentiment_score"] = df_crypto["sentiment"].map({"bullish": 1, "neutral": 0, "bearish": -1})

    return df_crypto

# 🔹 Function to Load Stock Data (Placeholder)
@st.cache_data
def load_stock_data():
    return pd.DataFrame()  # Placeholder: No stock data yet

# 📌 Load Data
df_crypto = load_crypto_data()
df_stock = load_stock_data()

# 📊 **Multi-Tab Navigation**
tab_home, tab_crypto, tab_stocks = st.tabs(["🏠 Home", "📈 Crypto Data", "💹 Stock Data"])

# 🔹 **🏠 HOME (README)**
with tab_home:
    st.title("📊 Financial Sentiment Dashboard")
    st.markdown("""
        **This dashboard provides insights into financial sentiment trends using Reddit discussions.**
        
        - **📈 Crypto Data:** Sentiment Analysis, Activity & Trends  
        - **💹 Stock Market Data (Coming Soon)**  

        🔄 **Data is regularly updated to reflect the latest trends.**
    """)

    # 🔄 **Refresh Button**
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.experimental_rerun()

# 🔹 **📈 CRYPTOCURRENCY ANALYSIS**
with tab_crypto:
    st.title("📈 Crypto Sentiment Dashboard")

    if df_crypto.empty:
        st.warning("⚠️ No Crypto Data Available.")
    else:
        # 🔹 **1️⃣ Most Discussed Cryptos**
        st.subheader("🔥 Top 10 Most Mentioned Cryptocurrencies")
        crypto_counts = df_crypto["crypto"].value_counts().head(10)
        st.bar_chart(crypto_counts)

        # 🔹 **2️⃣ Sentiment Distribution per Crypto**
        st.subheader("💡 Sentiment Distribution of Cryptos")
        sentiment_distribution = df_crypto.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
        st.bar_chart(sentiment_distribution)

        # 🔹 **3️⃣ Sentiment Trend Over Time (Based on Comments)**
        st.subheader("📅 Sentiment Trend Over Time (Comments)")
        crypto_options = df_crypto["crypto"].unique().tolist()
        selected_crypto = st.selectbox("Choose a Cryptocurrency:", crypto_options, index=0)

        df_filtered = df_crypto[(df_crypto["crypto"] == selected_crypto) & (df_crypto["sentiment"] != "neutral")]

        if df_filtered.empty:
            st.warning("⚠️ No sentiment data available for the selected cryptocurrency.")
        else:
            df_time = df_filtered.groupby(["comment_date", "sentiment"]).size().unstack(fill_value=0)
            st.line_chart(df_time)

        # 🔹 **6️⃣ Sentiment Heatmap of Top Cryptos**
        st.subheader("🌡️ Sentiment Heatmap of Top Cryptos")
        sentiment_counts = df_crypto[df_crypto["sentiment"] != "neutral"].groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(sentiment_counts, annot=True, fmt="d", cmap="RdYlGn", linewidths=0.5, ax=ax)
        st.pyplot(fig)

        # 🔹 **7️⃣ Average Sentiment Score per Crypto**
        st.subheader("📊 Average Sentiment Score per Crypto")
        avg_sentiment = df_crypto.groupby("crypto")["sentiment_score"].mean().sort_values()

        fig, ax = plt.subplots(figsize=(10, 5))
        avg_sentiment.plot(kind="bar", color=["red" if x < 0 else "green" for x in avg_sentiment], ax=ax)
        ax.set_ylabel("Average Sentiment Score")
        st.pyplot(fig)

        # 🔹 **8️⃣ Sentiment Volatility per Crypto**
        st.subheader("📉 Sentiment Volatility per Crypto")
        sentiment_std = df_crypto.groupby("crypto")["sentiment_score"].std().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(10, 5))
        sentiment_std.plot(kind="bar", color="blue", ax=ax)
        ax.set_ylabel("Sentiment Standard Deviation")
        st.pyplot(fig)

        # 🔹 **9️⃣ Multi-Selection Activity Over Time**
        st.subheader("📅 Multi-Selection Activity Over Time")
        selected_cryptos = st.multiselect("Choose one or more Cryptocurrencies:", crypto_options, default=crypto_options[:3])

        if selected_cryptos:
            df_activity_filtered = df_crypto[df_crypto["crypto"].isin(selected_cryptos)]
            activity_per_day = df_activity_filtered.groupby(["comment_date", "crypto"]).size().unstack(fill_value=0)
            st.line_chart(activity_per_day)

# 🔹 **💹 STOCK MARKET ANALYSIS**
with tab_stocks:
    st.title("💹 Stock Market Analysis (Coming Soon)")
    st.warning("🚧 This section is under development. Stock data will be integrated soon!")

