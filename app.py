import streamlit as st
import os

st.write("🔍 **Testing Streamlit Secrets...**")

# Prüfen, ob die Datei wirklich existiert
if os.path.exists(".streamlit/secrets.toml"):
    st.success("✅ `.streamlit/secrets.toml` existiert!")
else:
    st.error("❌ `.streamlit/secrets.toml` fehlt!")

# Testen, ob `st.secrets` geladen wird
if st.secrets:
    st.write("✅ `st.secrets` geladen:", st.secrets)
else:
    st.error("❌ `st.secrets` ist leer! 🚨")

# Einzelne Variablen testen oder do
try:
    merged_csv_id = st.secrets["MERGED_CRYPTO_CSV_ID"]
    st.success(f"✅ MERGED_CRYPTO_CSV_ID: {merged_csv_id}")
except KeyError:
    st.error("❌ `MERGED_CRYPTO_CSV_ID` nicht gefunden!")

try:
    prices_csv_id = st.secrets["CRYPTO_PRICES_CSV_ID"]
    st.success(f"✅ CRYPTO_PRICES_CSV_ID: {prices_csv_id}")
except KeyError:
    st.error("❌ `CRYPTO_PRICES_CSV_ID` nicht gefunden!")
