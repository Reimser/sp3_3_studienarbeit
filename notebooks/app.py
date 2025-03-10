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

        if not crypto_counts.empty:
            st.bar_chart(crypto_counts)
        else:
            st.warning("⚠️ Keine Erwähnungen verfügbar.")

        # 📊 **2️⃣ Sentiment-Verteilung**
        st.subheader("😊 Sentiment Distribution")
        sentiment_counts = df_filtered["sentiment"].value_counts()

        if not sentiment_counts.empty:
            st.bar_chart(sentiment_counts)
        else:
            st.warning("⚠️ Keine Sentiment-Daten verfügbar.")

        # 📊 **3️⃣ Sentiment-Trend über die Zeit**
        st.subheader("📅 Sentiment Trend Over Time")
        if "date" in df_filtered.columns and not df_filtered.empty:
            sentiment_trend = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
            if not sentiment_trend.empty:
                st.line_chart(sentiment_trend)
            else:
                st.warning("⚠️ Keine Zeitreihendaten verfügbar.")
        else:
            st.warning("⚠️ Spalte 'date' nicht gefunden oder keine Daten verfügbar.")



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