import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Reddit Crypto Dashboard", layout="wide")

# 📥 **Google Drive File IDs**
MERGED_CRYPTO_CSV_ID = "12ugApKWh1cJYONcLanpHND9gIdobh-wA"
CRYPTO_PRICES_CSV_ID = "11k9wiflOkqg2DayEgn7iPqNPHC5Qatht"

# 📌 **Lokale Dateinamen**
MERGED_CRYPTO_CSV = "app.csv"
CRYPTO_PRICES_CSV = "crypto_prices.csv"

# 🔥 **Daten herunterladen**
def download_csv(file_id, output):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        gdown.download(url, output, quiet=False, fuzzy=True)  # ✅ Alternative Download-Methode
        if not os.path.exists(output) or os.path.getsize(output) == 0:
            st.error(f"❌ Fehler: {output} wurde nicht korrekt heruntergeladen!")
    except Exception as e:
        st.error(f"❌ Download fehlgeschlagen: {str(e)}")

# 📥 **Daten laden**
download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)
download_csv(CRYPTO_PRICES_CSV_ID, CRYPTO_PRICES_CSV)

# 📌 **CSV-Dateien einlesen**
def load_csv(filepath):
    if not os.path.exists(filepath):
        st.error(f"❌ Datei nicht gefunden: {filepath}")
        return pd.DataFrame()
    try:
        return pd.read_csv(filepath, sep="|", encoding="utf-8-sig", on_bad_lines="skip")
    except Exception as e:
        st.error(f"❌ Fehler beim Laden von {filepath}: {str(e)}")
        return pd.DataFrame()

df_crypto = load_csv(MERGED_CRYPTO_CSV)
df_prices = load_csv(CRYPTO_PRICES_CSV)

# 📌 **Debugging: Dateiinhalt prüfen**
if df_crypto.empty:
    st.error("❌ Die CSV-Datei ist leer oder fehlerhaft!")

st.write("✅ CSV-Datei erfolgreich geladen:")
st.write(df_crypto.head())

# 🔹 Datentypen korrigieren
df_crypto["date"] = pd.to_datetime(df_crypto["date"], format="%Y-%m-%d", errors="coerce")
df_crypto["crypto"] = df_crypto["crypto"].astype(str)
df_crypto["sentiment"] = df_crypto["sentiment"].astype(str)

# 🔍 Debugging: Dtypes prüfen
print(df_crypto.dtypes)
print(df_crypto.head())


# 📊 **Multi-Tab Navigation mit Kategorien**
tab_home, tab_top, tab_new = st.tabs([
    "🏠 Home", "🏆 Top Coins", "📈 New Coins"
])

# 🔹 **🏠 HOME (README)**
with tab_home:
    st.title("📊 Reddit Crypto Sentiment Dashboard")
    st.markdown("""
        ## 🔍 Project Overview
        This dashboard provides a **data-driven analysis of cryptocurrency sentiment** using **Reddit discussions** and **historical price data**.

        ### 🔎 **Key Features**
        - **📈 Crypto Sentiment Analysis:**  
          - Top mentioned cryptocurrencies & sentiment distribution  
          - Sentiment trends over time (overall & high-confidence)  
          - Combined analysis of sentiment & price dynamics    

        🔥 **Use the navigation tabs above to explore sentiment trends & price dynamics!**
    """)

