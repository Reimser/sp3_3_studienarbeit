import streamlit as st
import pandas as pd
import gdown
import os
import ast
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Reddit Data Dashboard", layout="centered")

# 🚀 **Cache leeren, um alte Daten zu vermeiden**
st.cache_data.clear()

# 📌 Google Drive File IDs für die Datensätze
MERGED_CRYPTO_CSV_ID = "117G8MGV-KgKQ9S5D-YT4WKwLQCpiq7QI"
CRYPTO_PRICES_CSV_ID = "10wkptEC82rQDttx2zMFrl7r4sYgkx421"

# 📌 Lokale Dateinamen
MERGED_CRYPTO_CSV = "reddit_merged.csv"
CRYPTO_PRICES_CSV = "crypto_prices.csv"

# 🔹 Funktion zum Herunterladen von CSV-Dateien von Google Drive
@st.cache_data
def download_csv(file_id, output):
    """Lädt eine Datei von Google Drive herunter."""
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output, quiet=False)

# 🔹 Sicherstellen, dass Dateien existieren
for file_id, filename in [(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV), (CRYPTO_PRICES_CSV_ID, CRYPTO_PRICES_CSV)]:
    if not os.path.exists(filename):
        print(f"📥 Downloading {filename} from Google Drive...")
        download_csv(file_id, filename)

