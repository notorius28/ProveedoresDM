import streamlit as st
import pandas as pd
import glob
import traceback
import importlib.util

# Título de la aplicación
st.title("Aplicación de Procesamiento de Archivos Excel")

# Selector de procesador
procesadores_disponibles = glob.glob("procesadores/*.py")
procesador_seleccionado = st.selectbox("Selecciona un procesador:", procesadores_disponibles)

# Función para cargar el archivo
def cargar_archivo(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        return df
    return None

# Subir el archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

# Variable de estado para controlar la exportación
if "archivo_exportado" not in st.session_state:
    st.session_state.archivo_exportado = False

# Mostrar el DataFrame y ejecutar el procesamiento
if uploaded_file:
    df = cargar_archivo(uploaded_file)
    if df is not None:
        st.write("Aquí está tu DataFrame:")
        st.dataframe(df)
        
        # Botón para procesar el DataFrame
        if st.button("Procesar DataFrame"):
            try:
                # Importar el procesador seleccionado dinámicamente
                spec = importlib.util.spec_from_file_location(procesador_seleccionado, procesador_seleccionado)
                procesador_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(procesador_module)
                
                # Llamar a la función procesarExcel y mostrar el DataFrame procesado
                df_procesado = procesador_module.procesarExcel(df)
                st.write("DataFrame procesado:")
                st.dataframe(df_procesado)
                
                # Exportar el DataFrame procesado y actualizar el estado
                df_procesado.to_excel("archivo_procesado.xlsx", index=False)
                st.success("El DataFrame procesado ha sido exportado exitosamente.")
                st.session_state.archivo_exportado = True
            except Exception as e:
                st.error(f"¡Error al procesar el DataFrame: {str(e)}")
                st.error(traceback.format_exc())

# Mostrar el botón de descarga si el archivo ha sido exportado
if st.session_state.archivo_exportado:
    st.markdown("### Descargar el archivo procesado exportado")
    with open("archivo_procesado.xlsx", "rb") as file:
        st.download_button(
            label="Descargar Excel Procesado",
            data=file,
            file_name="archivo_procesado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
