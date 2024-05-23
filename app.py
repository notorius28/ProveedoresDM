import streamlit as st
import pandas as pd
import glob
import traceback
import importlib.util
import datetime
import pandas_xlwt

# Inicializar el estado si no está presente
if 'archivo_exportado' not in st.session_state:
    st.session_state['archivo_exportado'] = False


# Título de la aplicación y ocupar el ancho completo de página
st.set_page_config(page_title="Aplicación de Procesamiento de Archivos Excel", layout="wide")

# Selector de procesador
procesadores_disponibles = glob.glob("procesadores/proveedor*.py")
procesador_seleccionado = st.selectbox("Selecciona un procesador:", procesadores_disponibles)

# Mostramos un mensaje específico para algunos procesadores
if procesador_seleccionado == "procesadores/proveedor42.py":
    st.write("Para este tipo de fichero, solo se procesarán los lanzamientos del último mes.")

# Función para cargar el archivo
def cargar_archivo(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        return df
    return None

# Subir el archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx","xls"])

# Mostrar el DataFrame y ejecutar el procesamiento
if uploaded_file:
    df = cargar_archivo(uploaded_file)
    if df is not None:
        st.write("Aquí están los datos del fichero original:")
        st.dataframe(df)
        
        # Botón para procesar el DataFrame
        if st.button("Procesar Fichero"):
            try:
                # Importar el procesador seleccionado dinámicamente
                spec = importlib.util.spec_from_file_location(procesador_seleccionado, procesador_seleccionado)
                procesador_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(procesador_module)
                
                # Llamar a la función procesarExcel y mostrar el DataFrame procesado
                df_procesado = procesador_module.procesarExcel(df)
                st.write("Fichero procesado:")
                st.dataframe(df_procesado)
                
                #Exportamos el fichero en formato excel 97/2000 (XLS)
                df_procesado.to_excel('archivo_procesado.xls',engine='xlwt',index=False)

                st.success("El fichero procesado ha sido exportado exitosamente.")
                st.session_state.archivo_exportado = True
            except Exception as e:
                st.error(f"¡Error al procesar el fichero: {str(e)}")
                st.error(traceback.format_exc())

        # Mostrar el botón de descarga si el archivo ha sido exportado
        if st.session_state['archivo_exportado']:
            st.markdown("### Pulsa este botón para descargar el aarchivo procesado y exportado")
            with open("archivo_procesado.xls", "rb") as file:
                
                # Renombramos el fichero 
                now = datetime.datetime.now()
                timestamp = now.strftime("%Y%m%d_%H%M%S")
                filename_out = f'procesado_{timestamp}.xls'

                # Botón de descarga
                st.download_button(
                    label="Descargar Excel Procesado",
                    data=file,
                    file_name=filename_out,
                    mime="application/vnd.ms-excel."
                )
