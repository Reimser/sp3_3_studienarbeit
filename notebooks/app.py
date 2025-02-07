import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 📌 Datei-Pfade (anpassen, falls nötig)
POSTS_CSV = "G:/Meine Ablage/reddit/reddit_posts.csv"
COMMENTS_CSV = "G:/Meine Ablage/reddit/reddit_comments.csv"

# 📌 Laden der Daten mit Caching für bessere Performance
@st.cache_data
def load_data():
    # Daten laden
    df_posts = pd.read_csv(POSTS_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")
    df_comments = pd.read_csv(COMMENTS_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # 📌 Merge auf Basis von `post_id`, um Kommentare den Posts zuzuordnen
    df_merged = df_comments.merge(df_posts, on="post_id", how="left")

    # 🔹 Fehlende Werte entfernen (optional)
    df_merged.dropna(inplace=True)

    # 🔹 Sicherstellen, dass `date` im richtigen Format ist
    df_merged["date"] = pd.to_datetime(df_merged["date"])

    return df_merged

df_merged = load_data()

# 📊 Dashboard Titel
st.title("📊 Krypto-Sentiment Dashboard")

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
