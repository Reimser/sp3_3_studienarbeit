import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Streamlit Page Configuration
st.set_page_config(page_title="Reddit Data Dashboard", layout="centered")

# 🔄 **Refresh-Button**
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()  # Löscht gecachte Daten
    st.cache_resource.clear()  # Löscht gecachte Ressourcen
    st.experimental_rerun()  # Seite neu laden

# 📌 **Daten laden**
df_crypto = pd.read_csv("reddit_merged.csv")
df_prices = pd.read_csv("crypto_prices.csv")
# ✅ Sicherstellen, dass `date` wirklich `datetime64[ns]` ist
df_crypto["date"] = pd.to_datetime(df_crypto["date"], format="%Y-%m-%d", errors="coerce")
df_prices["date"] = pd.to_datetime(df_prices["date"], errors="coerce")
# ✅ Sicherstellen, dass `crypto` nur vorhandene Werte hat und als String gespeichert ist
df_crypto["crypto"] = df_crypto["crypto"].astype(str).str.strip()

# 🔍 **Debugging: Verfügbare Kryptowährungen**
available_cryptos = df_crypto["crypto"].dropna().unique().tolist()
print(f"🔍 Verfügbare Kryptowährungen im Datensatz: {available_cryptos}")
st.write("🔍 **Alle verfügbaren Kryptowährungen im Datensatz:**", df_crypto["crypto"].unique().tolist())

# 📊 **Multi-Tab Navigation mit Kategorien**
tab_home, tab_top, tab_new, tab_meme, tab_other, tab_stocks = st.tabs([
    "🏠 Home", "🏆 Top Coins", "📈 New Coins", "😂 Meme Coins", "⚡ Weitere Coins", "💹 Stock Data"
])

# 🔹 **🏠 HOME (README)**
with tab_home:
    st.title("📊 Reddit Financial Sentiment Dashboard")
    st.markdown("""
        ## 🔍 Project Overview
        This dashboard provides a **data-driven analysis of cryptocurrency sentiment** using **Reddit discussions** and **historical price data**.

        ### 🔎 **Key Features**
        - **📈 Crypto Sentiment Analysis:**  
          - Top mentioned cryptocurrencies & sentiment distribution  
          - Sentiment trends over time (overall & high-confidence)  
          - Combined analysis of sentiment & price dynamics    

        🔥 **Use the navigation tabs above to explore sentiment trends & price dynamics!**
    """)

# 📊 **Tabs für verschiedene Krypto-Kategorien**
def crypto_analysis_tab(tab, category, crypto_list):
    with tab:
        st.title(f"{category} Sentiment & Mentions")

        # ✅ **Nur existierende Coins anzeigen**
        crypto_list = [coin for coin in crypto_list if coin in available_cryptos]

        if not crypto_list:
            st.warning(f"⚠️ No cryptocurrencies available in this category.")
            return

        selected_crypto = st.selectbox(
            f"Choose a {category} Coin:", crypto_list, key=f"{category.lower()}_crypto"
        )

        # ✅ **Daten filtern**
        df_filtered = df_crypto[df_crypto["crypto"].str.lower() == selected_crypto.lower()]

        # 🔍 **Debugging: Überprüfen, ob gefilterte Daten existieren**
        print(f"📊 {category} - Verfügbare Daten für {selected_crypto}:")
        print(df_filtered.head())

        if df_filtered.empty:
            st.warning(f"⚠️ No data available for {selected_crypto}.")
            return

        # ✅ **1️⃣ Sentiment Distribution**
        st.subheader("💡 Sentiment Distribution of Cryptos")
        if "sentiment" in df_filtered.columns:
            sentiment_distribution = df_filtered["sentiment"].value_counts()
            st.bar_chart(sentiment_distribution)
        else:
            st.warning("⚠️ `sentiment` column not found. Skipping sentiment distribution.")

        # ✅ **2️⃣ Word Count Over Time**
        st.subheader("📝 Word Count Evolution Over Time")
        if "date" in df_filtered.columns:
            wordcount_per_day = df_filtered.groupby("date").size()
            st.line_chart(wordcount_per_day)
        else:
            st.warning("⚠️ `date` column not found. Skipping word count.")

        # ✅ **3️⃣ Sentiment Trend Over Time**
        st.subheader("📅 Sentiment Trend Over Time")
        if "sentiment" in df_filtered.columns:
            sentiment_trend = df_filtered.groupby(["date", "sentiment"]).size().unstack(fill_value=0)
            st.line_chart(sentiment_trend)
        else:
            st.warning("⚠️ `sentiment` column not found. Skipping sentiment trends.")

        # ✅ **4️⃣ Sentiment Confidence Boxplot**
        st.subheader("📊 Sentiment Confidence per Cryptocurrency")
        if "sentiment_confidence" in df_filtered.columns:
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.boxplot(x=df_filtered["sentiment_confidence"], ax=ax)
            ax.set_xlabel("Sentiment Confidence Score")
            st.pyplot(fig)
        else:
            st.warning("⚠️ `sentiment_confidence` column not found. Skipping boxplot.")

# 📊 **Tabs initialisieren**
top_coins = ["Ethereum", "Wrapped Ethereum", "Solana", "Avalanche", "Polkadot", "Near Protocol", "Polygon", "XRP", "Cardano", "Cronos"]
crypto_analysis_tab(tab_top, "Top Coins", top_coins)

new_coins = ["Arbitrum", "Starknet", "Injective Protocol", "Sei Network", "Aptos"]
crypto_analysis_tab(tab_new, "New Coins", new_coins)

meme_coins = ["Shiba Inu", "Pepe", "Floki Inu", "Bonk", "Degen", "Toshi"]
crypto_analysis_tab(tab_meme, "Meme Coins", meme_coins)

other_coins = ["VeChain", "Render", "Hedera", "Filecoin", "Cosmos"]
crypto_analysis_tab(tab_other, "Weitere Coins", other_coins)

# 🔹 **💹 STOCK MARKET ANALYSIS**
with tab_stocks:
    st.title("💹 Stock Market Analysis (Coming Soon)")
    st.warning("🚧 This section is under development. Stock data will be integrated soon!")
