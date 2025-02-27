import streamlit as st
import pandas as pd
import gdown
import os

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Reddit Data Analysis", layout="wide")

# 🚀 **Cache zurücksetzen**
st.cache_data.clear()
st.cache_resource.clear()

# 📌 Google Drive File IDs
MERGED_CRYPTO_CSV_ID = "127YXOmbF5V6KEPu8tzzrSRY3T8Pe68an"
CRYPTO_PRICES_CSV_ID = "11k9wiflOkqg2DayEgn7iPqNPHC5Qatht"

# 📌 Lokale Dateinamen
MERGED_CRYPTO_CSV = "reddit_merged.csv"
CRYPTO_PRICES_CSV = "crypto_prices.csv"

# 🔹 **Download CSV-Dateien**
def download_csv(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        gdown.download(url, output, quiet=False)
        if not os.path.exists(output) or os.path.getsize(output) == 0:
            st.error(f"❌ Fehler: {output} wurde nicht korrekt heruntergeladen!")
    except Exception as e:
        st.error(f"❌ Download fehlgeschlagen: {str(e)}")

# 🔥 **Daten laden**
st.sidebar.write("📥 **Daten werden geladen...**")

# Datei-Download
download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)
download_csv(CRYPTO_PRICES_CSV_ID, CRYPTO_PRICES_CSV)

# **Lade CSV-Dateien**
def load_csv(filepath):
    """Lädt eine CSV-Datei mit `|` als Trennzeichen"""
    if not os.path.exists(filepath):
        st.error(f"❌ Datei nicht gefunden: {filepath}")
        return pd.DataFrame()
    
    df = pd.read_csv(filepath, sep="|", encoding="utf-8-sig", on_bad_lines="skip")
    return df

# 📌 Daten einlesen
df_crypto = load_csv(MERGED_CRYPTO_CSV)
df_prices = load_csv(CRYPTO_PRICES_CSV)

# 🔍 **Daten-Übersicht**
st.title("📊 Reddit Krypto-Datenanalyse")
st.subheader("📌 Datenübersicht")

col1, col2 = st.columns(2)

with col1:
    st.write("### 🔹 reddit_merged.csv")
    st.write(f"✅ **{df_crypto.shape[0]:,}** Einträge | **{df_crypto.shape[1]}** Spalten")
    st.write(df_crypto.head())

with col2:
    st.write("### 🔹 crypto_prices.csv")
    st.write(f"✅ **{df_prices.shape[0]:,}** Einträge | **{df_prices.shape[1]}** Spalten")
    st.write(df_prices.head())

# 🔍 **Fehlende Werte analysieren**
st.subheader("❌ Fehlende Werte in den Daten")

missing_crypto = df_crypto.isnull().sum()
missing_prices = df_prices.isnull().sum()

col1, col2 = st.columns(2)
with col1:
    st.write("🔹 **Fehlende Werte in reddit_merged.csv**")
    st.write(missing_crypto[missing_crypto > 0])

with col2:
    st.write("🔹 **Fehlende Werte in crypto_prices.csv**")
    st.write(missing_prices[missing_prices > 0])

# 📊 **Datenverteilung**
st.subheader("📊 Verteilung wichtiger Spalten")

col1, col2 = st.columns(2)

with col1:
    st.write("**📌 Häufigste Kryptowährungen in reddit_merged.csv**")
    crypto_counts = df_crypto["crypto"].value_counts().head(10)
    st.bar_chart(crypto_counts)

with col2:
    st.write("**📌 Sentiment-Verteilung in reddit_merged.csv**")
    sentiment_counts = df_crypto["sentiment"].value_counts()
    st.bar_chart(sentiment_counts)

st.success("✅ **Analyse abgeschlossen!**")
