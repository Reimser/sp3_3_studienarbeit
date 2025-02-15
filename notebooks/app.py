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
