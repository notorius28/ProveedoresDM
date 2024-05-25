import streamlit as st
import json

st.title("Diccionario de Artistas")
st.write("En la siguiente ventana se pueden consultas las transformaciones generales de **artistas** que realizan los procesadores:")

with open('diccionarios/artistas.json', 'r', encoding='utf-8') as f:
  dict_formats = json.load(f)

st.json(dict_formats)
st.write("Además, en artistas que comienzan por 'The' (como The Beatles), este artículo se mueve al final precedido de una coma.")