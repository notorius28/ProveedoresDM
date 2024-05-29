import streamlit as st
import pandas as pd
import glob
import traceback
import importlib.util
from datetime import datetime, timedelta
import pandas_xlwt

# Inicializar el estado si no está presente
if 'archivo_exportado' not in st.session_state:
    st.session_state['archivo_exportado'] = False

# Título de la aplicación y ocupar el ancho completo de página
st.set_page_config(page_title="ProveedoresDM", layout="wide")
st.title("Aplicación de Procesamiento de Archivos Excel")

# Selector de procesador
procesadores_disponibles = glob.glob("procesadores/proveedor*.py")
procesador_seleccionado = st.selectbox("Selecciona un procesador:", procesadores_disponibles)

# Mostramos un mensaje específico para algunos procesadores
if procesador_seleccionado == "procesadores/proveedor42.py":
    st.warning("Para este tipo de fichero, solo se procesarán los lanzamientos del último mes.")
elif procesador_seleccionado == "procesadores/proveedor23novedades.py":
    st.warning("Para este tipo de fichero, se multiplica por 0,30 el precio original") 

# Función para cargar el archivo
def cargar_archivo(uploaded_file):
    if uploaded_file is not None:
        with st.spinner('Cargando archivo...'):
            df = pd.read_excel(uploaded_file)
            st.session_state['archivo_exportado'] = False
        return df
    return None

#Función para obtener el número de pestañas del fichero excel 
def obtener_numero_de_tabs(file):
    xls = pd.ExcelFile(file)
    num_hojas = len(xls.sheet_names)
    return num_hojas

#Función para procesar ficheros excel con múltiples pestañas
def procesar_excel_multiples_tabs(file):
    xls = pd.ExcelFile(file)
    hojas = xls.sheet_names
    num_hojas = len(hojas)
    df_procesado_total = pd.DataFrame()
    df_procesado_sin_formato_total = pd.DataFrame()

    # Importar el procesador seleccionado dinámicamente
    spec = importlib.util.spec_from_file_location(procesador_seleccionado, procesador_seleccionado)
    procesador_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(procesador_module)

    # Creamos una barra de progreso
    progreso = 0
    progress_text = str(progreso) + "/" + str(num_hojas) +  " pestañas procesadas"
    progress_bar = st.progress(0, text=progress_text)

    for hoja in hojas:
        df_hoja = pd.read_excel(file, sheet_name=hoja)
        df_procesado, df_procesado_sin_formato = procesador_module.procesarExcel(df_hoja)
        df_procesado_total = pd.concat([df_procesado_total, df_procesado], ignore_index=True)
        df_procesado_sin_formato_total = pd.concat([df_procesado_sin_formato_total, df_procesado_sin_formato], ignore_index=True)

        # Actualizar la barra de progreso
        progreso += 1
        progress_text = str(progreso) + "/" + str(num_hojas) +  " pestañas procesadas"
        progress_bar.progress(progreso / num_hojas, text=progress_text)

    
    ##Filtramos en este flujo para retornar lanzamientos de los últimos 30 días##
    df_procesado_total['Fecha Lanzamiento'] = pd.to_datetime(df_procesado_total['Fecha Lanzamiento'])
    df_procesado_sin_formato_total['Fecha Lanzamiento'] = pd.to_datetime(df_procesado_sin_formato_total['Fecha Lanzamiento'])
    # Obtener la fecha actual
    hoy = datetime.today()
    # Calcular la fecha correspondiente a 30 días antes
    hace_un_mes = hoy - timedelta(days=30)

    # Filtrar los DataFrame para incluir solo los lanzamientos de los últimos 30 días
    df_procesado_total = df_procesado_total[df_procesado_total['Fecha Lanzamiento'] >= hace_un_mes]
    df_procesado_sin_formato_total = df_procesado_sin_formato_total[df_procesado_sin_formato_total['Fecha Lanzamiento'] >= hace_un_mes]

    #Convertimos la fecha de lanzamiento a formato dd/mm/YYYY
    df_procesado_total['Fecha Lanzamiento'] = df_procesado_total['Fecha Lanzamiento'].dt.strftime('%d-%m-%Y')
    df_procesado_sin_formato_total['Fecha Lanzamiento'] = df_procesado_sin_formato_total['Fecha Lanzamiento'].dt.strftime('%d-%m-%Y')
    st.write("Los resultados generados corresponden sólo a los lanzamientos de los últimos 30 días")
    return df_procesado_total, df_procesado_sin_formato_total

