import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Reddit Data Dashboard", layout="centered")

# 🚀 **Cache zurücksetzen**
st.cache_data.clear()

# 📌 Google Drive File IDs für die Datensätze
MERGED_CRYPTO_CSV_ID = "11Q7obrTvT6KVoA8PPnwWYk7BscOtCweA"
CRYPTO_PRICES_CSV_ID = "10wkptEC82rQDttx2zMFrl7r4sYgkx421"

# 📌 Lokale Dateinamen
MERGED_CRYPTO_CSV = "reddit_merged.csv"
CRYPTO_PRICES_CSV = "crypto_prices.csv"

# 🔹 Funktion zum Herunterladen von CSV-Dateien von Google Drive
@st.cache_data
def download_csv(file_id, output):
    """Lädt eine CSV-Datei von Google Drive herunter"""
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output, quiet=False)

# 🔹 Sicherstellen, dass die Dateien existieren
if not os.path.exists(MERGED_CRYPTO_CSV):
    print(f"📥 Downloading {MERGED_CRYPTO_CSV} from Google Drive...")
    download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)

if not os.path.exists(CRYPTO_PRICES_CSV):
    print(f"📥 Downloading {CRYPTO_PRICES_CSV} from Google Drive...")
    download_csv(CRYPTO_PRICES_CSV_ID, CRYPTO_PRICES_CSV)

# 🔍 Überprüfung: Existieren die CSV-Dateien?
if os.path.exists(MERGED_CRYPTO_CSV):
    print(f"✅ Datei gefunden: {MERGED_CRYPTO_CSV}")
else:
    print(f"❌ Datei fehlt: {MERGED_CRYPTO_CSV}")

if os.path.exists(CRYPTO_PRICES_CSV):
    print(f"✅ Datei gefunden: {CRYPTO_PRICES_CSV}")
else:
    print(f"❌ Datei fehlt: {CRYPTO_PRICES_CSV}")

# 🔹 Funktion zum Laden der CSV-Daten mit Debugging
@st.cache_data
def load_csv(filepath):
    """Lädt eine CSV-Datei und zeigt Debugging-Informationen an"""
    if not os.path.exists(filepath):
        st.error(f"❌ Datei nicht gefunden: {filepath}")
        return pd.DataFrame()

    df = pd.read_csv(filepath, sep="|", encoding="utf-8-sig", on_bad_lines="skip")
    
    # Debugging: Zeige die ersten Zeilen
    print(f"📌 Spalten in {filepath}: {df.columns.tolist()}")
    print(df.head())  # Zeige die ersten 5 Zeilen
    
    return df

# 📌 Lade die Daten
df_crypto = load_csv(MERGED_CRYPTO_CSV)
df_prices = load_csv(CRYPTO_PRICES_CSV)

# 📊 Multi-Tab Navigation mit Kategorien
tab_home, tab_top, tab_new, tab_meme, tab_other, tab_stocks = st.tabs([
    "🏠 Home", "🏆 Top Coins", "📈 New Coins", "😂 Meme Coins", "⚡ Weitere Coins","💹 Stock Data"
])

# 🔹 **🏠 HOME (README)**
with tab_home:
    st.title("📊 Reddit Financial Sentiment Dashboard")
    st.markdown("""
        ## 🔍 Project Overview
        This dashboard provides a **data-driven analysis of cryptocurrency sentiment** using **Reddit discussions** and **historical price data** starting from November 2024. The project integrates multiple data sources to explore the relationship between social sentiment and market trends.

        ### 📊 **Data Sources & Processing**
        - **Reddit Comments & Posts:** Scraped weekly from multiple subreddits using a **custom Reddit scraper**.  
        - **Sentiment Analysis:** Applied **CryptoBERT** for a **bullish-bearish-neutral classification** with confidence scores.  
        - **Historical Price Data:** Collected from **CoinGecko API** for major cryptocurrencies.  
        - **Data Storage:** Merged sentiment and price data is stored and updated weekly in **Google Drive**.

        ### 🔎 **Key Features**
        - **📈 Crypto Sentiment Analysis:**  
          - Top mentioned cryptocurrencies & sentiment distribution  
          - Sentiment trends over time (overall & high-confidence)  
          - Word count trends for selected cryptos
          - Combined analysis of sentiment & price dynamics    
        - **💹 Stock Market Analysis (Coming Soon)**  

        ### 🔄 **Update Frequency**
        - **Reddit data & sentiment analysis:** Weekly  
        - **Crypto price data:** Weekly  

        ---
        🔥 **Use the navigation tabs above to explore sentiment trends & price dynamics!**
    """)
    # 🔄 **Refresh Button**
if st.button("🔄 Refresh Data"):
    # Lösche die vorhandene Datei, um sicherzugehen, dass neue Daten geladen werden
    if os.path.exists(MERGED_CRYPTO_CSV):
        os.remove(MERGED_CRYPTO_CSV)

    # Lade die neue Datei herunter
    download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)

    # Lade die neuen Daten in den DataFrame
    df_crypto = load_crypto_data()

    # Lösche den Cache und erzwinge das Neuladen der App
    st.cache_data.clear()
    st.rerun()