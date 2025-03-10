import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Config
st.set_page_config(page_title="Reddit Crypto Dashboard", layout="wide")

# 📥 **Google Drive File IDs**
MERGED_CRYPTO_CSV_ID = "12ugApKWh1cJYONcLanpHND9gIdobh-wA"
CRYPTO_PRICES_CSV_ID = "11k9wiflOkqg2DayEgn7iPqNPHC5Qatht"

# 📌 **Lokale Dateinamen**
MERGED_CRYPTO_CSV = "app.csv"
CRYPTO_PRICES_CSV = "crypto_prices.csv"

# 🔥 **Download CSV (falls nicht lokal vorhanden)**
def download_csv(file_id, output):
    if not os.path.exists(output):
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        try:
            st.info(f"📥 Lade {output} herunter...")
            gdown.download(url, output, quiet=False, fuzzy=True)
        except Exception as e:
            st.error(f"❌ Download fehlgeschlagen: {str(e)}")

download_csv(MERGED_CRYPTO_CSV_ID, MERGED_CRYPTO_CSV)
download_csv(CRYPTO_PRICES_CSV_ID, CRYPTO_PRICES_CSV)

# 📌 **CSV-Dateien einlesen**
def load_csv(filepath):
    if not os.path.exists(filepath):
        st.error(f"❌ Datei nicht gefunden: {filepath}")
        return pd.DataFrame()
    return pd.read_csv(filepath, sep="|", encoding="utf-8-sig", on_bad_lines="skip")

df_crypto = load_csv(MERGED_CRYPTO_CSV)
df_prices = load_csv(CRYPTO_PRICES_CSV)

# 🔹 **Fix für `date`-Spalten in beiden DataFrames**
for df in [df_crypto, df_prices]:
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")  # ALLES zu datetime umwandeln
        df.dropna(subset=["date"], inplace=True)  # NaT (NaN-Daten) entfernen

# 📊 **DEBUG: Datentypen ausgeben**
st.write("📊 Datentypen nach Konvertierung:")
st.write("🔹 df_crypto:", df_crypto.dtypes)
st.write("🔹 df_prices:", df_prices.dtypes)

# 📈 **DASHBOARD: CRYPTO SENTIMENT ANALYSIS**
st.title("📊 Crypto Sentiment Dashboard")

if df_crypto.empty:
    st.warning("⚠️ No Crypto Data Available.")
else:
    # 🔹 **Meistdiskutierte Kryptowährungen**
    st.subheader("🔥 Top 10 Most Mentioned Cryptos")
    st.bar_chart(df_crypto["crypto"].value_counts().head(10))

    # 🔹 **Sentiment-Verteilung**
    st.subheader("💡 Sentiment Distribution")
    sentiment_distribution = df_crypto.groupby(["crypto", "sentiment"]).size().unstack(fill_value=0)
    st.bar_chart(sentiment_distribution)

    # 🔹 **Word Count über die Zeit**
    st.subheader("📝 Word Count Over Time")
    selected_cryptos = st.multiselect("🔍 Select Cryptos:", df_crypto["crypto"].unique(), default=df_crypto["crypto"].unique()[:3])
    
    if selected_cryptos:
        df_wordcount_filtered = df_crypto[df_crypto["crypto"].isin(selected_cryptos)]
        wordcount_per_day = df_wordcount_filtered.groupby(["date", "crypto"]).size().unstack(fill_value=0)
        st.line_chart(wordcount_per_day)

    # 🔹 **Sentiment-Trend über die Zeit**
    st.subheader("📅 Sentiment Trend Over Time")
    selected_crypto = st.selectbox("🔍 Select a Crypto for Sentiment Analysis:", df_crypto["crypto"].unique())

    df_filtered = df_crypto[(df_crypto["crypto"] == selected_crypto) & (df_crypto["sentiment"] != "neutral")]
    
    if not df_filtered.empty:
        df_time = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
        st.line_chart(df_time)
    else:
        st.warning("⚠️ No sentiment data available.")

    # 🔹 **Word Count & Preis über die Zeit**
    st.subheader("📊 Word Count & Price Over Time")
    selected_crypto_dual = st.selectbox("🔍 Select a Crypto for Word Count & Price:", df_prices["crypto"].unique())

    df_wordcount_filtered = df_crypto[df_crypto["crypto"] == selected_crypto_dual].groupby("date").size().reset_index(name="word_count")
    df_price_filtered = df_prices[df_prices["crypto"] == selected_crypto_dual]

    # **Finaler Fix für Merge**
    df_wordcount_filtered["date"] = pd.to_datetime(df_wordcount_filtered["date"], errors="coerce")
    df_price_filtered["date"] = pd.to_datetime(df_price_filtered["date"], errors="coerce")

    df_combined_dual = df_wordcount_filtered.merge(df_price_filtered, on="date", how="inner")

    # **Zwei-Achsen-Plot: Word Count & Price**
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
