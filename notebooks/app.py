import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt

# 📌 Maximale Breite aktivieren
st.set_page_config(layout="wide")

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
    # 📌 **Zwei breite Spalten für größere Diagramme**
    col1, col2 = st.columns([2, 2])  # Breite optimieren

    with col1:
        st.subheader("🔥 Meist erwähnte Kryptowährungen")
        crypto_counts = df_merged["crypto"].value_counts().head(10)
        st.bar_chart(crypto_counts, use_container_width=True)

        st.subheader("📅 Sentiment-Entwicklung über Zeit")
        crypto_options = df_merged["crypto"].unique().tolist()
        selected_crypto = st.selectbox("Wähle eine Kryptowährung:", crypto_options, index=0)
        df_filtered = df_merged[(df_merged["crypto"] == selected_crypto) & (df_merged["sentiment"] != "neutral")]
        df_time = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
        st.line_chart(df_time, use_container_width=True)

    with col2:
        st.subheader("💡 Sentiment-Verteilung der Coins")
        sentiment_distribution = df_merged.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
        st.bar_chart(sentiment_distribution, use_container_width=True)

        st.subheader("📈 Verhältnis Positiv vs. Negativ")
        sentiment_ratio = df_merged[df_merged["sentiment"] != "neutral"].groupby("sentiment").size()
        fig, ax = plt.subplots(figsize=(6, 6))  # Größerer Pie-Chart
        ax.pie(sentiment_ratio, labels=sentiment_ratio.index, autopct="%1.1f%%", startangle=90, colors=["green", "red"])
        ax.axis("equal")
        st.pyplot(fig)

    st.write("🔄 Dashboard wird regelmäßig mit neuen Daten aktualisiert!")