# 📊 **Funktion für die Tabs mit mehreren individuellen Krypto-Auswahlen**
def crypto_analysis_tab(tab, category, crypto_list):
    with tab:
        st.title(f"{category} Sentiment & Mentions")

        # 🔹 Debugging: Alle verfügbaren Kryptowährungen im Datensatz anzeigen
        available_cryptos = df_crypto["crypto"].dropna().unique().tolist()
        print(f"🔍 Verfügbare Kryptowährungen im Datensatz: {available_cryptos}")

        # 🔹 **1️⃣ Most Discussed Cryptos**
        st.subheader("🔥 Top 10 Most Mentioned Cryptocurrencies")
        selected_crypto_mentions = st.selectbox(
            "Choose a Coin for Mentions Analysis:", crypto_list, key=f"{category.lower()}_mentions"
        )
        df_filtered_mentions = df_crypto[df_crypto["crypto"].str.lower() == selected_crypto_mentions.lower()]
        
        if not df_filtered_mentions.empty:
            crypto_counts = df_filtered_mentions["crypto"].value_counts().head(10)
            st.bar_chart(crypto_counts)
        else:
            st.warning("⚠️ No data available for this selection.")

        # 🔹 **2️⃣ Sentiment Distribution per Crypto**
        st.subheader("💡 Sentiment Distribution")
        selected_crypto_sentiment = st.selectbox(
            "Choose a Coin for Sentiment Distribution:", crypto_list, key=f"{category.lower()}_sentiment"
        )
        df_filtered_sentiment = df_crypto[df_crypto["crypto"].str.lower() == selected_crypto_sentiment.lower()]
        
        if not df_filtered_sentiment.empty:
            sentiment_distribution = df_filtered_sentiment["sentiment"].value_counts()
            st.bar_chart(sentiment_distribution)
        else:
            st.warning("⚠️ No data available for this selection.")

        # 🔹 **3️⃣ Word Count Over Time**
        st.subheader("📝 Word Count Evolution Over Time")
        selected_crypto_wordcount = st.selectbox(
            "Choose a Coin for Word Count Trend:", crypto_list, key=f"{category.lower()}_wordcount"
        )
        df_filtered_wordcount = df_crypto[df_crypto["crypto"].str.lower() == selected_crypto_wordcount.lower()]
        
        if not df_filtered_wordcount.empty:
            wordcount_per_day = df_filtered_wordcount.groupby("date").size()
            st.line_chart(wordcount_per_day)
        else:
            st.warning("⚠️ No data available for this selection.")

        # 🔹 **4️⃣ Sentiment Trend Over Time**
        st.subheader("📅 Sentiment Trend Over Time")
        selected_crypto_trend = st.selectbox(
            "Choose a Coin for Sentiment Trend:", crypto_list, key=f"{category.lower()}_trend"
        )
        df_filtered_trend = df_crypto[df_crypto["crypto"].str.lower() == selected_crypto_trend.lower()]
        
        if not df_filtered_trend.empty:
            sentiment_trend = df_filtered_trend.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
            st.line_chart(sentiment_trend)
        else:
            st.warning("⚠️ No data available for this selection.")

        # 🔹 **5️⃣ Word Count & Price Over Time**
        st.subheader("📊 Word Count & Price Over Time")
        selected_crypto_price = st.selectbox(
            "Choose a Coin for Word Count & Price Trend:", crypto_list, key=f"{category.lower()}_price"
        )
        
        if selected_crypto_price in df_prices["crypto"].values:
            df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto_price]
            df_combined_dual = df_filtered_wordcount.groupby("date").size().reset_index(name="word_count")
            df_combined_dual = df_combined_dual.merge(df_price_filtered, on="date", how="inner")

            fig, ax1 = plt.subplots(figsize=(10, 5))
            ax1.set_xlabel("Date")
            ax1.set_ylabel("Word Count", color="blue")
            ax1.plot(df_combined_dual["date"], df_combined_dual["word_count"], color="blue", label="Word Count")
            ax1.tick_params(axis="y", labelcolor="blue")

            ax2 = ax1.twinx()
            ax2.set_ylabel("Price (USD)", color="red")
            ax2.plot(df_combined_dual["date"], df_combined_dual["price"], color="red", label="Price")
            ax2.tick_params(axis="y", labelcolor="red")

            fig.suptitle(f"Word Count & Price for {selected_crypto_price} Over Time")
            fig.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("⚠️ No price data available for this crypto.")

        # 🔹 **6️⃣ Sentiment Confidence Boxplot**
        st.subheader("📊 Sentiment Confidence per Cryptocurrency")
        selected_crypto_confidence = st.selectbox(
            "Choose a Coin for Sentiment Confidence Analysis:", crypto_list, key=f"{category.lower()}_confidence"
        )
        df_filtered_confidence = df_crypto[df_crypto["crypto"].str.lower() == selected_crypto_confidence.lower()]

        if "sentiment_confidence" in df_filtered_confidence.columns and not df_filtered_confidence.empty:
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.boxplot(x=df_filtered_confidence["sentiment_confidence"], ax=ax)
            ax.set_xlabel("Sentiment Confidence Score")
            st.pyplot(fig)
        else:
            st.warning("⚠️ No sentiment confidence data available for this crypto.")

        # 🔹 **7️⃣ Sentiment Distribution per Crypto (High Confidence)**
        st.subheader("🎯 Sentiment Distribution (High Confidence)")
        selected_crypto_high_conf = st.selectbox(
            "Choose a Coin for High-Confidence Sentiment Analysis:", crypto_list, key=f"{category.lower()}_highconf"
        )
        df_filtered_high_conf = df_crypto[df_crypto["crypto"].str.lower() == selected_crypto_high_conf.lower()]
        CONFIDENCE_THRESHOLD = 0.8
        df_high_conf = df_filtered_high_conf[df_filtered_high_conf["sentiment_confidence"] >= CONFIDENCE_THRESHOLD]

        if not df_high_conf.empty:
            sentiment_dist_high_conf = df_high_conf.groupby(["sentiment"]).size()
            st.bar_chart(sentiment_dist_high_conf)
        else:
            st.warning("⚠️ No high-confidence sentiment data available for this crypto.")

        # 🔹 **8️⃣ High-Confidence Sentiment & Price Over Time**
        st.subheader("📊 High-Confidence Sentiment & Price Over Time")
        selected_crypto_high_conf_price = st.selectbox(
            "Choose a Coin for High-Confidence Sentiment & Price Trend:", crypto_list, key=f"{category.lower()}_highconf_price"
        )
        
        if selected_crypto_high_conf_price in df_prices["crypto"].values:
            df_high_conf_trend = df_high_conf.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
            df_combined_sentiment_price = df_high_conf_trend.merge(df_price_filtered, on="date", how="inner")

            fig, ax1 = plt.subplots(figsize=(10, 5))
            ax1.set_xlabel("Date")
            ax1.set_ylabel("Sentiment Count (High Confidence)", color="blue")
            ax1.plot(df_combined_sentiment_price.index, df_combined_sentiment_price["bullish"], color="green", label="Bullish (High Confidence)")
            ax1.plot(df_combined_sentiment_price.index, df_combined_sentiment_price["bearish"], color="red", label="Bearish (High Confidence)")
            ax1.tick_params(axis="y", labelcolor="blue")

            ax2 = ax1.twinx()
            ax2.set_ylabel("Price (USD)", color="black")
            ax2.plot(df_combined_sentiment_price.index, df_combined_sentiment_price["price"], color="black", label="Price", linewidth=2)
            ax2.tick_params(axis="y", labelcolor="black")

            fig.suptitle(f"High-Confidence Sentiment & Price for {selected_crypto_high_conf_price} Over Time")
            fig.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("⚠️ No high-confidence sentiment price data available.")




# 🔹 **Tab für jede Krypto-Kategorie**
top_coins = [
    "Bitcoin", "Ethereum", "Tether", "Ripple", "Binance Coin", "Solana", 
    "USD Coin", "Dogecoin", "Cardano", "TRON", "Polygon", "XRP", "Cronos"
]
crypto_analysis_tab(tab_top, "Top Coins", top_coins)

new_coins = [
    "NEAR", "MATIC", "Band", "Optimism", "Celestia", "Numerai", 
    "Atheir", "Sui", "HZPE", "Litecoin"
]
crypto_analysis_tab(tab_new, "New Coins", new_coins)