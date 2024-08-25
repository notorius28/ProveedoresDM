import pandas as pd
import streamlit as st
import json


def comprobarCampos (data, columnas):
    
    try:
        # Renombramos las columnas
        data.columns = columnas
        return data
    except:
        st.error("Las columnas del fichero no coinciden con las definidas para este proveedor. Revisa el listado de columnas y su orden para que coincida con el siguiente:  \n" + json.dumps(columnas, ensure_ascii= False), icon="🚨")
        st.stop()