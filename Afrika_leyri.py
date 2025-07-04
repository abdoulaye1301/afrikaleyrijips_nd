import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
from openpyxl import load_workbook
import io

st.set_page_config(
    page_title="Ingénieur NDAO", layout="wide", page_icon="ndao abdoulaye.png"
)
profil = Image.open("Logo Afrika Leyri.png")
st.logo(profil)

#st.header("🔐 Connexion KoboToolbox")
#api_token = st.sidebar.text_input("Mot de passe", type="password")
#form_uid = st.sidebar.text_input("ID du formulaire (KoboToolbox)", placeholder="Ex: aiukigovSDuthG6GcpfJc2")
# Mot de passe : aiuki
# Upload du fichier Excel
# --- Authentification simple ---
USER = "admin"
PASSWORD = "1234"

if "authentifie" not in st.session_state:
    st.session_state.authentifie = False
        
# --- Navigation ---
page = st.sidebar.radio("📁 Menu", ["Visualisation", "Tableau de bord sécurisé"])
# URL de récupération des données en CSV
donnee = pd.read_excel(f"https://kf.kobotoolbox.org/api/v2/assets/aiukigovSDuthG6GcpfJc4/export-settings/esY6CBjs5ceExzwiZ7xMRzP/data.xlsx")



# Choisir une feuille à modifier
#feuille_selectionnee = st.sidebar.selectbox("Choisissez une feuille à éditer :",  )

# Charger la feuille sélectionnée
nomscol=["Date","Prenom Nom", "Zone", "Prenom_Nom_Client", "Telephone_Client", 
        "Adresse", "Operation", "Numéro_Pack", "Reference Commande", "Montant", "Commentaire"]
# Définir les chemins des fichiers source et destination
base=donnee[nomscol]
#base["Date"] = base["Date"].dt.date
# donnee["Mois"] = donnee["Date"].dt.month
# --- Page 1 : Visualisation simple ---
if page == "Visualisation":
    with st.form("login_form"):
        st.subheader("🔐 Connexion requise")
        user = st.text_input("Nom d'utilisateur")
        pwd = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Connexion")
        if submit:
            if user == USER and pwd == PASSWORD:
                st.session_state.authentifie = True
                st.success("✅ Connexion réussie")
                st.title("📄 Visualisation des données")
                    # Définir les bornes du slider
                base["Date"] = base["Date"].dt.date
                min_date = min(base["Date"])
                max_date = max(base["Date"])

                # Slider Streamlit pour filtrer une plage de dates
                start_date, end_date = st.slider(
                    "Sélectionnez une plage de dates",
                    min_value=min_date,
                    max_value=max_date,
                    value=(min_date, max_date),  # valeur par défaut (tout)
                    format="DD/MM/YYYY"
                )

                # Filtrer les données selon la plage sélectionnée
                base = base[(base["Date"] >= start_date) & (base["Date"] <= end_date)]

                # Afficher les résultats
                st.write(f"Résultats entre {start_date} et {end_date} :")
                st.dataframe(base)
            else:
                st.error("❌ Identifiants incorrects")

# --- Page 2 : Tableau de bord (protégé) ---
elif page == "Tableau de bord sécurisé":
    if not st.session_state.authentifie:
        login()
    else:
        # --- Message de bienvenue si connecté ---
        st.title("📊 Tableau de bord des collectes")
                # Agrégation par jour
        evolution = base.groupby("Date").size().reset_index(name="Nombre")
        pack = base.groupby("Numéro_Pack").size().reset_index(name="Nombre de pack")

        st.subheader("📊 Évolution des ventes et installations des commerciaux")
        col= st.columns(3)
        col[0].metric("📌 Total de collectes", len(base))
        col[1].metric("📌 Total de références de commandes", base["Reference Commande"].nunique())
        col[2].metric("📌 Total de montants", base["Montant"].sum())
        # Représentation graphique avec plotly
        colon= st.columns(2)
        fig = px.line(evolution, x="Date", y="Nombre",
                        title="Nombre de collectes par jour",
                        markers=True)
        colon[0].plotly_chart(fig, use_container_width=True)
        gra=px.histogram(pack, x="Numéro_Pack", y="Nombre de pack",
                        title="Nombre de collectes par numéro de pack",)
        colon[1].plotly_chart(gra, use_container_width=True)

        colon[0].plotly_chart(px.pie(base, names="Operation"), use_container_width=True)  
        fig = px.bar(
            base,
            x="Date",
            y="Montant",
            color="Prenom Nom",
            title="📊 Performance des agents"
        )
        colon[1].plotly_chart(fig, use_container_width=True)

        # Performance des agents
        donnee_agre = base.groupby(["Prenom Nom","Operation"]).agg(
            {"Telephone_Client": "count", "Numéro_Pack": "count", "Montant": "sum"}
            ).reset_index()
        donnee_agre = donnee_agre.rename(
        columns={
            "Telephone_Client": "Nombre de Clients",
            "Numéro_Pack": "Nombre de Packs",
            "Montant": "Montant",
        }
    )
        st.subheader("Récapitulatif des ventes et installations des commerciaux")
        st.dataframe(donnee_agre.sort_values(by=["Prenom Nom", "Montant"], ascending=False))
            