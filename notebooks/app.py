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
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()  # Löscht gecachte Daten
    st.cache_resource.clear()  # Löscht gecachte Ressourcen
    st.experimental_rerun()  # Seite neu laden

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
    """)

# 📊 **Tabs für verschiedene Krypto-Kategorien**
def crypto_analysis_tab(tab, category, crypto_list):
    with tab:
        st.title(f"{category} Sentiment & Mentions")

        available_cryptos = df_crypto["crypto"].dropna().unique().tolist()
        selected_crypto = st.selectbox(
            f"Choose a {category} Coin:", [c for c in crypto_list if c in available_cryptos]
        )

        df_filtered = df_crypto[df_crypto["crypto"].str.lower() == selected_crypto.lower()]
        if df_filtered.empty:
            st.warning(f"⚠️ No data available for {selected_crypto}.")
            return

        st.write(df_filtered)

        # 🔹 **1️⃣ Most Discussed Cryptos**
        st.subheader("🔥 Top 10 Most Mentioned Cryptocurrencies")
        if "crypto" in df_filtered.columns:
            crypto_counts = df_filtered["crypto"].value_counts().head(10)
            st.bar_chart(crypto_counts)
        else:
            st.warning("⚠️ `crypto` column not found. Skipping this section.")

        # 🔹 **2️⃣ Sentiment Distribution per Crypto**
        st.subheader("💡 Sentiment Distribution of Cryptos")
        if "sentiment" in df_filtered.columns:
            sentiment_distribution = df_filtered["sentiment"].value_counts()
            st.bar_chart(sentiment_distribution)
        else:
            st.warning("⚠️ `sentiment` column not found. Skipping this section.")

        # 🔹 **3️⃣ Word Count Over Time**
        st.subheader("📝 Word Count Evolution Over Time")
        if "date" in df_filtered.columns:
            wordcount_per_day = df_filtered.groupby("date").size()
            st.line_chart(wordcount_per_day)
        else:
            st.warning("⚠️ `date` column not found. Skipping word count evolution.")

        # 🔹 **4️⃣ Sentiment Trend Over Time**
        st.subheader("📅 Sentiment Trend Over Time")
        if "sentiment" in df_filtered.columns:
            sentiment_trend = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
            st.line_chart(sentiment_trend)
        else:
            st.warning("⚠️ `sentiment` column not found. Skipping sentiment trends.")

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
        else:
            st.warning("⚠️ No price data available for this crypto.")

        # 🔹 **6️⃣ Sentiment Confidence Boxplot**
        st.subheader("📊 Sentiment Confidence per Cryptocurrency")
        if "sentiment_confidence" in df_filtered.columns:
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.boxplot(x=df_filtered["sentiment_confidence"], ax=ax)
            ax.set_xlabel("Sentiment Confidence Score")
            st.pyplot(fig)
        else:
            st.warning("⚠️ `sentiment_confidence` column not found. Skipping boxplot.")

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
        else:
            st.warning("⚠️ No high-confidence sentiment price data available.")

# 🏆 **Top Coins**
top_coins = ["Ethereum", "Wrapped Ethereum", "Solana", "Avalanche", "Polkadot", "Near Protocol", "Polygon", "XRP", "Cardano", "Cronos", "Chiliz", "Ronin", "Band Protocol", "Optimism", "Celestia", "Aethir", "Sui", "Hyperliquid", "Robinhood Coin", "Trump Coin", "USD Coin", "Binance Coin", "Litecoin", "Dogecoin", "Tron", "Aave", "Hedera", "Cosmos", "Gala", "Chainlink"]
crypto_analysis_tab(tab_top, "Top Coins", top_coins)


 # 🏆 **Top Coins**
top_coins = ["Ethereum", "Wrapped Ethereum", "Solana", "Avalanche", "Polkadot", "Near Protocol", "Polygon", "XRP", "Cardano", "Cronos",  "Chiliz",  "Ronin", "Band Protocol", "Optimism", "Celestia",  "Aethir", "Sui", "Hyperliquid", "Robinhood Coin", "Trump Coin", "USD Coin", "Binance Coin", "Litecoin", "Dogecoin", "Tron", "Aave", "Hedera",  "Cosmos", "Gala", "Chainlink"]
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

# 🔹 **STOCK MARKET ANALYSIS**
with tab_stocks:
    st.title("💹 Stock Market Analysis (Coming Soon)")
    st.warning("🚧 This section is under development. Stock data will be integrated soon!")
