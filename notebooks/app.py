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
MERGED_CRYPTO_CSV_ID = "127YXOmbF5V6KEPu8tzzrSRY3T8Pe68an"
CRYPTO_PRICES_CSV_ID = "11k9wiflOkqg2DayEgn7iPqNPHC5Qatht"

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

# 🔍 Debugging-Check
print(f"📌 Überprüfte Spalten:")
print(df_crypto.dtypes)
print(df_crypto.head())


print("🔍 Verfügbare Kryptowährungen im Datensatz:", df_crypto["crypto"].unique())


# 📊 **Multi-Tab Navigation mit Kategorien**
tab_home, tab_top, tab_new, tab_meme, tab_other, tab_stocks = st.tabs([
    "🏠 Home", "🏆 Top Coins", "📈 New Coins", "😂 Meme Coins", "⚡ Weitere Coins","💹 Stock Data"
])

# 🔹 **🏠 HOME (README)**
with tab_home:
    st.title("📊 Reddit Sentiment Dashboard")
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

        # 🔹 Debugging: Alle verfügbaren Kryptowährungen im Datensatz anzeigen
        available_cryptos = df_crypto["crypto"].dropna().unique().tolist()
        available_cryptos = [crypto for crypto in crypto_list if crypto in available_cryptos]
        print(f"🔍 Verfügbare Kryptowährungen im Datensatz für {category}: {available_cryptos}")

        if not available_cryptos:
            st.warning(f"⚠️ No cryptocurrencies available in this category.")
            return

        # 🔹 **Korrekte Filterung für alle Coins in diesem Tab**
        df_filtered = df_crypto[df_crypto["crypto"].isin(available_cryptos)]

        # 🔍 Debugging: Zeige die ersten Zeilen nach der Filterung
        print(f"📊 {category} - Verfügbare Daten nach Filterung:")
        print(df_filtered.head())

        if df_filtered.empty:
            st.warning(f"⚠️ No data available for {category}.")
            return  # Stoppe die weitere Verarbeitung, wenn keine Daten vorhanden sind

        # 🔹 Anzeige der gefilterten Daten
        st.write(df_filtered)

        # 🔹 **1️⃣ Most Discussed Cryptos**
        st.subheader("🔥 Most Mentioned Cryptocurrencies")
        if "crypto" in df_filtered.columns:
            crypto_counts = df_filtered["crypto"].value_counts()
            st.bar_chart(crypto_counts)
        else:
            st.warning("⚠️ `crypto` column not found. Skipping this section.")

        # 🔹 **2️⃣ Sentiment Distribution per Crypto**
        st.subheader("💡 Sentiment Distribution")
        if "sentiment" in df_filtered.columns:
            sentiment_distribution = df_filtered.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
            st.bar_chart(sentiment_distribution)
        else:
            st.warning("⚠️ `sentiment` column not found. Skipping this section.")

        # 🔹 **3️⃣ Word Count Over Time**
        st.subheader("📝 Word Count Evolution Over Time")
        if "date" in df_filtered.columns:
            wordcount_per_day = df_filtered.groupby(["date", "crypto"]).size().unstack(fill_value=0)
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
        df_combined_dual = None
        for selected_crypto in available_cryptos:
            if selected_crypto in df_prices["crypto"].values:
                df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto]
                df_crypto_filtered = df_filtered[df_filtered["crypto"] == selected_crypto]
                df_wordcount = df_crypto_filtered.groupby("date").size().reset_index(name="word_count")
                df_combined = df_wordcount.merge(df_price_filtered, on="date", how="inner")

                if df_combined_dual is None:
                    df_combined_dual = df_combined
                else:
                    df_combined_dual = pd.concat([df_combined_dual, df_combined])

        if df_combined_dual is not None and not df_combined_dual.empty:
            fig, ax1 = plt.subplots(figsize=(10, 5))
            ax1.set_xlabel("Date")
            ax1.set_ylabel("Word Count", color="blue")
            for crypto in df_combined_dual["crypto"].unique():
                df_subset = df_combined_dual[df_combined_dual["crypto"] == crypto]
                ax1.plot(df_subset["date"], df_subset["word_count"], label=f"{crypto} Word Count")
            ax1.tick_params(axis="y", labelcolor="blue")
            ax1.legend(loc="upper left")

            ax2 = ax1.twinx()
            ax2.set_ylabel("Price (USD)", color="red")
            for crypto in df_combined_dual["crypto"].unique():
                df_subset = df_combined_dual[df_combined_dual["crypto"] == crypto]
                ax2.plot(df_subset["date"], df_subset["price"], linestyle="dashed", label=f"{crypto} Price")
            ax2.tick_params(axis="y", labelcolor="red")
            ax2.legend(loc="upper right")

            fig.suptitle(f"Word Count & Price for Cryptos in {category} Over Time")
            fig.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("⚠️ No price data available for any cryptos in this category.")

        # 🔹 **6️⃣ Sentiment Confidence Boxplot**
        st.subheader("📊 Sentiment Confidence per Cryptocurrency")
        if "sentiment_confidence" in df_filtered.columns:
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.boxplot(x=df_filtered["crypto"], y=df_filtered["sentiment_confidence"], ax=ax)
            ax.set_xlabel("Cryptocurrency")
            ax.set_ylabel("Sentiment Confidence Score")
            st.pyplot(fig)
        else:
            st.warning("⚠️ `sentiment_confidence` column not found. Skipping boxplot.")

        # 🔹 **7️⃣ Sentiment Distribution per Crypto (High Confidence)**
        st.subheader("🎯 Sentiment Distribution (High Confidence)")
        CONFIDENCE_THRESHOLD = 0.8
        df_high_conf = df_filtered[df_filtered["sentiment_confidence"] >= CONFIDENCE_THRESHOLD]
        sentiment_dist_high_conf = df_high_conf.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
        st.bar_chart(sentiment_dist_high_conf)

        # 🔹 **8️⃣ High-Confidence Sentiment & Price Over Time**
        st.subheader("📊 High-Confidence Sentiment & Price Over Time")
        df_combined_sentiment_price = None
        for selected_crypto in available_cryptos:
            if selected_crypto in df_prices["crypto"].values:
                df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto]
                df_high_conf_filtered = df_high_conf[df_high_conf["crypto"] == selected_crypto]
                df_high_conf_trend = df_high_conf_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
                df_combined = df_high_conf_trend.merge(df_price_filtered, on="date", how="inner")

                if df_combined_sentiment_price is None:
                    df_combined_sentiment_price = df_combined
                else:
                    df_combined_sentiment_price = pd.concat([df_combined_sentiment_price, df_combined])

        if df_combined_sentiment_price is not None and not df_combined_sentiment_price.empty:
            fig, ax1 = plt.subplots(figsize=(10, 5))
            ax1.set_xlabel("Date")
            ax1.set_ylabel("Sentiment Count (High Confidence)", color="blue")
            for crypto in df_combined_sentiment_price["crypto"].unique():
                df_subset = df_combined_sentiment_price[df_combined_sentiment_price["crypto"] == crypto]
                ax1.plot(df_subset.index, df_subset["bullish"], color="green", label=f"{crypto} Bullish (High Confidence)")
                ax1.plot(df_subset.index, df_subset["bearish"], color="red", label=f"{crypto} Bearish (High Confidence)")
            ax1.tick_params(axis="y", labelcolor="blue")
            ax1.legend(loc="upper left")

            ax2 = ax1.twinx()
            ax2.set_ylabel("Price (USD)", color="black")
            for crypto in df_combined_sentiment_price["crypto"].unique():
                df_subset = df_combined_sentiment_price[df_combined_sentiment_price["crypto"] == crypto]
                ax2.plot(df_subset.index, df_subset["price"], color="black", label=f"{crypto} Price", linewidth=2)
            ax2.tick_params(axis="y", labelcolor="black")
            ax2.legend(loc="upper right")

            fig.suptitle(f"High-Confidence Sentiment & Price for Cryptos in {category} Over Time")
            fig.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("⚠️ No high-confidence sentiment price data available.")

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
