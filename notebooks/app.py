import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Crypto Sentiment Dashboard", layout="centered")

# 📌 Google Drive File ID for the latest dataset
MERGED_CSV_ID = "10Ft5DpBI-B3tBfU5wOVzGRj_vwT7TNxa"

# 📌 Local filename for the downloaded CSV
MERGED_CSV = "reddit_merged.csv"

# 🔹 Function to Download CSV from Google Drive
@st.cache_data
def download_csv(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output, quiet=False)

# 🔹 Function to Load Data
@st.cache_data
def load_data():
    if not os.path.exists(MERGED_CSV):
        download_csv(MERGED_CSV_ID, MERGED_CSV)

    df_crypto = pd.read_csv(MERGED_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # 🔍 Debugging: Check available columns
    print("📝 Columns in df_crypto:", df_crypto.columns.tolist())

    # 🔹 Ensure a valid date column exists
    possible_date_cols = [col for col in df_crypto.columns if "date" in col.lower()]
    if possible_date_cols:
        df_crypto["date"] = pd.to_datetime(df_crypto[possible_date_cols[0]], errors="coerce")
    else:
        raise KeyError(f"⚠️ No valid 'date' column found! Available columns: {df_crypto.columns.tolist()}")

    return df_crypto

# 📌 Load Data
df_crypto = load_data()

# 📊 **Dashboard Title**
st.title("📊 Crypto Sentiment Dashboard")

# 🔄 **Refresh Button**
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.experimental_rerun()

if df_crypto.empty:
    st.warning("⚠️ No Crypto Data Available.")
else:
    # 🔹 **1️⃣ Most Discussed Cryptos**
    st.subheader("🔥 Top 10 Most Mentioned Cryptocurrencies")
    crypto_counts = df_crypto["crypto"].value_counts().head(10)
    st.bar_chart(crypto_counts)

    # 🔹 **2️⃣ Sentiment Distribution per Crypto**
    st.subheader("💡 Sentiment Distribution of Cryptos")
    sentiment_distribution = df_crypto.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
    st.bar_chart(sentiment_distribution)

    # 🔹 **3️⃣ Sentiment Trend Over Time**
    st.subheader("📅 Sentiment Trend Over Time")
    crypto_options = df_crypto["crypto"].unique().tolist()
    selected_crypto = st.selectbox("Choose a Cryptocurrency:", crypto_options, index=0)

    df_filtered = df_crypto[(df_crypto["crypto"] == selected_crypto) & (df_crypto["sentiment"] != "neutral")]
    df_time = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)

    st.line_chart(df_time)

    st.write("🔄 Dashboard is regularly updated with new data!")