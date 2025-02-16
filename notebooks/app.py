import streamlit as st
import pandas as pd
import gdown
import os
import numpy as np
import matplotlib.pyplot as plt
import ast
import seaborn as sns

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Reddit Data Dashboard", layout="centered")

# 🚀 **Cache wirklich zurücksetzen**
st.cache_data.clear()
st.cache_resource.clear()
if "rerun_trigger" not in st.session_state:
    st.session_state.rerun_trigger = False

if st.session_state.rerun_trigger:
    st.session_state.rerun_trigger = False

# 📌 Google Drive File IDs für die Datensätze
MERGED_CRYPTO_CSV_ID = "11iGipDa3LUY9cMivOBVRrRbj0Nh6nbqT"
CRYPTO_PRICES_CSV_ID = "10wkptEC82rQDttx2zMFrl7r4sYgkx421"

# 📌 Lokale Dateinamen
MERGED_CRYPTO_CSV = "reddit_merged.csv"
CRYPTO_PRICES_CSV = "crypto_prices.csv"

# 🔹 Funktion zum Herunterladen von CSV-Dateien
@st.cache_data
def download_csv(file_id, output):
    """Lädt eine CSV-Datei von Google Drive herunter"""
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output, quiet=False)

# 🔹 Sicherstellen, dass die aktuelle CSV geladen wird
if os.path.exists(MERGED_CRYPTO_CSV):
    os.remove(MERGED_CRYPTO_CSV)

print(f"📥 Downloading {MERGED_CRYPTO_CSV} from Google Drive...")
download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)

if os.path.exists(CRYPTO_PRICES_CSV):
    os.remove(CRYPTO_PRICES_CSV)

print(f"📥 Downloading {CRYPTO_PRICES_CSV} from Google Drive...")
download_csv(CRYPTO_PRICES_CSV_ID, CRYPTO_PRICES_CSV)

# 🔍 **Funktion zum Laden der CSV-Dateien mit Debugging**
@st.cache_data
def load_csv(filepath):
    """Lädt eine CSV-Datei und zeigt Debugging-Informationen an"""
    if not os.path.exists(filepath):
        st.error(f"❌ Datei nicht gefunden: {filepath}")
        return pd.DataFrame()

    df = pd.read_csv(filepath, encoding="utf-8-sig", on_bad_lines="skip")

    # 🔹 Debugging: Spalten und erste Werte anzeigen
    print(f"\n📌 Datei: {filepath}")
    print(f"🔹 Spalten: {df.columns.tolist()}")
    print(df.dtypes)  # Datentypen prüfen
    print(df.head())   # Erste Zeilen anzeigen

    return df

# 📌 **Daten laden**
df_crypto = load_csv(MERGED_CRYPTO_CSV).copy()
df_prices = load_csv(CRYPTO_PRICES_CSV).copy()

# 🔹 **Daten bereinigen & anpassen**
def clean_crypto_data(df):
    """Reinigt die Reddit-Krypto-Daten und setzt den Goldstandard."""
    df = df.copy()

    # ✅ `date` in `datetime64` umwandeln
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # ✅ `comment_id` NaN durch None ersetzen
    df["comment_id"] = df["comment_id"].astype("object").where(df["comment_id"].notna(), None)

    return df

def clean_price_data(df):
    """Reinigt die Krypto-Preisdaten."""
    df = df.copy()

    # ✅ `date` in `datetime64` umwandeln
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # ✅ `price` in `float64` umwandeln
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    return df

# 📌 Wende die Bereinigung an
df_crypto = clean_crypto_data(df_crypto)
df_prices = clean_price_data(df_prices)

# Debugging: Zeige alle Spaltennamen und Datentypen
print("📌 Spalten in df_crypto:", df_crypto.columns.tolist())
print("🔍 Datentypen in df_crypto:")
print(df_crypto.dtypes)
print(df_crypto.head())  # Erste Zeilen zur Überprüfung


