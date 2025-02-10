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

    # 🔹 Keep both date columns
    if "date_x" in df_crypto.columns:
        df_crypto["comment_date"] = pd.to_datetime(df_crypto["date_x"], errors="coerce")
    else:
        raise KeyError(f"⚠️ No valid 'date_x' column found! Available columns: {df_crypto.columns.tolist()}")

    if "date_y" in df_crypto.columns:
        df_crypto["post_date"] = pd.to_datetime(df_crypto["date_y"], errors="coerce")
    else:
        raise KeyError(f"⚠️ No valid 'date_y' column found! Available columns: {df_crypto.columns.tolist()}")

    # Convert Sentiment Labels into Numeric Scores
    df_crypto["sentiment_score"] = df_crypto["sentiment"].map({"bullish": 1, "neutral": 0, "bearish": -1})

    return df_crypto

# 📌 Load Data
df_crypto = load_data()

# 🔄 **Refresh Button**
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.experimental_rerun()

# 📊 **Dashboard Title**
st.title("📊 Crypto Sentiment Dashboard")

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

    # 🔹 **3️⃣ Sentiment Trend Over Time (Based on Comments)**
    st.subheader("📅 Sentiment Trend Over Time (Comments)")
    crypto_options = df_crypto["crypto"].unique().tolist()
    selected_crypto = st.selectbox("Choose a Cryptocurrency:", crypto_options, index=0)

    df_filtered = df_crypto[(df_crypto["crypto"] == selected_crypto) & (df_crypto["sentiment"] != "neutral")]

    if df_filtered.empty:
        st.warning("⚠️ No sentiment data available for the selected cryptocurrency.")
    else:
        df_time = df_filtered.groupby(["comment_date", "sentiment"]).size().unstack(fill_value=0)
        st.line_chart(df_time)

    # 🔹 **4️⃣ Post vs. Comment Activity Over Time**
    st.subheader("📅 Post vs. Comment Activity Over Time")
    df_activity = df_crypto.groupby(["post_date", "comment_date"]).size().unstack(fill_value=0)
    st.line_chart(df_activity)

    # 🔹 **5️⃣ Sentiment Pie Chart (Excluding Neutral)**
    st.subheader("📈 Sentiment Ratio (Bullish vs. Bearish)")
    sentiment_ratio = df_crypto[df_crypto["sentiment"] != "neutral"].groupby("sentiment").size()

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_facecolor("#2E2E2E")  # Dark Background
    fig.patch.set_facecolor("#2E2E2E")

    ax.pie(
        sentiment_ratio,
        labels=sentiment_ratio.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=["green", "red"]
    )
    ax.axis("equal")  # Equal aspect ratio for a perfect circle
    st.pyplot(fig)

    # 🔹 **6️⃣ Sentiment Heatmap of Top Cryptos**
    st.subheader("🌡️ Sentiment Heatmap of Top Cryptos")
    sentiment_counts = df_crypto[df_crypto["sentiment"] != "neutral"].groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(sentiment_counts, annot=True, fmt="d", cmap="RdYlGn", linewidths=0.5, ax=ax)
    st.pyplot(fig)

    # 🔹 **7️⃣ Average Sentiment Score per Crypto**
    st.subheader("📊 Average Sentiment Score per Crypto")
    avg_sentiment = df_crypto.groupby("crypto")["sentiment_score"].mean().sort_values()

    fig, ax = plt.subplots(figsize=(10, 5))
    avg_sentiment.plot(kind="bar", color=["red" if x < 0 else "green" for x in avg_sentiment], ax=ax)
    ax.set_ylabel("Average Sentiment Score")
    st.pyplot(fig)

    # 🔹 **8️⃣ Sentiment Volatility per Crypto**
    st.subheader("📉 Sentiment Volatility per Crypto")
    sentiment_std = df_crypto.groupby("crypto")["sentiment_score"].std().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    sentiment_std.plot(kind="bar", color="blue", ax=ax)
    ax.set_ylabel("Sentiment Standard Deviation")
    st.pyplot(fig)

    # 🔹 **9️⃣ Multi-Selection Activity Over Time**
    st.subheader("📅 Multi-Selection Activity Over Time")
    selected_cryptos = st.multiselect("Choose one or more Cryptocurrencies:", crypto_options, default=crypto_options[:3])

    if selected_cryptos:
        df_activity_filtered = df_crypto[df_crypto["crypto"].isin(selected_cryptos)]
        activity_per_day = df_activity_filtered.groupby(["comment_date", "crypto"]).size().unstack(fill_value=0)
        st.line_chart(activity_per_day)

    st.write("🔄 Dashboard is regularly updated with new data!")
