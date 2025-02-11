import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Reims-Reddit Financial Data Dashboard", layout="centered")

# 📌 Google Drive File IDs for datasets
MERGED_CRYPTO_CSV_ID = "10Ft5DpBI-B3tBfU5wOVzGRj_vwT7TNxa"
CRYPTO_PRICES_CSV_ID = "10mB8tM6s6HOW8Mvd8-0xr3_i_sDTyovL"

# 📌 Local filenames
MERGED_CRYPTO_CSV = "reddit_merged.csv"
CRYPTO_PRICES_CSV = "crypto_prices.csv"

# 🔹 Function to Download CSV from Google Drive
@st.cache_data
def download_csv(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output, quiet=False)

# 🔹 Function to Load Crypto Sentiment Data
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

# 🔹 Function to Load Crypto Prices Data
@st.cache_data
def load_crypto_prices():
    if not os.path.exists(CRYPTO_PRICES_CSV):
        download_csv(CRYPTO_PRICES_CSV_ID, CRYPTO_PRICES_CSV)

    df_prices = pd.read_csv(CRYPTO_PRICES_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # Debugging: Print available columns
    print("📝 Columns in df_prices:", df_prices.columns.tolist())

    # Ensure no hidden spaces in column names
    df_prices.columns = df_prices.columns.str.strip()

    # Convert date column to datetime format
    if "date" in df_prices.columns:
        df_prices["date"] = pd.to_datetime(df_prices["date"], errors="coerce")
    else:
        raise KeyError(f"⚠️ 'date' column missing! Available columns: {df_prices.columns.tolist()}")

    return df_prices

# 📌 Load Data
df_crypto = load_crypto_data()
df_prices = load_crypto_prices()

# 📊 **Multi-Tab Navigation**
tab_home, tab_crypto, tab_prices, tab_stocks = st.tabs(["🏠 Home", "📈 Crypto Data", "💰 Crypto Prices", "💹 Stock Data"])

# 🔹 **🏠 HOME (README)**
with tab_home:
    st.title("📊 Financial Sentiment Dashboard")
    st.markdown("""
        **This dashboard provides insights into financial sentiment trends using Reddit discussions.**
        
        - **📈 Crypto Data:** Sentiment Analysis, Activity & Trends  
        - **💰 Crypto Prices:** Historical trends & correlation with sentiment  
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
        
        st.subheader(f"📈 Smoothed Sentiment Trend for {selected_crypto}")
        ##
        st.subheader("📝 Word Count Evolution Over Time")

        # Multi-Select für mehrere Kryptowährungen
        selected_cryptos_wordcount = st.multiselect(
            "Choose Cryptos to Compare Word Frequency:",
            crypto_options,
            default=crypto_options[:3]
        )

        if selected_cryptos_wordcount:
            # 🔹 Filtere die Daten nach den ausgewählten Kryptowährungen
            df_wordcount_filtered = df_crypto[df_crypto["crypto"].isin(selected_cryptos_wordcount)]

            # 🔹 Aggregiere den Word Count pro Tag für jede Krypto
            wordcount_per_day = df_wordcount_filtered.groupby(["comment_date", "crypto"]).size().unstack(fill_value=0)

            # 🔹 Visualisierung als Liniendiagramm
            st.line_chart(wordcount_per_day)

        ##
        df_sentiment_score = df_crypto[df_crypto["crypto"] == selected_crypto].groupby("comment_date")["sentiment_score"].mean()
        df_sentiment_score_ma = df_sentiment_score.rolling(window=7).mean()  # 7-Tage-Durchschnitt

        fig, ax = plt.subplots(figsize=(8, 4))
        df_sentiment_score.plot(ax=ax, label="Daily Sentiment Score", alpha=0.5)
        df_sentiment_score_ma.plot(ax=ax, label="7-Day Moving Avg", linewidth=2, color="red")
        ax.legend()
        st.pyplot(fig)


        # 🔹 Wordcount per Crypto Over Time
        st.subheader("📊 Wordcount per Crypto Over Time")
        df_wordcount = df_crypto.groupby(["comment_date", "crypto"]).size().unstack(fill_value=0)
        st.line_chart(df_wordcount)


        # 🔹 **3️⃣ Sentiment Trend Over Time (Based on Comments)**
        st.subheader("📅 Sentiment Trend Over Time (Comments)")
        crypto_options = df_crypto["crypto"].unique().tolist()
        selected_crypto = st.selectbox("Choose a Cryptocurrency for Sentiment:", crypto_options, index=0, key="sentiment_crypto")


        df_filtered = df_crypto[(df_crypto["crypto"] == selected_crypto) & (df_crypto["sentiment"] != "neutral")]

        if df_filtered.empty:
            st.warning("⚠️ No sentiment data available for the selected cryptocurrency.")
        else:
            df_time = df_filtered.groupby(["comment_date", "sentiment"]).size().unstack(fill_value=0)
            st.line_chart(df_time)

# 🔹 **💰 CRYPTO PRICE ANALYSIS**
with tab_prices:
    st.title("💰 Crypto Prices & Sentiment Impact")

    if df_prices.empty:
        st.warning("⚠️ No Crypto Price Data Available.")
    else:
        st.subheader("📈 Historical Crypto Prices")
        selected_price_crypto = st.selectbox("Choose a Cryptocurrency for Price Data:", df_prices["crypto"].unique(), key="price_crypto")

        df_price_filtered = df_prices[df_prices["crypto"] == selected_price_crypto]
        st.line_chart(df_price_filtered.set_index("date")["price"])

        st.subheader("📊 Correlation Between Sentiment & Prices")
        df_combined = df_crypto.merge(df_prices, left_on=["comment_date", "crypto"], right_on=["date", "crypto"], how="inner")

        correlation_matrix = df_combined[["sentiment_score", "price"]].corr()

        fig, ax = plt.subplots(figsize=(6, 4))
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

        st.subheader("📊 Sentiment Influence on Daily Price Changes")
        df_combined["price_change"] = df_combined.groupby("crypto")["price"].pct_change()
        sentiment_effect = df_combined.groupby("sentiment")["price_change"].mean()

        fig, ax = plt.subplots(figsize=(8, 5))
        sentiment_effect.plot(kind="bar", color=["red", "gray", "green"], ax=ax)
        ax.set_ylabel("Avg. Daily Price Change (%)")
        st.pyplot(fig)

# 🔹 **💹 STOCK MARKET ANALYSIS**
with tab_stocks:
    st.title("💹 Stock Market Analysis (Coming Soon)")
    st.warning("🚧 This section is under development. Stock data will be integrated soon!")
