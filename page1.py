import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

st.set_page_config(page_title="Suivi KoboToolbox", layout="wide")

st.title("📡 Suivi en direct des collectes KoboToolbox")

# Saisie des paramètres API
st.sidebar.header("🔐 Connexion KoboToolbox")
api_token = st.sidebar.text_input("Mot de passe", type="password")
form_uid = st.sidebar.text_input("ID du formulaire (KoboToolbox)", placeholder="Ex: aiukigovSDuthG6GcpfJc2")

headers = {
    "Authorization": f"Token {api_token}"
}
# Mot de passe : LyP2T
# ID du formulaire : aiukigovSDuthG6GcpfJc4
# https://kf.kobotoolbox.org/api/v2/assets/aiukigovSDuthG6GcpfJc4/export-settings/esafRjZ22V8XNxxBk6LyP2T/data.xlsx
if api_token and form_uid:
    # URL de récupération des données en CSV
    url = f"https://kf.kobotoolbox.org/api/v2/assets/{form_uid}/export-settings/esafRjZ22V8XNxxBk6{api_token}/data.xlsx"

    try:
        st.info("🔄 Chargement des données depuis KoboToolbox...")
        df = pd.read_excel(url, engine='openpyxl')

        st.success("✅ Données récupérées avec succès depuis KoboToolbox !")

        # Colonnes de date
        date_cols = [col for col in df.columns if 'start' in col.lower() or 'date' in col.lower()]
        if not date_cols:
            st.warning("⚠️ Aucune colonne de date trouvée.")
        else:
            date_col = st.selectbox("📅 Choisir la colonne de date :", date_cols)
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df["date"] = df[date_col].dt.date

            # Évolution
            evolution = df.groupby("date").size().reset_index(name="nombre_collectes")

            st.subheader("📈 Évolution des collectes par jour")
            fig, ax = plt.subplots()
            ax.plot(evolution["date"], evolution["nombre_collectes"], marker='o')
            ax.set_xlabel("Date")
            ax.set_ylabel("Collectes")
            ax.set_title("Collectes par jour")
            ax.grid(True)
            st.pyplot(fig)

            st.metric("📌 Total de collectes", len(df))

            st.subheader("📋 Données brutes")
            st.dataframe(df)

    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Erreur HTTP : {e}")
    except Exception as e:
        st.error(f"❌ Une erreur est survenue : {e}")

else:
    st.info("💡 Entrez votre token API et l'ID du formulaire pour charger les données.")

