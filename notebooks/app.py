import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit-Konfiguration für zentriertes Layout
st.set_page_config(page_title="Krypto-Sentiment Dashboard", layout="centered")

# 📌 Google Drive Direkt-Link für die CSV-Datei (ersetze mit deiner File-ID)
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

    # 🔹 Sentiment in numerische Werte umwandeln
    df["sentiment_score"] = df["sentiment"].map({"positive": 1, "neutral": 0, "negative": -1})

    return df

# 📌 Daten laden
df_merged = load_data()

# 📊 Dashboard Titel
st.title("📊 Krypto-Sentiment Dashboard")

if df_merged.empty:
    st.warning("⚠️ Keine Daten verfügbar. Überprüfe Google Drive oder lade neue Daten hoch.")
else:
    # 🔹 **1️⃣ Häufig diskutierte Coins**
    st.subheader("🔥 Top 10 meist erwähnte Kryptowährungen")
    crypto_counts = df_merged["crypto"].value_counts().head(10)
    st.bar_chart(crypto_counts)

    # 🔹 **2️⃣ Sentiment-Verteilung pro Coin**
    st.subheader("💡 Sentiment-Verteilung der Coins")
    sentiment_distribution = df_merged.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
    st.bar_chart(sentiment_distribution)

    # 🔹 **3️⃣ Verhältnis Positiv vs. Negativ (Matplotlib Pie-Chart)**
    st.subheader("📈 Verhältnis Positiv vs. Negativ")
    sentiment_ratio = df_merged[df_merged["sentiment"] != "neutral"].groupby("sentiment").size()

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_facecolor("#2E2E2E")  # Dunkler Hintergrund
    fig.patch.set_facecolor("#2E2E2E")

    ax.pie(
        sentiment_ratio,
        labels=sentiment_ratio.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=["green", "red"]
    )
    ax.axis("equal")  # Kreisförmige Darstellung
    st.pyplot(fig)

    # 🔹 **4️⃣ Interaktive Sentiment-Entwicklung**
    st.subheader("📅 Sentiment-Entwicklung über Zeit")
    crypto_options = df_merged["crypto"].unique().tolist()
    selected_crypto = st.selectbox("Wähle eine Kryptowährung:", crypto_options, index=0)

    df_filtered = df_merged[(df_merged["crypto"] == selected_crypto) & (df_merged["sentiment"] != "neutral")]
    df_time = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)

    st.line_chart(df_time)

    # 🔹 **5️⃣ Heatmap: Sentiment-Verteilung**
    st.subheader("🌡️ Sentiment-Heatmap der Top Coins")
    sentiment_counts = df_merged[df_merged["sentiment"] != "neutral"].groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(sentiment_counts, annot=True, fmt="d", cmap="RdYlGn", linewidths=0.5, ax=ax)
    st.pyplot(fig)

    # 🔹 **6️⃣ Durchschnittliches Sentiment pro Coin**
    st.subheader("📊 Durchschnittliches Sentiment pro Coin")
    avg_sentiment = df_merged.groupby("crypto")["sentiment_score"].mean().sort_values()

    fig, ax = plt.subplots(figsize=(10, 5))
    avg_sentiment.plot(kind="bar", color=["red" if x < 0 else "green" for x in avg_sentiment], ax=ax)
    ax.set_ylabel("Durchschnittliches Sentiment")
    st.pyplot(fig)

    # 🔹 **7️⃣ Volatilität des Sentiments pro Coin**
    st.subheader("📉 Sentiment-Volatilität pro Coin")
    sentiment_std = df_merged.groupby("crypto")["sentiment_score"].std().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    sentiment_std.plot(kind="bar", color="blue", ax=ax)
    ax.set_ylabel("Sentiment-Standardabweichung")
    st.pyplot(fig)

    # 🔹 **8️⃣ Aktivität pro Coin über Zeit mit Multi-Selection**
    st.subheader("📅 Aktivität pro Coin über die Zeit")

    # Multi-Select für mehrere Kryptowährungen
    selected_cryptos = st.multiselect("Wähle eine oder mehrere Kryptowährungen:", crypto_options, default=crypto_options[:3])

    if selected_cryptos:
        df_activity_filtered = df_merged[df_merged["crypto"].isin(selected_cryptos)]
        activity_per_day = df_activity_filtered.groupby(["date", "crypto"]).size().unstack(fill_value=0)
        st.line_chart(activity_per_day)

    st.write("🔄 Dashboard wird regelmäßig mit neuen Daten aktualisiert!")
