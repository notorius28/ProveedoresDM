import streamlit as st
import json

st.title("Diccionario de Formatos")
st.write("En la siguiente ventana se pueden consultas las transformaciones generales de **formatos** que realizan los procesadores:")

with open('diccionarios/formatos.json', 'r', encoding='utf-8') as f:
  dict_formats = json.load(f)

st.json(dict_formats)