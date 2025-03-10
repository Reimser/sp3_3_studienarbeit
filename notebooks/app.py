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
    wordcount_per_day = df_wordcount_filtered.groupby(["date", "crypto"]).size().unstack(fill_value=0)  # ✅ FIXED
    st.line_chart(wordcount_per_day)


# **Sentiment Trend Over Time**
st.subheader("📅 Sentiment Trend Over Time")
selected_crypto = st.selectbox("Choose a Cryptocurrency for Sentiment:", df_crypto["crypto"].unique(), key="sentiment_crypto")

df_filtered = df_crypto[(df_crypto["crypto"] == selected_crypto) & (df_crypto["sentiment"] != "neutral")]

if df_filtered.empty:
    st.warning("⚠️ No sentiment data available for the selected cryptocurrency.")
else:
    df_time = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)  # ✅ FIXED
    st.line_chart(df_time)


# **Word Count & Price Over Time**
st.subheader("📊 Word Count & Price Over Time")
selected_crypto_dual = st.selectbox("Choose a Cryptocurrency for Word Count & Price:", df_prices["crypto"].unique(), key="dual_axis_crypto")

df_wordcount_filtered = df_crypto[df_crypto["crypto"] == selected_crypto_dual].groupby("date").size().reset_index(name="word_count")  # ✅ FIXED
df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto_dual]

# Sicherstellen, dass beide DataFrames die gleiche Zeitachse haben
df_combined_dual = df_wordcount_filtered.merge(df_price_filtered, on="date", how="inner")  # ✅ FIXED

# Visualisierung mit zwei Y-Achsen
fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.set_xlabel("Date")
ax1.set_ylabel("Word Count", color="blue")
ax1.plot(df_combined_dual["date"], df_combined_dual["word_count"], color="blue", label="Word Count", alpha=0.7)
ax1.tick_params(axis="y", labelcolor="blue")

ax2 = ax1.twinx()
ax2.set_ylabel("Price (USD)", color="red")
ax2.plot(df_combined_dual["date"], df_combined_dual["price"], color="red", label="Price", alpha=0.7)
ax2.tick_params(axis="y", labelcolor="red")

fig.suptitle(f"Word Count & Price for {selected_crypto_dual} Over Time")
fig.tight_layout()
st.pyplot(fig)
        
# 🔹 **💹 STOCK MARKET ANALYSIS**
with tab_stocks:
    st.title("💹 Stock Market Analysis (Coming Soon)")
    st.warning("🚧 This section is under development. Stock data will be integrated soon!")