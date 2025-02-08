import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt

# 📌 Google Drive Direkt-Link (ersetze mit deiner File-ID)
MERGED_CSV_ID = "102W-f_u58Jvx9xBAv4IaYrOY6txk-XKL"

# 📌 Lokale Datei für die heruntergeladene CSV
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


# 📌 Daten laden
df_merged = load_data()

# 📊 Dashboard Titel
st.title("📊 Krypto-Sentiment Dashboard")

# 🔹 Überprüfen, ob Daten geladen wurden
if df_merged.empty:
    st.warning("⚠️ Keine Daten verfügbar. Überprüfe Google Drive oder lade neue Daten hoch.")
else:
    # ➖➖➖ **Erste Reihe: Meist erwähnte Coins & Sentiment-Verteilung** ➖➖➖
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 Meist erwähnte Kryptowährungen")
        crypto_counts = df_merged["crypto"].value_counts().head(10)
        
        fig, ax = plt.subplots(figsize=(5,3))
        crypto_counts.plot(kind="bar", ax=ax, color="blue")
        ax.set_ylabel("Anzahl")
        ax.set_xlabel("Kryptowährung")
        st.pyplot(fig)

    with col2:
        st.subheader("💡 Sentiment-Verteilung pro Coin")
        sentiment_distribution = df_merged.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
        
        fig, ax = plt.subplots(figsize=(5,3))
        sentiment_distribution.plot(kind="bar", stacked=True, ax=ax, colormap="coolwarm")
        ax.set_ylabel("Anzahl")
        st.pyplot(fig)

    # ➖➖➖ **Zweite Reihe: Verhältnis Positiv/Negativ & Sentiment-Entwicklung** ➖➖➖
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("📈 Verhältnis Positiv vs. Negativ")
        sentiment_ratio = df_merged[df_merged["sentiment"] != "neutral"].groupby("sentiment").size()
        
        fig, ax = plt.subplots(figsize=(5,3))
        ax.pie(sentiment_ratio, labels=sentiment_ratio.index, autopct="%1.1f%%", startangle=90, colors=["green", "red"])
        ax.axis("equal")
        st.pyplot(fig)

    with col4:
        st.subheader("📅 Sentiment-Entwicklung")
        crypto_options = df_merged["crypto"].unique().tolist()
        selected_crypto = st.selectbox("Wähle eine Kryptowährung:", crypto_options, index=0)
        
        df_filtered = df_merged[(df_merged["crypto"] == selected_crypto) & (df_merged["sentiment"] != "neutral")]
        df_time = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
        
        fig, ax = plt.subplots(figsize=(5,3))
        df_time.plot(ax=ax)
        ax.set_ylabel("Anzahl")
        ax.set_xlabel("Datum")
        st.pyplot(fig)

    st.write("🔄 Dashboard wird regelmäßig mit neuen Daten aktualisiert!")