# 📊 **Multi-Tab Navigation mit Kategorien**
tab_home, tab_top, tab_new, tab_meme, tab_other, tab_stocks = st.tabs([
    "🏠 Home", "🏆 Top Coins", "📈 New Coins", "😂 Meme Coins", "⚡ Weitere Coins","💹 Stock Data"
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

        selected_crypto = st.selectbox(
            f"Choose a {category} Coin:", crypto_list, key=f"{category.lower()}_crypto"
        )

        # 🔹 Korrekte Filterung basierend auf dem neuen Datensatz
        df_filtered = df_crypto[df_crypto["crypto"].astype(str) == selected_crypto]

        # 🔍 Debugging: Zeige die ersten Zeilen nach der Filterung
        st.write(f"📊 {category} - Verfügbare Daten für {selected_crypto}:")
        st.write(df_filtered.head())

        if df_filtered.empty:
            st.warning(f"⚠️ No data available for {selected_crypto}.")
            st.stop()


        # 🔹 **1️⃣ Most Discussed Cryptos**
        st.subheader("🔥 Top 10 Most Mentioned Cryptocurrencies")
        crypto_counts = df_filtered["detected_crypto"].explode().value_counts().head(10)
        st.bar_chart(crypto_counts)

        # 🔹 **2️⃣ Sentiment Distribution per Crypto**
        st.subheader("💡 Sentiment Distribution of Cryptos")
        sentiment_distribution = df_filtered.groupby(["sentiment"]).size()
        st.bar_chart(sentiment_distribution)

        # 🔹 **3️⃣ Word Count Over Time**
        st.subheader("📝 Word Count Evolution Over Time")
        wordcount_per_day = df_filtered.groupby("date").size()
        st.line_chart(wordcount_per_day)

        # 🔹 **4️⃣ Sentiment Trend Over Time**
        st.subheader("📅 Sentiment Trend Over Time")
        sentiment_trend = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
        st.line_chart(sentiment_trend)

        # 🔹 **5️⃣ Word Count & Price Over Time**
        st.subheader("📊 Word Count & Price Over Time")
        if selected_crypto in df_prices["crypto"].values:
            df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto]
            df_combined_dual = df_filtered.groupby("date").size().reset_index(name="word_count")
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

            fig.suptitle(f"Word Count & Price for {selected_crypto} Over Time")
            fig.tight_layout()
            st.pyplot(fig)

        # 🔹 **6️⃣ Sentiment Confidence Boxplot**
        st.subheader("📊 Sentiment Confidence per Cryptocurrency")
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.boxplot(x=df_filtered["sentiment_confidence"], ax=ax)
        ax.set_xlabel("Sentiment Confidence Score")
        st.pyplot(fig)

        # 🔹 **7️⃣ Sentiment Distribution per Crypto (High Confidence)**
        st.subheader("🎯 Sentiment Distribution (High Confidence)")
        CONFIDENCE_THRESHOLD = 0.8
        df_high_conf = df_filtered[df_filtered["sentiment_confidence"] >= CONFIDENCE_THRESHOLD]
        sentiment_dist_high_conf = df_high_conf.groupby(["sentiment"]).size()
        st.bar_chart(sentiment_dist_high_conf)

        # 🔹 **8️⃣ High-Confidence Sentiment & Price Over Time**
        st.subheader("📊 High-Confidence Sentiment & Price Over Time")
        if selected_crypto in df_prices["crypto"].values:
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


 # 🏆 **Top Coins**
top_coins = ["Bitcoin", "Ethereum", "Wrapped Ethereum", "Solana", "Avalanche", "Polkadot", "Near Protocol", "Polygon", "XRP", "Cardano", "Cronos",  "Chiliz",  "Ronin", "Band Protocol", "Optimism", "Celestia",  "Aethir", "Sui", "Hyperliquid", "Robinhood Coin", "Trump Coin", "USD Coin", "Binance Coin", "Litecoin", "Dogecoin", "Tron", "Aave", "Hedera",  "Cosmos", "Gala", "Chainlink"]
crypto_analysis_tab(tab_top, "Top Coins", top_coins)

# 📈 **New Coins**
new_coins = ["Arbitrum", "Starknet", "Injective Protocol", "Sei Network", "Aptos", "EigenLayer", "Mantle", "Immutable X", "Ondo Finance", "Worldcoin", "Aerodrome", "Jupiter", "THORChain", "Pendle", "Kujira", "Noble", "Stride", "Dymension", "Seamless Protocol", "Blast", "Merlin", "Tapioca", "Arcadia Finance", "Notcoin", "Omni Network", "LayerZero", "ZetaChain", "Friend.tech"]
crypto_analysis_tab(tab_new, "New Coins", new_coins)

# 😂 **Meme Coins**
meme_coins = ["Shiba Inu", "Pepe", "Floki Inu", "Bonk", "Wojak", "Mog Coin", "Doge Killer (Leash)", "Baby Doge Coin", "Degen", "Toshi", "Fartcoin", "Banana", "Kabosu", "Husky", "Samoyedcoin", "Milkbag"]
crypto_analysis_tab(tab_meme, "Meme Coins", meme_coins)

# ⚡ **Weitere Coins**
other_coins = ["VeChain", "Render", "Kusama", "Hedera", "Filecoin", "Vulcan Forged PYR", "Illuvium", "Numerai", "Audius", "Kusama",  "Berachain", "The Sandbox", "TestCoin", "Cosmos"]
crypto_analysis_tab(tab_other, "Weitere Coins", other_coins)

# 🔹 **💹 STOCK MARKET ANALYSIS**
with tab_stocks:
    st.title("💹 Stock Market Analysis (Coming Soon)")
    st.warning("🚧 This section is under development. Stock data will be integrated soon!")
