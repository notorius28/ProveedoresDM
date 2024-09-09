import streamlit as st
import pandas as pd
import traceback
import procesadores.funcionesGenericas as fg
import utils.coverart as portadas     
from PIL import Image
import urllib.request 
import os


# Título de la aplicación y ocupar el ancho completo de página
st.set_page_config(page_title="ProveedoresDM", layout="wide")
st.title("Búsqueda de Portadas de Referencias")

# Función para cargar el archivo
def cargar_archivo(uploaded_file):
    if uploaded_file is not None:
        with st.spinner('Cargando archivo...'):
            df = pd.read_excel(uploaded_file)
            st.session_state['archivo_exportado'] = False
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
        num_filas = df.shape[0]
        st.write("El número de filas del fichero original es **" + str(num_filas)+"**.")
        
        # Botón para procesar el DataFrame
        if st.button("Buscar Portadas"):
            try:
                              
                # Llamar a la función procesarExcel y mostrar el DataFrame procesado
                df_procesado = portadas.buscarPortadasExcel(df)
                st.write("Estas son las portadas encontradas:")

                for index, row in df.iterrows():
                    st.write(row['Autor'] + ' - ' + row['Título'])
                    try:
                        # Intentar descargar la imagen
                        urllib.request.urlretrieve(row['Enlace Portada'], 'cover.jpg')
                        # Abrir y mostrar la imagen
                        img = Image.open('cover.jpg')
                        st.image(img)
                    except Exception as e:
                        # Manejar el error (por ejemplo, mostrando un mensaje de error en la interfaz)
                        st.error(f"Error al descargar la imagen: {e}")
                        # O mostrar una imagen predeterminada o un mensaje
                        st.write("Imagen no disponible")

                # Limpiar el archivo temporal si existe
                if os.path.exists('cover.jpg'):
                    os.remove('cover.jpg')

                

            except Exception as e:
                st.error(f"¡Error al procesar el fichero: {str(e)}")
                st.error(traceback.format_exc())


