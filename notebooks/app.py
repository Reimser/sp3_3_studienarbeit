import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Config
st.set_page_config(page_title="Reddit Financial Sentiment Dashboard", layout="wide")

# 📥 **Google Drive File IDs**
MERGED_CRYPTO_CSV_ID = "12ugApKWh1cJYONcLanpHND9gIdobh-wA"
CRYPTO_PRICES_CSV_ID = "11k9wiflOkqg2DayEgn7iPqNPHC5Qatht"

# 📌 **Lokale Dateinamen**
MERGED_CRYPTO_CSV = "app.csv"
CRYPTO_PRICES_CSV = "crypto_prices.csv"

# 🔥 **Download CSV (falls nicht lokal vorhanden)**
def download_csv(file_id, output):
    if not os.path.exists(output):
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        try:
            st.info(f"📥 Lade {output} herunter...")
            gdown.download(url, output, quiet=False, fuzzy=True)
        except Exception as e:
            st.error(f"❌ Download fehlgeschlagen: {str(e)}")

download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)
download_csv(CRYPTO_PRICES_CSV_ID, CRYPTO_PRICES_CSV)

# 📌 **CSV-Dateien einlesen**
def load_csv(filepath):
    if not os.path.exists(filepath):
        st.error(f"❌ Datei nicht gefunden: {filepath}")
        return pd.DataFrame()
    return pd.read_csv(filepath, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

df_crypto = load_csv(MERGED_CRYPTO_CSV)
df_prices = load_csv(CRYPTO_PRICES_CSV)

# 🔹 **Fix für `date`-Spalten in beiden DataFrames**
for df in [df_crypto, df_prices]:
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")  # ALLES zu datetime umwandeln
        df.dropna(subset=["date"], inplace=True)  # NaT (NaN-Daten) entfernen

# 📊 **DEBUG: Datentypen ausgeben**
st.write("📊 Datentypen nach Konvertierung:")
st.write("🔹 df_crypto:", df_crypto.dtypes)
st.write("🔹 df_prices:", df_prices.dtypes)

# 📊 **Multi-Tab Navigation**
tab_home, tab_crypto, tab_stocks = st.tabs(["🏠 Home", "📈 Crypto Data", "💹 Stock Data"])

# 🔹 **🏠 HOME (README)**
with tab_home:
    st.title("📊 Reddit Financial Sentiment Dashboard")
    st.markdown("""
        ## 🔍 Project Overview
        This dashboard provides a **data-driven analysis of cryptocurrency sentiment** using **Reddit discussions** and **historical price data** starting from November 2024.

        ### 📊 **Data Sources & Processing**
        - **Reddit Comments & Posts:** Scraped weekly from multiple subreddits using a **custom Reddit scraper**.  
        - **Sentiment Analysis:** Applied **CryptoBERT** for a **bullish-bearish-neutral classification** with confidence scores.  
        - **Historical Price Data:** Collected from **CoinGecko API** for major cryptocurrencies.  
        - **Data Storage:** Merged sentiment and price data is stored and updated weekly in **Google Drive**.

        ### 🔎 **Key Features**
        - **📈 Crypto Sentiment Analysis**  
        - **💹 Stock Market Analysis (Coming Soon)**  

        ---  
        🔥 **Use the navigation tabs above to explore sentiment trends & price dynamics!**
    """)

# 📈 **CRYPTOCURRENCY SENTIMENT DASHBOARD**
with tab_crypto:
    st.title("📊 Crypto Sentiment Dashboard")

    if df_crypto.empty:
        st.warning("⚠️ No Crypto Data Available.")
    else:
        # 🔹 **Meistdiskutierte Kryptowährungen**
        st.subheader("🔥 Top 10 Most Mentioned Cryptos")
        st.bar_chart(df_crypto["crypto"].value_counts().head(10))

        # 🔹 **Sentiment-Verteilung**
        st.subheader("💡 Sentiment Distribution")
        sentiment_distribution = df_crypto.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
        st.bar_chart(sentiment_distribution)

        # 🔹 **Word Count über die Zeit**
        st.subheader("📝 Word Count Over Time")
        selected_cryptos = st.multiselect("🔍 Select Cryptos:", df_crypto["crypto"].unique(), default=df_crypto["crypto"].unique()[:3])

        if selected_cryptos:
            df_wordcount_filtered = df_crypto[df_crypto["crypto"].isin(selected_cryptos)]
            wordcount_per_day = df_wordcount_filtered.groupby(["date", "crypto"]).size().unstack(fill_value=0)
            st.line_chart(wordcount_per_day)

        # 🔹 **Word Count & Preis über die Zeit (Dark Mode)**
        st.subheader("🌑📊 Word Count & Price Over Time")

        selected_crypto_dual = st.selectbox("🔍 Select a Crypto for Word Count & Price:", df_prices["crypto"].unique(), key="price_crypto")

        df_wordcount_filtered = df_crypto[df_crypto["crypto"] == selected_crypto_dual].groupby("date").size().reset_index(name="word_count")
        df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto_dual]

        # **Finaler Fix für Merge**
        df_wordcount_filtered["date"] = pd.to_datetime(df_wordcount_filtered["date"], errors="coerce")
        df_price_filtered["date"] = pd.to_datetime(df_price_filtered["date"], errors="coerce")

        df_combined_dual = df_wordcount_filtered.merge(df_price_filtered, on="date", how="inner")

        # **Zwei-Achsen-Plot: Dark Mode**
        plt.style.use("dark_background")  # Dark Theme aktivieren
        fig, ax1 = plt.subplots(figsize=(10, 5))

        ax1.set_facecolor("#222222")  # Dunkler Hintergrund
        fig.patch.set_facecolor("#222222")  # Rand-Hintergrund

        ax1.set_xlabel("Date", color="white")
        ax1.set_ylabel("Word Count", color="cyan")
        ax1.plot(df_combined_dual["date"], df_combined_dual["word_count"], color="cyan", label="Word Count", alpha=0.8, linewidth=2)
        ax1.tick_params(axis="y", labelcolor="cyan")
        ax1.tick_params(axis="x", colors="white")
        ax1.grid(color="#444444", linestyle="--", linewidth=0.5)

        ax2 = ax1.twinx()
        ax2.set_ylabel("Price (USD)", color="lightcoral")
        ax2.plot(df_combined_dual["date"], df_combined_dual["price"], color="lightcoral", label="Price", alpha=0.8, linewidth=2)
        ax2.tick_params(axis="y", labelcolor="lightcoral")
        ax2.grid(color="#444444", linestyle="--", linewidth=0.5)

        fig.suptitle(f"🌑 Word Count & Price for {selected_crypto_dual} Over Time", color="white")
        fig.tight_layout()

        st.pyplot(fig)

        # 🔹 **Sentiment-Verteilung (nur hohe Confidence)**
        st.subheader("🎯 Sentiment Distribution (High Confidence)")
        CONFIDENCE_THRESHOLD = 0.8
        df_high_conf = df_crypto[
            (df_crypto["sentiment"].isin(["bullish", "bearish"])) & 
            (df_crypto["sentiment_confidence"] >= CONFIDENCE_THRESHOLD)
        ]
        sentiment_dist_high_conf = df_high_conf.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
        st.bar_chart(sentiment_dist_high_conf)

        # 🔹 **Sentiment-Trend über die Zeit (Hohe Confidence)**
        st.subheader("📅 High-Confidence Sentiment Trend Over Time")
        selected_crypto = st.selectbox("🔍 Select a Cryptocurrency:", df_crypto["crypto"].unique(), key="sentiment_crypto_high_conf")
        df_filtered_high_conf = df_high_conf[df_high_conf["crypto"] == selected_crypto]

        if df_filtered_high_conf.empty:
            st.warning("⚠️ No high-confidence sentiment data available.")
        else:
            df_time_high_conf = df_filtered_high_conf.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
            st.line_chart(df_time_high_conf)

        # 🔹 **High-Confidence Sentiment & Price Over Time**
        st.subheader("📊 High-Confidence Sentiment & Price Over Time")
        selected_crypto_sentiment_price = st.selectbox("🔍 Select a Crypto:", df_prices["crypto"].unique(), key="sentiment_price_dual")
        df_sentiment_high_conf_filtered = df_high_conf[df_high_conf["crypto"] == selected_crypto_sentiment_price].groupby(["date", "sentiment"]).size().unstack(fill_value=0).reset_index()
        df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto_sentiment_price]

        df_combined_sentiment_price = df_sentiment_high_conf_filtered.merge(df_price_filtered, on="date", how="inner")

        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax1.set_xlabel("Date")
        ax1.set_ylabel("High-Confidence Sentiment Count", color="blue")
        ax1.plot(df_combined_sentiment_price["date"], df_combined_sentiment_price.get("bullish", 0), color="green", label="Bullish", alpha=0.7)
        ax1.plot(df_combined_sentiment_price["date"], df_combined_sentiment_price.get("bearish", 0), color="red", label="Bearish", alpha=0.7)
        ax1.tick_params(axis="y", labelcolor="blue")

        ax2 = ax1.twinx()
        ax2.set_ylabel("Price (USD)", color="white")
        ax2.plot(df_combined_sentiment_price["date"], df_combined_sentiment_price["price"], color="white", label="Price", linewidth=2)
        ax2.tick_params(axis="y", labelcolor="white")

        fig.suptitle(f"High-Confidence Sentiment & Price for {selected_crypto_sentiment_price}")
        fig.tight_layout()
        st.pyplot(fig)

# 🔹 **💹 STOCK MARKET ANALYSIS**
with tab_stocks:
    st.title("💹 Stock Market Analysis (Coming Soon)")
    st.warning("🚧 This section is under development. Stock data will be integrated soon!")
