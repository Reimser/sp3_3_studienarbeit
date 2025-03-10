import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Reddit Crypto Dashboard", layout="wide")

# 📥 **Google Drive File IDs**
MERGED_CRYPTO_CSV_ID = "12ugApKWh1cJYONcLanpHND9gIdobh-wA"
CRYPTO_PRICES_CSV_ID = "11k9wiflOkqg2DayEgn7iPqNPHC5Qatht"

# 📌 **Lokale Dateinamen**
MERGED_CRYPTO_CSV = "app.csv"
CRYPTO_PRICES_CSV = "crypto_prices.csv"

# 🔥 **Daten herunterladen**
def download_csv(file_id, output):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        gdown.download(url, output, quiet=False, fuzzy=True)  # ✅ Alternative Download-Methode
        if not os.path.exists(output) or os.path.getsize(output) == 0:
            st.error(f"❌ Fehler: {output} wurde nicht korrekt heruntergeladen!")
    except Exception as e:
        st.error(f"❌ Download fehlgeschlagen: {str(e)}")

# 📥 **Daten laden**
download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)
download_csv(CRYPTO_PRICES_CSV_ID, CRYPTO_PRICES_CSV)

# 📌 **CSV-Dateien einlesen**
def load_csv(filepath):
    if not os.path.exists(filepath):
        st.error(f"❌ Datei nicht gefunden: {filepath}")
        return pd.DataFrame()
    try:
        return pd.read_csv(filepath, sep="|", encoding="utf-8-sig", on_bad_lines="skip")
    except Exception as e:
        st.error(f"❌ Fehler beim Laden von {filepath}: {str(e)}")
        return pd.DataFrame()

df_crypto = load_csv(MERGED_CRYPTO_CSV)
df_prices = load_csv(CRYPTO_PRICES_CSV)

# 📌 **Debugging: Dateiinhalt prüfen**
if df_crypto.empty:
    st.error("❌ Die CSV-Datei ist leer oder fehlerhaft!")

st.write("✅ CSV-Datei erfolgreich geladen:")
st.write(df_crypto.head())

# 🔹 Datentypen korrigieren
df_crypto["date"] = pd.to_datetime(df_crypto["date"], format="%Y-%m-%d", errors="coerce")
df_crypto["crypto"] = df_crypto["crypto"].astype(str)
df_crypto["sentiment"] = df_crypto["sentiment"].astype(str)

# 🔍 Debugging: Dtypes prüfen
print(df_crypto.dtypes)
print(df_crypto.head())


# 📊 **Multi-Tab Navigation**
tab_home, tab_crypto, tab_stocks = st.tabs(["🏠 Home", "📈 Crypto Data", "💹 Stock Data"])

# 🔹 **🏠 HOME (README)**
with tab_home:
    st.title("📊 Reddit Financial Sentiment Dashboard")
    st.markdown("""
        ## 🔍 Project Overview
        This dashboard provides a **data-driven analysis of cryptocurrency sentiment** using **Reddit discussions** and **historical price data** starting from November 2024. The project integrates multiple data sources to explore the relationship between social sentiment and market trends.

        ### 📊 **Data Sources & Processing**
        - **Reddit Comments & Posts:** Scraped weekly from multiple subreddits using a **custom Reddit scraper**.  
        - **Sentiment Analysis:** Applied **CryptoBERT** for a **bullish-bearish-neutral classification** with confidence scores.  
        - **Historical Price Data:** Collected from **CoinGecko API** for major cryptocurrencies.  
        - **Data Storage:** Merged sentiment and price data is stored and updated weekly in **Google Drive**.

        ### 🔎 **Key Features**
        - **📈 Crypto Sentiment Analysis:**  
          - Top mentioned cryptocurrencies & sentiment distribution  
          - Sentiment trends over time (overall & high-confidence)  
          - Word count trends for selected cryptos
          - Combined analysis of sentiment & price dynamics    
        - **💹 Stock Market Analysis (Coming Soon)**  

        ### 🔄 **Update Frequency**
        - **Reddit data & sentiment analysis:** Weekly  
        - **Crypto price data:** Weekly  

        ---
        🔥 **Use the navigation tabs above to explore sentiment trends & price dynamics!**
    """)

