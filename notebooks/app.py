import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt

# 📌 Google Drive Direkt-Link für die CSV-Datei (ersetze mit deiner File-ID)
MERGED_CSV_ID = "102W-f_u58Jvx9xBAv4IaYrOY6txk-XKL"

# 📌 Lokale Datei für die heruntergeladene CSV
MERGED_CSV = "reddit_merged.csv"

# 📌 Funktion zum Herunterladen der Datei aus Google Drive
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

    # 🔹 Konvertiere das Datum
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
    # 🔹 **GRID-Layout für 4 Visualisierungen**
    col1, col2 = st.columns(2)  # Erste Zeile mit 2 Charts
    col3, col4 = st.columns(2)  # Zweite Zeile mit 2 Charts

    # 🔹 **1️⃣ Häufig diskutierte Coins**
    with col1:
        st.subheader("🔥 Top 10 meist erwähnte Kryptowährungen")
        crypto_counts = df_merged["crypto"].value_counts().head(10)
        st.bar_chart(crypto_counts)

    # 🔹 **2️⃣ Sentiment-Verteilung pro Coin**
    with col2:
        st.subheader("💡 Sentiment-Verteilung der Coins")
        sentiment_distribution = df_merged.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
        st.bar_chart(sentiment_distribution)

    # 🔹 **3️⃣ Verhältnis Positiv vs. Negativ (Matplotlib Pie-Chart)**
    with col3:
        st.subheader("📈 Verhältnis Positiv vs. Negativ")

        # Entferne neutrale Werte
        sentiment_ratio = df_merged[df_merged["sentiment"] != "neutral"].groupby("sentiment").size()

        # **Pie-Chart mit Matplotlib**
        fig, ax = plt.subplots()
        ax.pie(
            sentiment_ratio, 
            labels=sentiment_ratio.index, 
            autopct="%1.1f%%", 
            startangle=90, 
            colors=["green", "red"]
        )
        ax.axis("equal")  # Kreisförmige Darstellung
        st.pyplot(fig)  # **Streamlit Pie-Chart anzeigen**

    # 🔹 **4️⃣ Interaktive Sentiment-Entwicklung**
    with col4:
        st.subheader("📅 Sentiment-Entwicklung über Zeit")

        # **Dropdown-Menü für Krypto-Auswahl**
        crypto_options = df_merged["crypto"].unique().tolist()
        selected_crypto = st.selectbox("Wähle eine Kryptowährung:", crypto_options, index=0)

        # **Nur gewählte Krypto & ohne neutrales Sentiment**
        df_filtered = df_merged[(df_merged["crypto"] == selected_crypto) & (df_merged["sentiment"] != "neutral")]

        # **Sentiment aggregieren**
        df_time = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)

        # **Interaktive Liniendiagramm-Visualisierung**
        st.line_chart(df_time)

    st.write("🔄 Dashboard wird regelmäßig mit neuen Daten aktualisiert!")
