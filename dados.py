import streamlit as st
from trilhas import TRILHAS
from recomendador import recomendar_trilha


# >>> ADD: imports de persistência/analytics
from persistencia import get_db
from analytics import on_app_load, log_event


import json, os, streamlit as st

st.markdown("### Debug de dados (temporário)")
st.write("Pasta existe?", os.path.isdir("dados"))
st.write("Arquivo existe?", os.path.isfile("dados/eventos.json"))
if os.path.isfile("dados/eventos.json"):
    with open("dados/eventos.json", "r", encoding="utf-8") as f:
        st.json(json.load(f))
else:
    st.info("Ainda não há eventos.json; interaja no app (ex.: clique em 'Gerar trilha').")
