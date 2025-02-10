import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Financial Data Dashboard", layout="centered")

# 📌 Google Drive Direct Links (Replace with your File ID for Crypto Data)
MERGED_CRYPTO_CSV_ID = "10Ft5DpBI-B3tBfU5wOVzGRj_vwT7TNxa"

# 📌 Local File Paths for Downloaded CSVs
MERGED_CRYPTO_CSV = "reddit_merged.csv"

# 🔹 Function to Download CSV from Google Drive
@st.cache_data
def download_csv(file_id, output):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output, quiet=False)

# 🔹 Function to Load Data
@st.cache_data
def load_crypto_data():
    # 🔹 Load Crypto Data
    if not os.path.exists(MERGED_CRYPTO_CSV):
        download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)

    df_crypto = pd.read_csv(MERGED_CRYPTO_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # 🔹 Ensure "date" column exists
    if "date" not in df_crypto.columns:
        if "date_x" in df_crypto.columns:
            df_crypto["date"] = df_crypto["date_x"]
        elif "date_y" in df_crypto.columns:
            df_crypto["date"] = df_crypto["date_y"]
        else:
            raise KeyError("⚠️ No valid 'date' column found! Check the CSV.")

    df_crypto["date"] = pd.to_datetime(df_crypto["date"], errors="coerce")

    # 🔹 Convert Sentiment to Numerical Values
    sentiment_mapping = {"positive": 1, "neutral": 0, "negative": -1, "bullish": 1, "bearish": -1}
    df_crypto["sentiment_score"] = df_crypto["sentiment"].map(sentiment_mapping).fillna(0)

    return df_crypto

# 📌 Load Crypto Data
df_crypto = load_crypto_data()

# 📊 **Multi-Tab Navigation**
tab_home, tab_crypto, tab_stocks = st.tabs(["🏠 Home", "📈 Crypto Data", "💹 Stock Data"])

# 🔹 **🏠 HOME (README)**
with tab_home:
    st.title("📊 Reims Financial Dashboard")
    st.markdown("""
        **This dashboard provides insights into financial data on Reddit:**
        - 📈 **Cryptocurrencies:** Sentiment Analysis, Activity & Trends  
        - 💹 **Stock Market:** (Coming Soon)  
        
        Use the tabs to explore different datasets!  
        """)

# 🔹 **📈 CRYPTOCURRENCY ANALYSIS**
with tab_crypto:
    st.title("📈 Crypto Sentiment Dashboard")

    if df_crypto.empty:
        st.warning("⚠️ No Crypto Data Available.")
    else:
        # 🔹 **1️⃣ Most Mentioned Cryptocurrencies**
        st.subheader("🔥 Top 10 Most Mentioned Cryptocurrencies")
        crypto_counts = df_crypto["crypto"].value_counts().head(10)
        st.bar_chart(crypto_counts)

        # 🔹 **2️⃣ Sentiment Distribution per Cryptocurrency**
        st.subheader("💡 Sentiment Distribution of Cryptos")
        sentiment_distribution = df_crypto.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
        st.bar_chart(sentiment_distribution)

        # 🔹 **3️⃣ Ratio of Positive vs. Negative (Pie Chart)**
        st.subheader("📈 Ratio of Positive vs. Negative Sentiments")
        sentiment_ratio = df_crypto[df_crypto["sentiment"] != "neutral"].groupby("sentiment").size()

        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_facecolor("#2E2E2E")  # Dark background
        fig.patch.set_facecolor("#2E2E2E")

        ax.pie(
            sentiment_ratio,
            labels=sentiment_ratio.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=["green", "red"]
        )
        ax.axis("equal")  # Circular layout
        st.pyplot(fig)

        # 🔹 **4️⃣ Sentiment Trends Over Time (Interactive)**
        st.subheader("📅 Sentiment Trends Over Time")
        crypto_options = df_crypto["crypto"].unique().tolist()
        selected_crypto = st.selectbox("Choose a Cryptocurrency:", crypto_options, index=0)

        df_filtered = df_crypto[(df_crypto["crypto"] == selected_crypto) & (df_crypto["sentiment"] != "neutral")]

        if "date" in df_filtered.columns:
            df_time = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
            st.line_chart(df_time)
        else:
            st.error("⚠️ 'date' column is missing, check data processing.")

        # 🔹 **5️⃣ Sentiment Heatmap**
        st.subheader("🌡️ Sentiment Heatmap for Top Coins")
        sentiment_counts = df_crypto[df_crypto["sentiment"] != "neutral"].groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(sentiment_counts, annot=True, fmt="d", cmap="RdYlGn", linewidths=0.5, ax=ax)
        st.pyplot(fig)

        # 🔹 **6️⃣ Average Sentiment per Coin**
        st.subheader("📊 Average Sentiment per Coin")
        avg_sentiment = df_crypto.groupby("crypto")["sentiment_score"].mean().sort_values()

        fig, ax = plt.subplots(figsize=(10, 5))
        avg_sentiment.plot(kind="bar", color=["red" if x < 0 else "green" for x in avg_sentiment], ax=ax)
        ax.set_ylabel("Average Sentiment")
        st.pyplot(fig)

        # 🔹 **7️⃣ Sentiment Volatility per Coin**
        st.subheader("📉 Sentiment Volatility per Coin")
        sentiment_std = df_crypto.groupby("crypto")["sentiment_score"].std().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(10, 5))
        sentiment_std.plot(kind="bar", color="blue", ax=ax)
        ax.set_ylabel("Sentiment Standard Deviation")
        st.pyplot(fig)

        # 🔹 **8️⃣ Activity Over Time with Multi-Selection**
        st.subheader("📅 Activity Over Time per Coin")

        # Multi-Select for Multiple Cryptos
        selected_cryptos = st.multiselect("Choose One or More Cryptocurrencies:", crypto_options, default=crypto_options[:3])

        if selected_cryptos:
            df_activity_filtered = df_crypto[df_crypto["crypto"].isin(selected_cryptos)]
            activity_per_day = df_activity_filtered.groupby(["date", "crypto"]).size().unstack(fill_value=0)
            st.line_chart(activity_per_day)

# 🔹 **💹 STOCK MARKET ANALYSIS (Coming Soon)**
with tab_stocks:
    st.title("💹 Stock Market Analysis")
    st.subheader("🚧 This section is under construction. 🚧")
    st.markdown("""
        The stock market analysis feature is currently in development.  
        Stay tuned for future updates! 📈
        """)
