import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Google Drive Direkt-Link für CSV (ersetze mit deiner File-ID)
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

if df_merged.empty:
    st.warning("⚠️ Keine Daten verfügbar. Überprüfe Google Drive oder lade neue Daten hoch.")
else:
    # 🔹 **GRID-Layout für Visualisierungen**
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # 🔹 **1️⃣ Häufig diskutierte Coins**
    with col1:
        st.subheader("🔥 Meist erwähnte Kryptowährungen")
        crypto_counts = df_merged["crypto"].value_counts().head(10)

        fig, ax = plt.subplots(figsize=(5,3))
        crypto_counts.plot(kind="bar", ax=ax, color="blue")
        ax.set_ylabel("Anzahl")
        ax.set_xlabel("Kryptowährung")
        st.pyplot(fig)

    # 🔹 **2️⃣ Sentiment-Verteilung pro Coin**
    with col2:
        st.subheader("💡 Sentiment-Verteilung der Coins")
        sentiment_distribution = df_merged.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)

        fig, ax = plt.subplots(figsize=(5,3))
        sentiment_distribution.plot(kind="bar", stacked=True, ax=ax, colormap="coolwarm")
        ax.set_ylabel("Anzahl")
        st.pyplot(fig)

    # 🔹 **3️⃣ Dunkler Pie-Chart: Verhältnis Positiv vs. Negativ**
    with col3:
        st.subheader("📈 Positiv vs. Negativ")

        sentiment_ratio = df_merged[df_merged["sentiment"] != "neutral"].groupby("sentiment").size()

        fig, ax = plt.subplots(figsize=(5,3), facecolor="black")
        ax.set_facecolor("black")

        ax.pie(
            sentiment_ratio, 
            labels=sentiment_ratio.index, 
            autopct="%1.1f%%", 
            startangle=90, 
            colors=["green", "red"],
            textprops={'color':"white"}  # Text weiß für dunklen Hintergrund
        )
        ax.axis("equal")  # Kreisförmig halten
        st.pyplot(fig)

    # 🔹 **4️⃣ Interaktive Sentiment-Entwicklung**
    with col4:
        st.subheader("📅 Sentiment-Trend über Zeit")

        crypto_options = df_merged["crypto"].unique().tolist()
        selected_crypto = st.selectbox("🔎 Wähle eine Kryptowährung:", crypto_options, index=0)

        df_filtered = df_merged[(df_merged["crypto"] == selected_crypto) & (df_merged["sentiment"] != "neutral")]
        df_time = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)

        fig, ax = plt.subplots(figsize=(5,3))
        df_time.plot(ax=ax)
        ax.set_ylabel("Anzahl")
        ax.set_xlabel("Datum")
        st.pyplot(fig)

    # ➖➖➖ **Zusätzliche Analysen** ➖➖➖
    st.subheader("📊 Erweiterte Analysen")

    # **🔹 Durchschnittlicher Sentiment-Score pro Coin**
    df_sentiment_scores = df_merged.groupby("crypto")["sentiment_confidence"].mean().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(7,3))
    df_sentiment_scores.plot(kind="bar", color="purple", ax=ax)
    ax.set_ylabel("Ø Sentiment-Score")
    st.pyplot(fig)

    # **🔹 Heatmap: Sentiment über Tageszeiten**
    df_merged["hour"] = df_merged["date"].dt.hour
    df_hourly_sentiment = df_merged.pivot_table(index="hour", columns="sentiment", aggfunc="size", fill_value=0)

    fig, ax = plt.subplots(figsize=(7,3))
    sns.heatmap(df_hourly_sentiment, cmap="coolwarm", linewidths=0.5, ax=ax)
    st.pyplot(fig)

    # **🔹 Volatilität des Sentiments**
    df_sentiment_std = df_merged.groupby("crypto")["sentiment_confidence"].std().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(7,3))
    df_sentiment_std.plot(kind="bar", color="orange", ax=ax)
    ax.set_ylabel("Sentiment-Volatilität")
    st.pyplot(fig)

    st.write("🔄 Dashboard wird regelmäßig mit neuen Daten aktualisiert!")
