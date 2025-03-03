import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Reddit Crypto Dashboard", layout="wide")

# 📥 **Google Drive File IDs**
MERGED_CRYPTO_CSV_ID = "12erlPOoKQS5jgB0Qh74uY3cuY3adAz6r"
CRYPTO_PRICES_CSV_ID = "11k9wiflOkqg2DayEgn7iPqNPHC5Qatht"

# 📌 **Lokale Dateinamen**
MERGED_CRYPTO_CSV = "reddit_merged.csv"
CRYPTO_PRICES_CSV = "crypto_prices.csv"

# 🔥 **Daten herunterladen**
def download_csv(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        gdown.download(url, output, quiet=False)
        if not os.path.exists(output) or os.path.getsize(output) == 0:
            st.error(f"❌ Fehler: {output} wurde nicht korrekt heruntergeladen!")
    except Exception as e:
        st.error(f"❌ Download fehlgeschlagen: {str(e)}")

# 📥 **Daten laden**
download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)
download_csv(CRYPTO_PRICES_CSV_ID, CRYPTO_PRICES_CSV)

# 📌 **CSV-Dateien einlesen**
@st.cache_data
def load_csv(filepath):
    if not os.path.exists(filepath):
        st.error(f"❌ Datei nicht gefunden: {filepath}")
        return pd.DataFrame()
    return pd.read_csv(filepath, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

df_crypto = load_csv(MERGED_CRYPTO_CSV)
df_prices = load_csv(CRYPTO_PRICES_CSV)

# 🔹 Datentypen korrigieren
df_crypto["date"] = pd.to_datetime(df_crypto["date"], format="%Y-%m-%d", errors="coerce")

df_crypto["crypto"] = df_crypto["crypto"].astype(str)
df_crypto["sentiment"] = df_crypto["sentiment"].astype(str)

# 🔍 Debugging: Dtypes prüfen
print(df_crypto.dtypes)
print(df_crypto.head())

# 📊 **Multi-Tab Navigation mit Kategorien**
tab_home, tab_top, tab_new, tab_meme, tab_other = st.tabs([
    "🏠 Home", "🏆 Top Coins", "📈 New Coins", "😂 Meme Coins", "⚡ Weitere Coins"
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

# 📊 **Funktion für die Tabs mit zwei Visualisierungen**
def crypto_analysis_tab(tab, category, crypto_list):
    with tab:
        st.title(f"{category} Sentiment & Mentions")

        # 🔹 **Nur relevante Coins anzeigen**
        df_filtered = df_crypto[df_crypto["crypto"].isin(crypto_list)]
        available_cryptos = df_filtered["crypto"].unique()
        print(f"🔍 Verfügbare Kryptowährungen in {category}: {available_cryptos}")

        if df_filtered.empty:
            st.warning(f"⚠️ No data available for {category}.")
            return

        # 📊 **1️⃣ Erwähnungen pro Crypto**
        st.subheader("🔥 Most Mentioned Cryptocurrencies")
        crypto_counts = df_filtered["crypto"].value_counts()
        st.bar_chart(crypto_counts)

        # 📊 **2️⃣ Sentiment-Trend über die Zeit**
        st.subheader("📅 Sentiment Trend Over Time")
        sentiment_trend = df_filtered.groupby(["date", "crypto", "sentiment"]).size().unstack(fill_value=0)
        st.line_chart(sentiment_trend)

# 🔹 **Tab für jede Krypto-Kategorie**
top_coins = ["Ethereum", "Wrapped Ethereum", "Solana", "Avalanche", "Polkadot", "Near Protocol", "Polygon", "XRP", "Cardano", "Cronos"]
crypto_analysis_tab(tab_top, "Top Coins", top_coins)

new_coins = ["Arbitrum", "Starknet", "Injective Protocol", "Sei Network", "Aptos", "EigenLayer", "Mantle", "Immutable X", "Ondo Finance"]
crypto_analysis_tab(tab_new, "New Coins", new_coins)

meme_coins = ["Shiba Inu", "Pepe", "Floki Inu", "Bonk", "Degen", "Toshi", "Fartcoin", "Banana", "Husky"]
crypto_analysis_tab(tab_meme, "Meme Coins", meme_coins)

other_coins = ["VeChain", "Render", "Kusama", "Hedera", "Filecoin", "Cosmos", "Numerai", "Berachain", "The Sandbox"]
crypto_analysis_tab(tab_other, "Weitere Coins", other_coins)
