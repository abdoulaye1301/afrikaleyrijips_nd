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

st.title("Éditeur Excel avec plusieurs feuilles")
# Upload du fichier Excel
donnee = pd.read_excel("https://kf.kobotoolbox.org/api/v2/assets/aiukigovSDuthG6GcpfJc4/export-settings/esY6CBjs5ceExzwiZ7xMRzP/data.xlsx")



# Choisir une feuille à modifier
#feuille_selectionnee = st.sidebar.selectbox("Choisissez une feuille à éditer :",  )

# Charger la feuille sélectionnée
nomscol=["Date","Prenom Nom", "Zone", "Prenom_Nom_Client", "Telephone_Client", 
         "Adresse", "Operation", "Numéro_Pack", "Reference Commande", "Montant", "Commentaire"]
# Définir les chemins des fichiers source et destination
base=donnee[nomscol]
base["Date"] = base["Date"].dt.date
# donnee["Mois"] = donnee["Date"].dt.month
base
# Agrégation par jour
evolution = base.groupby("Date").size().reset_index(name="Nombre")
pack = base.groupby("Numéro_Pack").size().reset_index(name="Nombre")

st.subheader("📊 Évolution des collectes dans le temps (interactive)")
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
gra=px.histogram(pack, x="Numéro_Pack", y="Nombre",
                 title="Nombre de collectes par numéro de pack",)
colon[1].plotly_chart(gra, use_container_width=True)

st.subheader("📋 Données brutes")
st.plotly_chart(px.pie(base, names="Operation"), use_container_width=True)  