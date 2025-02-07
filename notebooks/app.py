import pandas as pd
import streamlit as st

# 📌 Direkt-Download-Links aus Google Drive (ersetze mit deinen File-IDs)
POSTS_CSV_URL = "https://drive.google.com/file/d/100PIX5Ev3WumQcRMOyxjuaJ9GUe6yO0d/view?usp=drive_link"
COMMENTS_CSV_URL = "https://drive.google.com/file/d/102AKIf8InQgHgIGMwgzeFYkNN6bCUGaX/view?usp=drive_link"

# 📌 Laden der Daten
@st.cache_data
def load_data():
    df_posts = pd.read_csv(POSTS_CSV_URL, sep="|", encoding="utf-8-sig", on_bad_lines="skip")
    df_comments = pd.read_csv(COMMENTS_CSV_URL, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # Mergen
    df_merged = df_comments.merge(df_posts, on="post_id", how="left")
    df_merged.dropna(inplace=True)

    return df_merged

df_merged = load_data()

st.title("📊 Krypto-Sentiment Dashboard")
st.write(df_merged.head())  # Test-Anzeige der Daten
