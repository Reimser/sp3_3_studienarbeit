import streamlit as st
import pandas as pd
import gdown
import os

# 📌 Google Drive Direkt-Link (ersetze mit deinem File-ID)
MERGED_CSV_ID = "102W-f_u58Jvx9xBAv4IaYrOY6txk-XKL"

# 📌 Lokale Datei für die heruntergeladene CSV
MERGED_CSV = "reddit_merged.csv"

# 📌 Funktion zum Herunterladen der Datei aus Google Drive
@st.cache_data
def download_csv(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output, quiet=False)

# 📌 Funktion zum Laden der Daten
@st.cache_data
def load_data():
    # 🔹 CSV herunterladen, falls nicht vorhanden
    if not os.path.exists(MERGED_CSV):
        download_csv(MERGED_CSV_ID, MERGED_CSV)

    # 🔹 CSV einlesen
    df_merged = pd.read_csv(MERGED_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # 🔹 Sicherstellen, dass `date` im richtigen Format ist
    if "date_x" in df_merged.columns:
        df_merged["date"] = pd.to_datetime(df_merged["date_x"])
    elif "date_y" in df_merged.columns:
        df_merged["date"] = pd.to_datetime(df_merged["date_y"])
    else:
        st.error("⚠️ Keine gültige 'date'-Spalte gefunden!")


    return df_merged

# 📌 Daten laden
df_merged = load_data()

# 📊 Dashboard Titel
st.title("📊 Krypto-Sentiment Dashboard")

# 🔹 Überprüfen, ob Daten geladen wurden
if df_merged.empty:
    st.warning("⚠️ Keine Daten verfügbar. Überprüfe Google Drive oder lade neue Daten hoch.")
else:
    # 🔹 1️⃣ Häufig diskutierte Coins
    st.subheader("Top 10 meist erwähnte Kryptowährungen")
    crypto_counts = df_merged["crypto"].value_counts().head(10)
    st.bar_chart(crypto_counts)

    # 🔹 2️⃣ Sentiment-Analyse pro Coin
    st.subheader("Sentiment-Verteilung pro Kryptowährung")
    sentiment_distribution = df_merged.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
    st.bar_chart(sentiment_distribution)

    # 🔹 3️⃣ Sentiment-Entwicklung über die Zeit
    st.subheader("📅 Sentiment-Entwicklung über die Zeit")
    df_time = df_merged.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
    st.line_chart(df_time)

    st.write("🔄 Dashboard wird regelmäßig mit neuen Daten aktualisiert!")
