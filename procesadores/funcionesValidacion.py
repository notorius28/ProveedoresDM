import streamlit as st
import json


def comprobarCampos(data, columnas):
    try:
        # Renombramos las columnas
        data.columns = columnas
        return data
    except:
        st.error("Las columnas del fichero no coinciden con las definidas para este proveedor. Revisa el listado de columnas y su orden para que coincida con el siguiente:  \n" + json.dumps(columnas, ensure_ascii=False), icon="🚨")
        st.stop()

def comprobarCamposNombreExacto(data, columnas):
    # Comprobar número de columnas
    if len(data.columns) != len(columnas):
        st.error(
            f"El número de columnas no coincide. Esperado: {len(columnas)}, encontrado: {len(data.columns)}.\n"
            f"Esperado: {columnas}\nEncontrado: {list(data.columns)}",
            icon="🚨"
        )
        st.stop()
    # Comprobar nombres de columnas y orden
    if list(data.columns) != columnas:
        st.error(
            "Los nombres de las columnas no coinciden con los definidos para este proveedor.\n"
            f"Esperado: {columnas}\nEncontrado: {list(data.columns)}",
            icon="🚨"
        )
        st.stop()
    return data