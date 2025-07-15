import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
from openpyxl import load_workbook
import io

st.set_page_config(
    page_title="AFRIKA LEYRI", layout="wide", page_icon="ndao abdoulaye.png"
)
profil = Image.open("Logo Afrika Leyri.png")
st.logo(profil)

#st.header("🔐 Connexion KoboToolbox")
#api_token = st.sidebar.text_input("Mot de passe", type="password")
#form_uid = st.sidebar.text_input("ID du formulaire (KoboToolbox)", placeholder="Ex: aiukigovSDuthG6GcpfJc2")
# Mot de passe : aiuki
# Upload du fichier Excel
# --- Authentification simple ---
USER = "AFRIKA LEYRI"
PASSWORD = "Afrikaleyri2025"

if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Données')
    output.seek(0)
    return output

def login():
    with st.form("login_form"):
        st.subheader("🔐 IDENTIFICATION")
        user = st.text_input("Nom d'utilisateur")
        pwd = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Connexion")
        if submit:
            if user == USER and pwd == PASSWORD:
                st.session_state.authentifie = True
                st.success("Bienvenue dans l'application Afrika Leyri !")
            else:
                st.error("❌ Identifiants incorrects")
                st.warning("Veuillez vous connecter pour accéder aux données.")
                st.stop()
# --- Onction de vuisualisation des données ---
def visualiser_donnees(base):
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
    st.dataframe(base.sort_values(by=["Date","Prenom Nom"], ascending=False))
    # Téléchargement des données en format Excel
    excel_data = to_excel(base)

    st.download_button(
        label="📄 Télécharger les données",
        data=excel_data,
        file_name="Données JIPS.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# --- Fonction de tableau de bord ---
def tableau_de_bord(base):
            # Agrégation par jour
    evolution = base.groupby("Date").agg({"Montant": "sum"}).reset_index()
    pack = base.groupby("Numéro_Pack").size().reset_index(name="Nombre de pack")

    st.subheader("📊 Évolution des ventes et installations des commerciaux")
    col= st.columns(4)
    col[0].metric("🎗️Total commandes", base["Reference Commande"].nunique())
    col[1].metric("🔢 Nombre de pack de 5000", int((base["Montant"] < 10000).sum()))
    col[2].metric("🔢 Nombre de pack de 10000", int((base["Montant"] >= 10000).sum()))
    col[3].metric("🔢 Nombre d'installations", int((base["Operation"] == "Installation").sum()))
    colone= st.columns(3)
    colone[0].metric("💴 CA Total Réalisé", f"{base["Montant"].sum():,.0f}".replace(",", " ")+" XOF")
    colone[1].metric("💴 CA des packs de 5000", f"{base[base["Montant"] < 10000]["Montant"].sum():,.0f}".replace(",", " ")+" XOF")
    colone[2].metric("💴 CA des packs de 10000", f"{base[base["Montant"] >= 10000]["Montant"].sum():,.0f}".replace(",", " ")+" XOF")

        # Evolution des ventes
    evolution["Montant_affiche"] = evolution["Montant"].map(lambda x: f"{x:,.0f}".replace(",", " "))
    fig = px.line(evolution, x="Date", y="Montant",
                  text="Montant_affiche",
                    title="CA des ventes par jour",
                    markers=True)
    fig.update_traces(marker=dict(size=8, color="red", line=dict(width=2, color="DarkSlateGrey")),
                      textfont=dict(size=12, color="white"),
    textposition="top center")
    fig.update_layout(xaxis=dict(tickformat="%d-%m",
                      tickangle=-45, 
                      tickvals=base["Date"].unique()))
    st.plotly_chart(fig, use_container_width=True)


    # Représentation graphique avec plotly
    colon= st.columns(2)
    gra=px.histogram(pack, x="Numéro_Pack", y="Nombre de pack",
                    title="Nombre de ventes par pack")
    gra.update_traces(texttemplate='%{y}', textposition='auto')
    gra.update_layout( xaxis_title="Numéro de Pack",xaxis=dict(tickmode='linear',dtick=1), yaxis_title="Nombre de Packs")
    colon[0].plotly_chart(gra, use_container_width=True)


# graphique des operations
    colon[1].write("Répartition des opérations")
    colon[1].plotly_chart(px.pie(base, names="Operation"), use_container_width=True,title="Répartition des opérations")  





  

    # Performance des agents
    donnee_agre = base.groupby(["Prenom Nom","Operation"]).agg(
        {"Telephone_Client": "count", "Numéro_Pack": "count", "Montant": "sum"}
        ).reset_index()
    donnee_agre = donnee_agre.rename(
    columns={
        "Telephone_Client": "Nombre d'installations",
        "Numéro_Pack": "Nombre de Packs vendus",
        "Montant": "Montant",
    }
    )
    st.subheader("Récapitulatif des ventes et installations des commerciaux")
    st.dataframe(donnee_agre.sort_values(by=["Prenom Nom", "Montant"], ascending=False))

# --- Navigation ---
page = st.sidebar.radio("📁 Menu de navigation", ["Données", "Tableau de bord"])
# URL de récupération des données en CSV
donnee = pd.read_excel(f"https://kf.kobotoolbox.org/api/v2/assets/aiukigovSDuthG6GcpfJc4/export-settings/esY6CBjs5ceExzwiZ7xMRzP/data.xlsx")


# Charger la feuille sélectionnée
nomscol=["Date","Prenom Nom", "Zone", "Prenom_Nom_Client", "Telephone_Client", 
        "Adresse", "Operation", "Numéro_Pack", "Reference Commande", "Montant"]
# Définir les chemins des fichiers source et destination
base=donnee[nomscol]

# --- Page 1 : Visualisation simple ---
if page == "Données":
    if not st.session_state.authentifie:
        login()
        if st.session_state.authentifie:
            visualiser_donnees(base)
    else:
        visualiser_donnees(base)
            
# --- Page 2 : Tableau de bord (protégé) ---
elif page == "Tableau de bord":
    if not st.session_state.authentifie:
        login()
        if st.session_state.authentifie:
            tableau_de_bord(base)
    else:
        tableau_de_bord(base)
        
        # --- Message de bienvenue si connecté --
            