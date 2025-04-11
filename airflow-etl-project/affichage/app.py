import streamlit as st
import pandas as pd
import numpy as np

# Titre de l'application
st.title("Ma première application Streamlit")

# Texte simple
st.write("Voici un exemple d'application Streamlit.")

# Générer des données aléatoires
data = pd.DataFrame(
    np.random.randn(10, 3), columns=["Colonne A", "Colonne B", "Colonne C"]
)

# Afficher un tableau
st.write("Voici un tableau de données :", data)

# Afficher un graphique
st.line_chart(data)

# Ajouter un widget interactif
slider_value = st.slider("Choisissez une valeur", 0, 100, 50)
st.write(f"Vous avez choisi : {slider_value}")
