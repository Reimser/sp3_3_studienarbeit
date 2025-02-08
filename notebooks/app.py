import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt

# 📌 Google Drive Direkt-Link für die CSV-Datei (ersetze mit deiner File-ID)
MERGED_CSV_ID = "102W-f_u58Jvx9xBAv4IaYrOY6txk-XKL"
MERGED_CSV = "reddit_merged.csv"

@st.cache_data
def download_csv(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output, quiet=False)

@st.cache_data
def load_data():
    if not os.path.exists(MERGED_CSV):
        download_csv(MERGED_CSV_ID, MERGED_CSV)

    df = pd.read_csv(MERGED_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # 🔹 Überprüfen, ob "date" vorhanden ist
    if "date" not in df.columns:
        if "date_x" in df.columns:
            df["date"] = df["date_x"]
        elif "date_y" in df.columns:
            df["date"] = df["date_y"]
        else:
            raise KeyError("⚠️ Keine gültige 'date'-Spalte gefunden! Überprüfe die CSV.")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df

df_merged = load_data()

st.title("📊 Krypto-Sentiment Dashboard")

if df_merged.empty:
    st.warning("⚠️ Keine Daten verfügbar. Überprüfe Google Drive oder lade neue Daten hoch.")
else:
    # 🔹 1️⃣ **Meist erwähnte Kryptowährungen**
    st.subheader("🔥 Meist erwähnte Kryptowährungen")
    crypto_counts = df_merged["crypto"].value_counts().head(10)
    st.bar_chart(crypto_counts, use_container_width=False)  # 🔹 Kleinere Breite

    # 🔹 2️⃣ **Sentiment-Verteilung der Coins**
    st.subheader("💡 Sentiment-Verteilung pro Kryptowährung")
    sentiment_distribution = df_merged.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
    st.bar_chart(sentiment_distribution, use_container_width=False)  # 🔹 Kleinere Breite

    # 🔹 3️⃣ **Verhältnis Positiv vs. Negativ**
    st.subheader("📈 Verhältnis von positivem & negativem Sentiment")
    sentiment_ratio = df_merged[df_merged["sentiment"] != "neutral"].groupby("sentiment").size()
    
    fig, ax = plt.subplots(figsize=(4, 4))  # 🔹 Kleinere Pie-Chart-Größe
    ax.pie(sentiment_ratio, labels=sentiment_ratio.index, autopct="%1.1f%%", startangle=90, colors=["green", "red"])
    ax.axis("equal")
    st.pyplot(fig)

    # 🔹 4️⃣ **Interaktive Sentiment-Entwicklung**
    st.subheader("📅 Sentiment-Entwicklung über Zeit")

    # **Dropdown-Menü für Kryptowährungsauswahl**
    crypto_options = df_merged["crypto"].unique().tolist()
    selected_crypto = st.selectbox("Wähle eine Kryptowährung:", crypto_options, index=0)

    # **Daten für gewählte Kryptowährung filtern**
    df_filtered = df_merged[(df_merged["crypto"] == selected_crypto) & (df_merged["sentiment"] != "neutral")]
    df_time = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)

    # **Liniendiagramm der Sentiment-Entwicklung**
    st.line_chart(df_time, use_container_width=False)  # 🔹 Kleinere Breite

    st.write("🔄 Dashboard wird regelmäßig mit neuen Daten aktualisiert!")
