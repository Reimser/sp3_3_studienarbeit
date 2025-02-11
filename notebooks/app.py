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

        # **Word Count Over Time**
        st.subheader("📝 Word Count Evolution Over Time")

        # Multi-Select für mehrere Kryptowährungen
        selected_cryptos_wordcount = st.multiselect(
            "Choose Cryptos to Compare Word Frequency:",
            df_crypto["crypto"].unique().tolist(),
            default=df_crypto["crypto"].unique()[:3]
        )

    if selected_cryptos_wordcount:
        df_wordcount_filtered = df_crypto[df_crypto["crypto"].isin(selected_cryptos_wordcount)]
        wordcount_per_day = df_wordcount_filtered.groupby(["comment_date", "crypto"]).size().unstack(fill_value=0)
        st.line_chart(wordcount_per_day)


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
        # 📊 **2️⃣ Word Count & Price Over Time**
        st.subheader("📊 Word Count & Price Over Time")

        # Auswahl einer Kryptowährung für die kombinierte Analyse
        selected_crypto_dual = st.selectbox("Choose a Cryptocurrency for Word Count & Price:", df_prices["crypto"].unique(), key="dual_axis_crypto")

        # Daten für die gewählte Krypto filtern
        df_wordcount_filtered = df_crypto[df_crypto["crypto"] == selected_crypto_dual].groupby("comment_date").size().reset_index(name="word_count")
        df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto_dual]

        # Sicherstellen, dass beide DataFrames die gleiche Zeitachse haben
        df_combined_dual = df_wordcount_filtered.merge(df_price_filtered, left_on="comment_date", right_on="date", how="inner")

        # Visualisierung mit zwei Y-Achsen
        fig, ax1 = plt.subplots(figsize=(10, 5))

        # Word Count auf linker Achse
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Word Count", color="blue")
        ax1.plot(df_combined_dual["comment_date"], df_combined_dual["word_count"], color="blue", label="Word Count", alpha=0.7)
        ax1.tick_params(axis="y", labelcolor="blue")

        # Preis auf rechter Achse
        ax2 = ax1.twinx()
        ax2.set_ylabel("Price (USD)", color="red")
        ax2.plot(df_combined_dual["comment_date"], df_combined_dual["price"], color="red", label="Price", alpha=0.7)
        ax2.tick_params(axis="y", labelcolor="red")

        # Titel und Legende
        fig.suptitle(f"Word Count & Price for {selected_crypto_dual} Over Time")
        fig.tight_layout()
        st.pyplot(fig)

        # 🔹 **📊 Price Change vs. Extreme Sentiment**
        st.subheader("📈 Price Movement for Extreme Sentiment Days")

        # Berechnung der 3-Tages-Preisänderung
        df_prices["price_change_3d"] = df_prices.groupby("crypto")["price"].pct_change(periods=3)

        # Kombination mit Sentiment-Daten
        df_combined = df_crypto.merge(df_prices, left_on=["comment_date", "crypto"], right_on=["date", "crypto"], how="inner")

        # Berechnung der Sentiment-Perzentile
        lower_threshold = df_combined["sentiment_score"].quantile(0.1)  # Unterste 10%
        upper_threshold = df_combined["sentiment_score"].quantile(0.9)  # Oberste 10%

        # Auswahl nur extremer Sentiment-Werte
        df_extreme_sentiment = df_combined[
            (df_combined["sentiment_score"] <= lower_threshold) | (df_combined["sentiment_score"] >= upper_threshold)
        ]

        # Gruppieren nach Crypto & Sentiment für den Mittelwert der 3-Tages-Preisveränderung
        df_sentiment_price_change = df_extreme_sentiment.groupby(["crypto", "sentiment"])["price_change_3d"].mean().unstack()

        # Heatmap-Visualisierung
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(df_sentiment_price_change * 100, annot=True, fmt=".2f%%", cmap="RdYlGn", linewidths=0.5, ax=ax)
        ax.set_title("Average 3-Day Price Change Based on Extreme Sentiment")
        ax.set_xlabel("Sentiment Type")
        ax.set_ylabel("Cryptocurrency")
        
        st.pyplot(fig)

# 🔹 **💹 STOCK MARKET ANALYSIS**
with tab_stocks:
    st.title("💹 Stock Market Analysis (Coming Soon)")
    st.warning("🚧 This section is under development. Stock data will be integrated soon!")
