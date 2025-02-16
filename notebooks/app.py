import streamlit as st
import pandas as pd
import gdown
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import ast

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Reddit Data Dashboard", layout="centered")

# 🚀 **Cache wirklich zurücksetzen**
st.cache_data.clear()
st.cache_resource.clear()

# 📌 Google Drive File IDs für die Datensätze
MERGED_CRYPTO_CSV_ID = "11iGipDa3LUY9cMivOBVRrRbj0Nh6nbqT"
CRYPTO_PRICES_CSV_ID = "10wkptEC82rQDttx2zMFrl7r4sYgkx421"

# 📌 Lokale Dateinamen
MERGED_CRYPTO_CSV = "reddit_merged.csv"
CRYPTO_PRICES_CSV = "crypto_prices.csv"

# 🔹 Sicherstellen, dass die aktuelle CSV geladen wird
def download_csv(file_id, output):
    """Lädt eine CSV-Datei von Google Drive herunter"""
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        gdown.download(url, output, quiet=False)
        if not os.path.exists(output) or os.path.getsize(output) == 0:
            st.error(f"❌ Fehler: {output} wurde nicht korrekt heruntergeladen!")
    except Exception as e:
        st.error(f"❌ Download fehlgeschlagen: {str(e)}")

# 📥 **Dateien von Google Drive herunterladen**
if os.path.exists(MERGED_CRYPTO_CSV):
    os.remove(MERGED_CRYPTO_CSV)
print(f"📥 Downloading {MERGED_CRYPTO_CSV} from Google Drive...")
download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)

if os.path.exists(CRYPTO_PRICES_CSV):
    os.remove(CRYPTO_PRICES_CSV)
print(f"📥 Downloading {CRYPTO_PRICES_CSV} from Google Drive...")
download_csv(CRYPTO_PRICES_CSV_ID, CRYPTO_PRICES_CSV)

