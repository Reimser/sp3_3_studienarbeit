import streamlit as st
import pandas as pd
import gdown
import os

# 📌 Google Drive Direkt-Link (ersetze mit deiner File-ID)
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
    df = pd.read_csv(MERGED_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # 🔹 Datumsformat korrigieren
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df

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

    # 🔹 3️⃣ **Interaktive Sentiment-Entwicklung**
    st.subheader("📅 Sentiment-Entwicklung über die Zeit")

    # **Dropdown-Menü für Kryptowährungsauswahl**
    crypto_options = df_merged["crypto"].unique().tolist()
    selected_crypto = st.selectbox("Wähle eine Kryptowährung:", crypto_options, index=0)

    # **Daten für gewählte Kryptowährung filtern**
    df_filtered = df_merged[df_merged["crypto"] == selected_crypto]

    # **Sentiment aggregieren**
    df_time = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)

    # **Interaktive Liniendiagramm-Visualisierung**
    st.line_chart(df_time)

    st.write("🔄 Dashboard wird regelmäßig mit neuen Daten aktualisiert!")
