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

        # 🔹 **1️⃣ Sentiment Distribution**
        sentiment_distribution = df_filtered["sentiment"].value_counts()
        st.bar_chart(sentiment_distribution)

        # 🔹 **2️⃣ Sentiment Trend Over Time**
        sentiment_trend = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
        st.line_chart(sentiment_trend)

# 🏆 **Top Coins**
top_coins = ["Ethereum", "Wrapped Ethereum", "Solana", "Avalanche", "Polkadot"]
crypto_analysis_tab(tab_top, "Top Coins", top_coins)

# 📈 **New Coins**
new_coins = ["Arbitrum", "Starknet", "Injective Protocol"]
crypto_analysis_tab(tab_new, "New Coins", new_coins)

# 😂 **Meme Coins**
meme_coins = ["Shiba Inu", "Pepe", "Floki Inu"]
crypto_analysis_tab(tab_meme, "Meme Coins", meme_coins)

# ⚡ **Weitere Coins**
other_coins = ["VeChain", "Render", "Filecoin"]
crypto_analysis_tab(tab_other, "Weitere Coins", other_coins)

# 🔹 **STOCK MARKET ANALYSIS**
with tab_stocks:
    st.title("💹 Stock Market Analysis (Coming Soon)")
    st.warning("🚧 This section is under development. Stock data will be integrated soon!")