# 🔹 **📈 CRYPTOCURRENCY ANALYSIS**
with tab_crypto:
    st.title("📈 Crypto Sentiment Dashboard")

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


        # **Word Count Over Time**
        st.subheader("📝 Word Count Evolution Over Time")

        # Multi-Select für mehrere Kryptowährungen
        selected_cryptos_wordcount = st.multiselect(
            "Choose Cryptos to Compare Word Frequency:",
            df_crypto["crypto"].unique().tolist(),
            default=df_crypto["crypto"].unique()[:3]
        )

        if selected_cryptos_wordcount:
            df_wordcount_filtered = df_crypto[df_crypto["crypto"].isin(selected_cryptos_wordcount)]
            wordcount_per_day = df_wordcount_filtered.groupby(["comment_date", "crypto"]).size().unstack(fill_value=0)
            st.line_chart(wordcount_per_day)


        # 🔹 **3️⃣ Sentiment Trend Over Time (Based on Comments)**
        st.subheader("📅 Sentiment Trend Over Time (Comments)")
        crypto_options = df_crypto["crypto"].unique().tolist()
        selected_crypto = st.selectbox("Choose a Cryptocurrency for Sentiment:", crypto_options, index=0, key="sentiment_crypto")


        df_filtered = df_crypto[(df_crypto["crypto"] == selected_crypto) & (df_crypto["sentiment"] != "neutral")]

        if df_filtered.empty:
            st.warning("⚠️ No sentiment data available for the selected cryptocurrency.")
        else:
            df_time = df_filtered.groupby(["comment_date", "sentiment"]).size().unstack(fill_value=0)
            st.line_chart(df_time)

    # 📊 **2️⃣ Word Count & Price Over Time**
        st.subheader("📊 Word Count & Price Over Time")

        # Auswahl einer Kryptowährung für die kombinierte Analyse
        selected_crypto_dual = st.selectbox("Choose a Cryptocurrency for Word Count & Price:", df_prices["crypto"].unique(), key="dual_axis_crypto")

        # Daten für die gewählte Krypto filtern
        df_wordcount_filtered = df_crypto[df_crypto["crypto"] == selected_crypto_dual].groupby("comment_date").size().reset_index(name="word_count")
        df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto_dual]

        # Sicherstellen, dass beide DataFrames die gleiche Zeitachse haben
        df_combined_dual = df_wordcount_filtered.merge(df_price_filtered, left_on="comment_date", right_on="date", how="inner")

        # Visualisierung mit zwei Y-Achsen
        fig, ax1 = plt.subplots(figsize=(10, 5))

        # Word Count auf linker Achse
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Word Count", color="blue")
        ax1.plot(df_combined_dual["comment_date"], df_combined_dual["word_count"], color="blue", label="Word Count", alpha=0.7)
        ax1.tick_params(axis="y", labelcolor="blue")

        # Preis auf rechter Achse
        ax2 = ax1.twinx()
        ax2.set_ylabel("Price (USD)", color="red")
        ax2.plot(df_combined_dual["comment_date"], df_combined_dual["price"], color="red", label="Price", alpha=0.7)
        ax2.tick_params(axis="y", labelcolor="red")

        # Titel und Legende
        fig.suptitle(f"Word Count & Price for {selected_crypto_dual} Over Time")
        fig.tight_layout()
        st.pyplot(fig)

        # 🔹 **1️⃣ Boxplot: Sentiment Confidence per Crypto**
        st.subheader("📊 Sentiment Confidence per Cryptocurrency")

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.boxplot(x="crypto", y="sentiment_confidence", data=df_crypto, ax=ax)
        ax.set_ylabel("Sentiment Confidence Score")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)  # Drehe Labels für bessere Lesbarkeit
        st.pyplot(fig)

       # 🔹 **Filtered Sentiment Distribution per Crypto (Only High Confidence)**
        st.subheader("🎯 Sentiment Distribution per Crypto (Only High Confidence)")

        # Wähle einen Confidence-Threshold (z. B. 0.8)
        CONFIDENCE_THRESHOLD = 0.8

        # Filtere nur Bullish & Bearish Sentiments mit hoher Confidence
        df_high_conf = df_crypto[
            (df_crypto["sentiment"].isin(["bullish", "bearish"])) & 
            (df_crypto["sentiment_confidence"] >= CONFIDENCE_THRESHOLD)
        ]

        # Gruppiere nach Crypto & Sentiment
        sentiment_dist_high_conf = df_high_conf.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)

        # Bar Chart in Streamlit
        st.bar_chart(sentiment_dist_high_conf)


        # 🔹 **3️⃣ Sentiment Trend Over Time (High Confidence Only)**
        st.subheader("📅 Sentiment Trend Over Time (Only High Confidence)")

        # Wähle einen Confidence-Threshold (z. B. 0.8)
        CONFIDENCE_THRESHOLD = 0.8

        # Auswahl der Kryptowährung
        crypto_options = df_crypto["crypto"].unique().tolist()
        selected_crypto = st.selectbox(
            "Choose a Cryptocurrency for High Confidence Sentiment:",
            crypto_options,
            index=0,
            key="sentiment_crypto_high_conf"
        )

        # Filtere nur bullish & bearish Sentiments mit hoher Confidence
        df_filtered_high_conf = df_crypto[
            (df_crypto["crypto"] == selected_crypto) &
            (df_crypto["sentiment"].isin(["bullish", "bearish"])) &
            (df_crypto["sentiment_confidence"] >= CONFIDENCE_THRESHOLD)
        ]

        if df_filtered_high_conf.empty:
            st.warning("⚠️ No high-confidence sentiment data available for the selected cryptocurrency.")
        else:
            df_time_high_conf = df_filtered_high_conf.groupby(["comment_date", "sentiment"]).size().unstack(fill_value=0)
            st.line_chart(df_time_high_conf)

        # 📊 **3️⃣ High-Confidence Sentiment & Price Over Time**
        st.subheader("📊 High-Confidence Sentiment & Price Over Time")

        # Auswahl einer Kryptowährung für die kombinierte Analyse
        selected_crypto_sentiment_price = st.selectbox(
            "Choose a Cryptocurrency for High-Confidence Sentiment & Price:",
            df_prices["crypto"].unique(),
            key="sentiment_price_dual"
        )

        # 🔹 Daten für die gewählte Krypto filtern (nur bullish & bearish mit hoher Confidence)
        df_sentiment_high_conf_filtered = df_crypto[
            (df_crypto["crypto"] == selected_crypto_sentiment_price) &
            (df_crypto["sentiment"].isin(["bullish", "bearish"])) &
            (df_crypto["sentiment_confidence"] >= CONFIDENCE_THRESHOLD)
        ].groupby(["comment_date", "sentiment"]).size().unstack(fill_value=0).reset_index()

        # 🔹 Preisdaten für dieselbe Krypto filtern
        df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto_sentiment_price]

        # 🔹 Sicherstellen, dass beide DataFrames die gleiche Zeitachse haben
        df_combined_sentiment_price = df_sentiment_high_conf_filtered.merge(
            df_price_filtered, left_on="comment_date", right_on="date", how="inner"
        )

        # 🔹 Visualisierung mit zwei Y-Achsen
        fig, ax1 = plt.subplots(figsize=(10, 5))

        # Sentiment-Trends auf linker Achse
        ax1.set_xlabel("Date")
        ax1.set_ylabel("High-Confidence Sentiment Count", color="blue")
        ax1.plot(df_combined_sentiment_price["comment_date"], df_combined_sentiment_price["bullish"], 
                color="green", label="Bullish (High Confidence)", alpha=0.7)
        ax1.plot(df_combined_sentiment_price["comment_date"], df_combined_sentiment_price["bearish"], 
                color="red", label="Bearish (High Confidence)", alpha=0.7)
        ax1.tick_params(axis="y", labelcolor="blue")
        ax1.legend(loc="upper left")

        # Preis auf rechter Achse
        ax2 = ax1.twinx()
        ax2.set_ylabel("Price (USD)", color="black")
        ax2.plot(df_combined_sentiment_price["comment_date"], df_combined_sentiment_price["price"], 
                color="black", label="Price", linewidth=2)
        ax2.tick_params(axis="y", labelcolor="black")
        ax2.legend(loc="upper right")

        # Titel & Layout
        fig.suptitle(f"High-Confidence Sentiment & Price for {selected_crypto_sentiment_price} Over Time")
        fig.tight_layout()
        st.pyplot(fig)

        
# 🔹 **💹 STOCK MARKET ANALYSIS**
with tab_stocks:
    st.title("💹 Stock Market Analysis (Coming Soon)")
    st.warning("🚧 This section is under development. Stock data will be integrated soon!")