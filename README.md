# reddit-crypto-sentiment-pipeline

Automatisierte Pipeline zur Analyse der Marktstimmung von Kryptowährungen auf Basis von Reddit-Diskussionen. Das Projekt kombiniert Web Scraping, Sentiment-Analyse mit CryptoBERT, die Integration von CoinGecko-Preisdaten sowie die Visualisierung der Ergebnisse in einem interaktiven Streamlit-Dashboard.

## Projektübersicht
Dieses Projekt implementiert eine vollständige End-to-End-Pipeline:

Datenextraktion aktueller und historischer Reddit-Daten über PRAW und Pushshift API

Sentiment-Analyse der Beiträge mithilfe des spezialisierten CryptoBERT-Modells

Integration historischer Preisdaten über die CoinGecko API

Automatisierte Verarbeitung mittels Jenkins CI/CD-Pipeline

Interaktive Visualisierung der Sentiment- und Preistrends in Streamlit

## Projektstruktur
/notebooks/ – Jupyter Notebooks für Datenextraktion, Vorverarbeitung und Analyse

/streamlit_app/ – Streamlit-App zur interaktiven Darstellung der Ergebnisse

/jenkins_jobs/ – Automatisierungsskripte zur regelmäßigen Ausführung

/data/ – Gespeicherte Rohdaten und verarbeitete CSV-Dateien

requirements.txt – Alle benötigten Python-Pakete

README.md – Projektdokumentation

## Features
Batch-Scraping von Reddit-Posts und Kommentaren

GPU-optimierte Sentiment-Analyse mit CryptoBERT

Historische Preisabrufe via CoinGecko API

Jenkins-Pipeline für automatisierte Ausführung

Übersichtliche Dashboards für Sentiment- und Preisanalysen

## Genutzte Technologien
Python 3.10+

PRAW, PSAW (Reddit APIs)

Hugging Face Transformers

Streamlit

Jenkins

Papermill

Pandas, Matplotlib

CoinGecko API