# 🔍 **Funktion zum Laden der CSV-Dateien mit Debugging**
def load_csv(filepath):
    """Lädt eine CSV-Datei mit `|` als Trennzeichen"""
    if not os.path.exists(filepath):
        st.error(f"❌ Datei nicht gefunden: {filepath}")
        return pd.DataFrame()

    df = pd.read_csv(filepath, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # 🔹 Debugging-Informationen
    print(f"\n📌 Datei geladen: {filepath}")
    print(f"🔹 Spalten: {df.columns.tolist()}")
    print(df.dtypes)
    print(df.head())

    return df

# 📌 **Daten laden**
df_crypto = load_csv(MERGED_CRYPTO_CSV)
df_prices = load_csv(CRYPTO_PRICES_CSV)

# 🔹 **Daten bereinigen & anpassen**
def clean_crypto_data(df):
    """Reinigt die Reddit-Krypto-Daten und korrigiert Datentypen."""
    df = df.copy()

    # ✅ `date` in `datetime64` umwandeln
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")

    # ✅ `time` als Zeitformat speichern
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S", errors="coerce").dt.time

    # ✅ `comment_id` NaN durch None ersetzen
    if "comment_id" in df.columns:
        df["comment_id"] = df["comment_id"].astype("object").where(df["comment_id"].notna(), None)

    return df

def clean_price_data(df):
    """Reinigt die Krypto-Preisdaten."""
    df = df.copy()

    # ✅ `date` in `datetime64` umwandeln
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # ✅ `price` in `float64` umwandeln
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")

    return df

# 📌 Wende die Bereinigung an
df_crypto = clean_crypto_data(df_crypto)
df_prices = clean_price_data(df_prices)

# ✅ Sicherstellen, dass `date` wirklich `datetime64[ns]` ist
df_crypto["date"] = pd.to_datetime(df_crypto["date"], format="%Y-%m-%d", errors="coerce")
df_prices["date"] = pd.to_datetime(df_prices["date"], errors="coerce")

# 🔍 Debugging-Check
print(f"📌 Überprüfte Spalten:")
print(df_crypto.dtypes)
print(df_crypto.head())


print("🔍 Verfügbare Kryptowährungen im Datensatz:", df_crypto["crypto"].unique())


## 📊 **Multi-Tab Navigation mit Kategorien**
tab_home, tab_top, tab_new, tab_meme, tab_other, tab_stocks = st.tabs([
    "🏠 Home", "🏆 Top Coins", "📈 New Coins", "😂 Meme Coins", "⚡ Weitere Coins", "💹 Stock Data"
])

# 🔹 **🏠 HOME (README)**
with tab_home:
    st.title("📊 Reddit Financial Sentiment Dashboard")
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

# 📊 **Tabs für verschiedene Krypto-Kategorien**
def crypto_analysis_tab(tab, category, crypto_list):
    with tab:
        st.title(f"{category} Sentiment & Mentions")

        # ✅ **Nur existierende Coins anzeigen**
        crypto_list = [coin for coin in crypto_list if coin in available_cryptos]

        if not crypto_list:
            st.warning(f"⚠️ No cryptocurrencies available in this category.")
            return

        selected_crypto = st.selectbox(
            f"Choose a {category} Coin:", crypto_list, key=f"{category.lower()}_crypto"
        )

        # ✅ **Daten filtern**
        df_filtered = df_crypto[df_crypto["crypto"].str.lower() == selected_crypto.lower()]

        # 🔍 **Debugging: Überprüfen, ob gefilterte Daten existieren**
        print(f"📊 {category} - Verfügbare Daten für {selected_crypto}:")
        print(df_filtered.head())

        if df_filtered.empty:
            st.warning(f"⚠️ No data available for {selected_crypto}.")
            return

        # ✅ **1️⃣ Sentiment Distribution**
        st.subheader("💡 Sentiment Distribution of Cryptos")
        if "sentiment" in df_filtered.columns:
            sentiment_distribution = df_filtered["sentiment"].value_counts()
            st.bar_chart(sentiment_distribution)
        else:
            st.warning("⚠️ `sentiment` column not found. Skipping sentiment distribution.")

        # ✅ **2️⃣ Word Count Over Time**
        st.subheader("📝 Word Count Evolution Over Time")
        if "date" in df_filtered.columns:
            wordcount_per_day = df_filtered.groupby("date").size()
            st.line_chart(wordcount_per_day)
        else:
            st.warning("⚠️ `date` column not found. Skipping word count.")

        # ✅ **3️⃣ Sentiment Trend Over Time**
        st.subheader("📅 Sentiment Trend Over Time")
        if "sentiment" in df_filtered.columns:
            sentiment_trend = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
            st.line_chart(sentiment_trend)
        else:
            st.warning("⚠️ `sentiment` column not found. Skipping sentiment trends.")

        # ✅ **4️⃣ Sentiment Confidence Boxplot**
        st.subheader("📊 Sentiment Confidence per Cryptocurrency")
        if "sentiment_confidence" in df_filtered.columns:
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.boxplot(x=df_filtered["sentiment_confidence"], ax=ax)
            ax.set_xlabel("Sentiment Confidence Score")
            st.pyplot(fig)
        else:
            st.warning("⚠️ `sentiment_confidence` column not found. Skipping boxplot.")

        # ✅ **5️⃣ High-Confidence Sentiment**
        st.subheader("🎯 Sentiment Distribution (High Confidence)")
        CONFIDENCE_THRESHOLD = 0.8
        df_high_conf = df_filtered[df_filtered["sentiment_confidence"] >= CONFIDENCE_THRESHOLD]
        sentiment_dist_high_conf = df_high_conf.groupby(["sentiment"]).size()
        st.bar_chart(sentiment_dist_high_conf)

        # ✅ **6️⃣ High-Confidence Sentiment & Price Over Time**
        st.subheader("📊 High-Confidence Sentiment & Price Over Time")
        if selected_crypto in df_prices["crypto"].values:
            df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto]
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

            fig.suptitle(f"High-Confidence Sentiment & Price for {selected_crypto} Over Time")
            fig.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("⚠️ No price data available for this crypto.")

# 📊 **Tabs initialisieren**
top_coins = ["Ethereum", "Wrapped Ethereum", "Solana", "Avalanche", "Polkadot", "Near Protocol", "Polygon", "XRP", "Cardano", "Cronos"]
crypto_analysis_tab(tab_top, "Top Coins", top_coins)

new_coins = ["Arbitrum", "Starknet", "Injective Protocol", "Sei Network", "Aptos"]
crypto_analysis_tab(tab_new, "New Coins", new_coins)

meme_coins = ["Shiba Inu", "Pepe", "Floki Inu", "Bonk", "Degen", "Toshi"]
crypto_analysis_tab(tab_meme, "Meme Coins", meme_coins)

other_coins = ["VeChain", "Render", "Hedera", "Filecoin", "Cosmos"]
crypto_analysis_tab(tab_other, "Weitere Coins", other_coins)

# 🔹 **💹 STOCK MARKET ANALYSIS**
with tab_stocks:
    st.title("💹 Stock Market Analysis (Coming Soon)")
    st.warning("🚧 This section is under development. Stock data will be integrated soon!")
