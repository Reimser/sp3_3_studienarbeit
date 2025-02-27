import streamlit as st
import pandas as pd
import gdown
import os

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Reddit Data Import", layout="centered")

# 🚀 **Cache wirklich zurücksetzen**
st.cache_data.clear()
st.cache_resource.clear()

# 📌 Google Drive File IDs
MERGED_CRYPTO_CSV_ID = "127YXOmbF5V6KEPu8tzzrSRY3T8Pe68an"
CRYPTO_PRICES_CSV_ID = "11k9wiflOkqg2DayEgn7iPqNPHC5Qatht"

# 📌 Lokale Dateinamen
MERGED_CRYPTO_CSV = "reddit_merged.csv"
CRYPTO_PRICES_CSV = "crypto_prices.csv"

# 🔹 **Download CSV-Dateien von Google Drive**
def download_csv(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        gdown.download(url, output, quiet=False)
        if not os.path.exists(output) or os.path.getsize(output) == 0:
            st.error(f"❌ Fehler: {output} wurde nicht korrekt heruntergeladen!")
    except Exception as e:
        st.error(f"❌ Download fehlgeschlagen: {str(e)}")

# 🔥 **Daten laden**
st.write("📥 **Daten werden geladen...**")

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

# **Erste Datenprüfung**
st.write("📌 **Importierte Datenstruktur:**")
st.write("🔹 **reddit_merged.csv**")
st.write(df_crypto.head())

st.write("🔹 **crypto_prices.csv**")
st.write(df_prices.head())

st.write("✅ **Datenimport abgeschlossen!**")