# 🔹 Funktion zum Laden der Crypto-Daten
@st.cache_data
def load_crypto_data():
    """Lädt die Reddit Crypto-Daten."""
    if not os.path.exists(MERGED_CRYPTO_CSV):
        st.error(f"❌ Datei nicht gefunden: {MERGED_CRYPTO_CSV}")
        return pd.DataFrame()

    df_crypto = pd.read_csv(MERGED_CRYPTO_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # 🛠 Debugging: Spalten prüfen
    print("📌 Spalten in df_crypto:", df_crypto.columns.tolist())

    # 🔹 Sicherstellen, dass 'date' existiert
    if "date" not in df_crypto.columns:
        raise KeyError(f"❌ 'date' fehlt! Verfügbare Spalten: {df_crypto.columns.tolist()}")

    # 🔹 `date` in datetime-Format umwandeln
    df_crypto["date"] = pd.to_datetime(df_crypto["date"], errors="coerce")

    # 🔹 `detected_crypto` als Liste speichern
    if "detected_crypto" in df_crypto.columns:
        df_crypto["detected_crypto"] = df_crypto["detected_crypto"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith("[") else []
        )
    else:
        st.warning("⚠️ 'detected_crypto' Spalte fehlt!")

    # 🔹 Sentiment in numerische Werte umwandeln
    sentiment_mapping = {"bullish": 1, "neutral": 0, "bearish": -1}
    df_crypto["sentiment_score"] = df_crypto["sentiment"].map(sentiment_mapping)

    return df_crypto

# 🔹 Funktion zum Laden der Crypto-Preisdaten
@st.cache_data
def load_crypto_prices():
    """Lädt die Crypto-Preisdaten."""
    if not os.path.exists(CRYPTO_PRICES_CSV):
        st.error(f"❌ Datei nicht gefunden: {CRYPTO_PRICES_CSV}")
        return pd.DataFrame()

    df_prices = pd.read_csv(CRYPTO_PRICES_CSV, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

    # 📌 Debugging: Spalten prüfen
    print("📝 Spalten in df_prices:", df_prices.columns.tolist())

    # 🔹 Entferne unnötige Leerzeichen aus Spaltennamen
    df_prices.columns = df_prices.columns.str.strip()

    # 🔹 Sicherstellen, dass `date` existiert und umwandeln
    if "date" in df_prices.columns:
        df_prices["date"] = pd.to_datetime(df_prices["date"], errors="coerce")
    else:
        raise KeyError(f"⚠️ 'date' Spalte fehlt! Verfügbare Spalten: {df_prices.columns.tolist()}")

    return df_prices

# 📌 Lade die Daten
df_crypto = load_crypto_data()
df_prices = load_crypto_prices()

# 🔹 Debugging: Zeige die ersten Zeilen der geladenen DataFrames
print("🔍 Erste Zeilen von df_crypto:")
print(df_crypto.head())

print("🔍 Erste Zeilen von df_prices:")
print(df_prices.head())

# 📊 Multi-Tab Navigation mit Kategorien
tab_home, tab_top, tab_new, tab_meme, tab_other, tab_stocks = st.tabs([
    "🏠 Home", "🏆 Top Coins", "📈 New Coins", "😂 Meme Coins", "⚡ Weitere Coins","💹 Stock Data"
])

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
    # 🔄 **Refresh Button**
if st.button("🔄 Refresh Data"):
    # Lösche die vorhandene Datei, um sicherzugehen, dass neue Daten geladen werden
    if os.path.exists(MERGED_CRYPTO_CSV):
        os.remove(MERGED_CRYPTO_CSV)

    # Lade die neue Datei herunter
    download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)

    # Lade die neuen Daten in den DataFrame
    df_crypto = load_crypto_data()

    # Lösche den Cache und erzwinge das Neuladen der App
    st.cache_data.clear()
    st.rerun()


# 📊 **Tabs for Different Categories**
def crypto_analysis_tab(tab, category, crypto_list):
    with tab:
        st.title(f"{category} Sentiment & Mentions")

        selected_crypto = st.selectbox(f"Choose a {category} Coin:", crypto_list, key=f"{category.lower()}_crypto")

        df_filtered = df_crypto[df_crypto["detected_crypto"].apply(lambda x: selected_crypto in x if isinstance(x, list) else False)]

        if df_filtered.empty:
            st.warning(f"⚠️ No data available for {selected_crypto}.")
        else:
            # 🔹 **1️⃣ Most Discussed Cryptos**
            st.subheader("🔥 Top 10 Most Mentioned Cryptocurrencies")
            crypto_counts = df_filtered["crypto"].value_counts().head(10)
            st.bar_chart(crypto_counts)

            # 🔹 **2️⃣ Sentiment Distribution per Crypto**
            st.subheader("💡 Sentiment Distribution of Cryptos")
            sentiment_distribution = df_filtered.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
            st.bar_chart(sentiment_distribution)

            # **📝 Word Count Over Time**
            st.subheader("📝 Word Count Evolution Over Time")
            selected_cryptos_wordcount = st.multiselect(
                "Choose Cryptos to Compare Word Frequency:",
                df_filtered["crypto"].unique().tolist(),
                default=df_filtered["crypto"].unique()[:3]
            )
            if selected_cryptos_wordcount:
                df_wordcount_filtered = df_filtered[df_filtered["crypto"].isin(selected_cryptos_wordcount)]
                wordcount_per_day = df_wordcount_filtered.groupby(["comment_date", "crypto"]).size().unstack(fill_value=0)
                st.line_chart(wordcount_per_day)

            # 🔹 **3️⃣ Sentiment Trend Over Time (Based on Comments)**
            st.subheader("📅 Sentiment Trend Over Time (Comments)")
            crypto_options = df_filtered["crypto"].unique().tolist()
            selected_crypto = st.selectbox("Choose a Cryptocurrency for Sentiment:", crypto_options, index=0, key="sentiment_crypto")

            df_filtered = df_filtered[(df_filtered["crypto"] == selected_crypto) & (df_filtered["sentiment"] != "neutral")]
            if df_filtered.empty:
                st.warning("⚠️ No sentiment data available for the selected cryptocurrency.")
            else:
                df_time = df_filtered.groupby(["comment_date", "sentiment"]).size().unstack(fill_value=0)
                st.line_chart(df_time)

            # 📊 **2️⃣ Word Count & Price Over Time**
            st.subheader("📊 Word Count & Price Over Time")
            selected_crypto_dual = st.selectbox("Choose a Cryptocurrency for Word Count & Price:", df_prices["crypto"].unique(), key="dual_axis_crypto")

            df_wordcount_filtered = df_filtered[df_filtered["crypto"] == selected_crypto_dual].groupby("comment_date").size().reset_index(name="word_count")
            df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto_dual]

            df_combined_dual = df_wordcount_filtered.merge(df_price_filtered, left_on="comment_date", right_on="date", how="inner")

            fig, ax1 = plt.subplots(figsize=(10, 5))
            ax1.set_xlabel("Date")
            ax1.set_ylabel("Word Count", color="blue")
            ax1.plot(df_combined_dual["comment_date"], df_combined_dual["word_count"], color="blue", label="Word Count", alpha=0.7)
            ax1.tick_params(axis="y", labelcolor="blue")

            ax2 = ax1.twinx()
            ax2.set_ylabel("Price (USD)", color="red")
            ax2.plot(df_combined_dual["comment_date"], df_combined_dual["price"], color="red", label="Price", alpha=0.7)
            ax2.tick_params(axis="y", labelcolor="red")

            fig.suptitle(f"Word Count & Price for {selected_crypto_dual} Over Time")
            fig.tight_layout()
            st.pyplot(fig)

            # 🔹 **1️⃣ Boxplot: Sentiment Confidence per Crypto**
            st.subheader("📊 Sentiment Confidence per Cryptocurrency")
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.boxplot(x="crypto", y="sentiment_confidence", data=df_filtered, ax=ax)
            ax.set_ylabel("Sentiment Confidence Score")
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
            st.pyplot(fig)

            # 🔹 **Filtered Sentiment Distribution per Crypto (Only High Confidence)**
            st.subheader("🎯 Sentiment Distribution per Crypto (Only High Confidence)")
            CONFIDENCE_THRESHOLD = 0.8

            df_high_conf = df_filtered[
                (df_filtered["sentiment"].isin(["bullish", "bearish"])) &
                (df_filtered["sentiment_confidence"] >= CONFIDENCE_THRESHOLD)
            ]
            sentiment_dist_high_conf = df_high_conf.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
            st.bar_chart(sentiment_dist_high_conf)

            # 🔹 **3️⃣ Sentiment Trend Over Time (High Confidence Only)**
            st.subheader("📅 Sentiment Trend Over Time (Only High Confidence)")
            selected_crypto = st.selectbox(
                "Choose a Cryptocurrency for High Confidence Sentiment:",
                df_filtered["crypto"].unique().tolist(),
                index=0,
                key="sentiment_crypto_high_conf"
            )

            df_filtered_high_conf = df_filtered[
                (df_filtered["crypto"] == selected_crypto) &
                (df_filtered["sentiment"].isin(["bullish", "bearish"])) &
                (df_filtered["sentiment_confidence"] >= CONFIDENCE_THRESHOLD)
            ]
            if df_filtered_high_conf.empty:
                st.warning("⚠️ No high-confidence sentiment data available for the selected cryptocurrency.")
            else:
                df_time_high_conf = df_filtered_high_conf.groupby(["comment_date", "sentiment"]).size().unstack(fill_value=0)
                st.line_chart(df_time_high_conf)

            # 📊 **3️⃣ High-Confidence Sentiment & Price Over Time**
            st.subheader("📊 High-Confidence Sentiment & Price Over Time")
            selected_crypto_sentiment_price = st.selectbox(
                "Choose a Cryptocurrency for High-Confidence Sentiment & Price:",
                df_prices["crypto"].unique(),
                key="sentiment_price_dual"
            )

            df_sentiment_high_conf_filtered = df_filtered[
                (df_filtered["crypto"] == selected_crypto_sentiment_price) &
                (df_filtered["sentiment"].isin(["bullish", "bearish"])) &
                (df_filtered["sentiment_confidence"] >= CONFIDENCE_THRESHOLD)
            ].groupby(["comment_date", "sentiment"]).size().unstack(fill_value=0).reset_index()

            df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto_sentiment_price]

            df_combined_sentiment_price = df_sentiment_high_conf_filtered.merge(
                df_price_filtered, left_on="comment_date", right_on="date", how="inner"
            )

            fig, ax1 = plt.subplots(figsize=(10, 5))
            ax1.set_xlabel("Date")
            ax1.set_ylabel("High-Confidence Sentiment Count", color="blue")
            ax1.plot(df_combined_sentiment_price["comment_date"], df_combined_sentiment_price["bullish"],
                    color="green", label="Bullish (High Confidence)", alpha=0.7)
            ax1.plot(df_combined_sentiment_price["comment_date"], df_combined_sentiment_price["bearish"],
                    color="red", label="Bearish (High Confidence)", alpha=0.7)
            ax1.tick_params(axis="y", labelcolor="blue")
            ax1.legend(loc="upper left")

            ax2 = ax1.twinx()
            ax2.set_ylabel("Price (USD)", color="black")
            ax2.plot(df_combined_sentiment_price["comment_date"], df_combined_sentiment_price["price"],
                    color="black", label="Price", linewidth=2)
            ax2.tick_params(axis="y", labelcolor="black")
            ax2.legend(loc="upper right")

            fig.suptitle(f"High-Confidence Sentiment & Price for {selected_crypto_sentiment_price} Over Time")
            fig.tight_layout()
            st.pyplot(fig)

            

    # 🏆 **Top Coins**
    top_coins = ["Bitcoin", "Ethereum", "Wrapped Ethereum", "Solana", "Avalanche", "Polkadot", "Near Protocol", "Polygon", "XRP", "Cardano", "Cronos",  "Chiliz",  "Ronin", "Band Protocol", "Optimism", "Celestia",  "Aethir", "Sui", "Hyperliquid", "Robinhood Coin", "Trump Coin", "USD Coin", "Binance Coin", "Litecoin", "Dogecoin", "Tron", "Aave", "Hedera",  "Cosmos", "Gala", "Chainlink"]
    crypto_analysis_tab(tab_top, "Top Coins", top_coins)

    # 📈 **New Coins**
    new_coins = ["Arbitrum", "Starknet", "Injective Protocol", "Sei Network", "Aptos", "EigenLayer", "Mantle", "Immutable X", "Ondo Finance", "Worldcoin", "Aerodrome", "Jupiter", "THORChain", "Pendle", "Kujira", "Noble", "Stride", "Dymension", "Seamless Protocol", "Blast", "Merlin", "Tapioca", "Arcadia Finance", "Notcoin", "Omni Network", "LayerZero", "ZetaChain", "Friend.tech"]
    crypto_analysis_tab(tab_new, "New Coins", new_coins)

    # 😂 **Meme Coins**
    meme_coins = ["Shiba Inu", "Pepe", "Floki Inu", "Bonk", "Wojak", "Mog Coin", "Doge Killer (Leash)", "Baby Doge Coin", "Degen", "Toshi", "Fartcoin", "Banana", "Kabosu", "Husky", "Samoyedcoin", "Milkbag"]
    crypto_analysis_tab(tab_meme, "Meme Coins", meme_coins)

    # ⚡ **Weitere Coins**
    other_coins = ["VeChain", "Render", "Kusama", "Hedera", "Filecoin", "Vulcan Forged PYR", "Illuvium", "Numerai", "Audius", "Kusama",  "Berachain", "The Sandbox", "TestCoin", "Cosmos"]
    crypto_analysis_tab(tab_other, "Weitere Coins", other_coins)

# 🔹 **💹 STOCK MARKET ANALYSIS**
with tab_stocks:
    st.title("💹 Stock Market Analysis (Coming Soon)")
    st.warning("🚧 This section is under development. Stock data will be integrated soon!")