# Subir el archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx","xls"])

# Mostrar el DataFrame y ejecutar el procesamiento
if uploaded_file:

    # Miramos el número de pestañas que tiene el fichero
    numero_tabs = obtener_numero_de_tabs(uploaded_file)
    
    if numero_tabs == 1:
        df = cargar_archivo(uploaded_file)
        if df is not None:
            st.write("Aquí están los datos del fichero original:")
            st.dataframe(df)
            num_filas = df.shape[0]
            st.write("El número de filas del fichero original es **" + str(num_filas)+"**.")
            
            # Botón para procesar el DataFrame
            if st.button("Procesar Fichero"):
                try:
                    # Importar el procesador seleccionado dinámicamente
                    spec = importlib.util.spec_from_file_location(procesador_seleccionado, procesador_seleccionado)
                    procesador_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(procesador_module)
                    
                    # Llamar a la función procesarExcel y mostrar el DataFrame procesado
                    df_procesado, df_procesado_sin_formato = procesador_module.procesarExcel(df)
                    st.write("Fichero procesado:")
                    st.dataframe(df_procesado)

                    st.write("Filas sin formato equivalente:")
                    st.dataframe(df_procesado_sin_formato)
                    
                    #Exportamos el fichero en formato excel 97/2000 (XLS)
                    df_procesado.to_excel('archivo_procesado.xls',engine='xlwt',index=False)
                    num_filas = df_procesado.shape[0]
                    st.success("El fichero procesado ha sido exportado exitosamente. Total de filas: **"+ str(num_filas) +"**")
                    st.session_state.archivo_exportado = True
                except Exception as e:
                    st.error(f"¡Error al procesar el fichero: {str(e)}")
                    st.error(traceback.format_exc())

            # Mostrar el botón de descarga si el archivo ha sido exportado
            if st.session_state['archivo_exportado']:
                st.markdown("### Pulsa este botón para descargar el archivo procesado y exportado")
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
    else:
        st.warning(":exclamation: ADVERTENCIA: El fichero cargado tiene más de una pestaña. La aplicación está en pruebas aún para procesar este tipo de ficheros, por lo que los resultados pueden ser erróneos.")

        # Botón para procesar el DataFrame
        if st.button("Procesar Fichero"):
            try:
                st.write("Procesando fichero con múltiples pestañas...")
                df_procesado, df_procesado_sin_formato =procesar_excel_multiples_tabs(uploaded_file)
                st.write("Fichero procesado:")
                st.dataframe(df_procesado)

                st.write("Filas sin formato equivalente:")
                st.dataframe(df_procesado_sin_formato)
                
                #Exportamos el fichero en formato excel 97/2000 (XLS)
                df_procesado.to_excel('archivo_procesado.xls',engine='xlwt',index=False)
                num_filas = df_procesado.shape[0]
                st.success("El fichero procesado ha sido exportado exitosamente. Total de filas: **"+ str(num_filas) +"**")
                st.session_state.archivo_exportado = True
            except Exception as e:
                st.error(f"¡Error al procesar el fichero: {str(e)}")
                st.error(traceback.format_exc())

                    # Mostrar el botón de descarga si el archivo ha sido exportado
        if st.session_state['archivo_exportado']:
            st.markdown("### Pulsa este botón para descargar el archivo procesado y exportado")
            with open("archivo_procesado.xls", "rb") as file:
                
                # Renombramos el fichero 
                now = datetime.now()
                timestamp = now.strftime("%Y%m%d_%H%M%S")
                filename_out = f'procesado_{timestamp}.xls'

                # Botón de descarga
                st.download_button(
                    label="Descargar Excel Procesado",
                    data=file,
                    file_name=filename_out,
                    mime="application/vnd.ms-excel."
                )
