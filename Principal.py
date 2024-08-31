import streamlit as st
import pandas as pd
import glob
import traceback
import importlib.util
from datetime import datetime, timedelta
import procesadores.funcionesGenericas as fg
import pandas_xlwt 
from io import BytesIO


#Inicializamos variables de sesión
if "cached_file" not in st.session_state:
    st.session_state.cached_file = False
if "excel_dict" not in st.session_state:
    st.session_state.excel_dict = False
if 'exported_file' not in st.session_state:
    st.session_state.exported_file = False
if 'process_ok' not in st.session_state:
    st.session_state.process_ok = False
if 'show_button' not in st.session_state:
    st.session_state.show_button = False
if 'clicked' not in st.session_state:
    st.session_state.clicked = False
if 'progressbar' not in st.session_state:
    st.session_state.progressbar = False
if 'df_procesado_total' not in st.session_state:
    st.session_state.df_procesado_total = pd.DataFrame()
if 'df_procesado_sin_formato_total' not in st.session_state:
    st.session_state.df_procesado_sin_formato_total = pd.DataFrame()

def reiniciar_estados():
    st.session_state.cached_file = False
    st.session_state.excel_dict = False
    st.session_state.exported_file = False
    st.session_state.process_ok = False
    st.session_state.show_button = False
    st.session_state.clicked = False
    st.session_state.progressbar = False
    st.session_state.df_procesado_total = pd.DataFrame()
    st.session_state.df_procesado_sin_formato_total = pd.DataFrame()

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

# Función para cachear el archivo
@st.cache_data
def cachear_fichero(file):
    return file

# Función para leer el fichero (con caché)
@st.cache_data(show_spinner="Leyendo archivo Excel...")
def leer_excel(uploaded_file):
    if uploaded_file is not None:
        file_bytes = BytesIO(uploaded_file.read())
        df = pd.read_excel(file_bytes, sheet_name=None, dtype=object)
        return df
    return None

# Función para obtener el número de pestañas del fichero excel 
def obtener_numero_de_tabs(file):
    num_hojas = len(file)
    return num_hojas

def click_boton_procesar_fichero():
    st.session_state.clicked = True

# Mostrarmos el botón de importar fichero al cargar el formulario
ficheroExcel = st.file_uploader("Sube tu archivo Excel", type=["xlsx","xls"], accept_multiple_files=False, on_change=reiniciar_estados)
st.session_state.cached_file = cachear_fichero(ficheroExcel)

# Si se ha subido el fichero, leemos el excel y lo guardamos en un diccionario
if st.session_state.cached_file:
    st.session_state.excel_dict = leer_excel(st.session_state.cached_file)
    #st.session_state.cached_file = None

# Con el fichero excel en memoria, ejecutamos los procesos de transformación
if st.session_state.excel_dict: 

    # Miramos el número de pestañas que tiene el fichero
    numero_tabs = obtener_numero_de_tabs(st.session_state.excel_dict)
    if numero_tabs > 1: 
        st.warning(":exclamation: ADVERTENCIA: El fichero cargado tiene más de una pestaña.")

    # Importar el procesador seleccionado dinámicamente
    spec = importlib.util.spec_from_file_location(procesador_seleccionado, procesador_seleccionado)
    procesador_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(procesador_module)
    multitab = procesador_module.procesarExcel.multitab

    # Obtener la fecha actual
    hoy = datetime.today()
    # Calcular la fecha correspondiente a 30 días antes
    hace_un_mes = hoy - timedelta(days=30)

    #Si el proveedor se ha definido que no es multitab pero el fichero tiene varias pestañas, eliminamos todas las que no sean la primera
    if multitab is False and numero_tabs > 1:
        primera_clave, primer_valor = next(iter(st.session_state.excel_dict.items()))
        st.session_state.excel_dict.clear()
        st.session_state.excel_dict[primera_clave] = primer_valor
        numero_tabs = 1
        
    # En un bucle, leemos cada pestaña del excel
    for nombre, hoja in st.session_state.excel_dict.items():
        
        if multitab is True and numero_tabs > 1:
            # En multipestaña, obtenemos la fecha del nombre de la pestaña y no mostramos datos previso
            try:
                fecha_tab = datetime.strptime(fg.obtener_fecha_desde_texto(nombre),'%Y-%m-%d') 
            except:
                st.error("La fecha en la pestaña " + nombre + " no tiene la estructura correcta. Renombre la pestaña.", icon="🚨")
                st.stop()
        else:
            # Con una sola pestaña, mostramos la vista previa y el total de registros
            fecha_tab = hoy
            st.write("Aquí están los datos del fichero original:")
            st.dataframe(hoja)
            num_filas = hoja.shape[0]
            st.write("El número de filas del fichero original es **" + str(num_filas)+"**.")
        
        # Mostramos el botón para procesar el fichero
        if not st.session_state.show_button:
            st.button("Procesar Fichero", on_click=click_boton_procesar_fichero)
            st.session_state.show_button = True

        # Procesamos el fichero si no se ha exportado previamente
        if st.session_state.clicked and st.session_state.exported_file == False:

            # Mostramos una barra de progreso
            if not st.session_state.progressbar:
                progreso = 0
                progress_text = str(progreso) + "/" + str(numero_tabs) +  " pestañas procesadas"
                progress_bar = st.progress(progreso / numero_tabs, text=progress_text)
                st.session_state.progressbar = True
            
            try:
                # Comprobamos que la pestaña sea de una fecha reciente y procesamos el excel, almacenando los resultados en dos dataframes                             
                if fecha_tab >= hace_un_mes:
                    if multitab is True and numero_tabs > 1:
                        df_procesado, df_procesado_sin_formato = procesador_module.procesarExcel(hoja, nombre, multitab)
                    else:
                        df_procesado, df_procesado_sin_formato = procesador_module.procesarExcel(hoja, nombre)
                    st.session_state.df_procesado_total = pd.concat([st.session_state.df_procesado_total, df_procesado], ignore_index=True)
                    st.session_state.df_procesado_sin_formato_total = pd.concat([st.session_state.df_procesado_sin_formato_total, df_procesado_sin_formato], ignore_index=True)

                # Actualizar la barra de progreso
                progreso += 1
                progress_text = str(progreso) + "/" + str(numero_tabs) +  " pestañas procesadas"
                progress_bar.progress(progreso / numero_tabs, text=progress_text)

                if progreso == numero_tabs:

                    if st.session_state.df_procesado_total.empty:
                        st.warning("No se ha podido generar un fichero de salida porque no hay registros con fecha de lanzamiento reciente.")
                    else:
                        # Convertimos la fecha de lanzamiento a formato fecha para la exportación, indicando que el día va al principio
                        st.session_state.df_procesado_total['Fecha Lanzamiento'] = pd.to_datetime(st.session_state.df_procesado_total['Fecha Lanzamiento'], dayfirst=True)
                        st.session_state.df_procesado_sin_formato_total['Fecha Lanzamiento'] = pd.to_datetime(st.session_state.df_procesado_sin_formato_total['Fecha Lanzamiento'], dayfirst=True)

                        # Convertimos la fecha de lanzamiento a formato dd/mm/YYYY
                        st.session_state.df_procesado_total['Fecha Lanzamiento'] = st.session_state.df_procesado_total['Fecha Lanzamiento'].dt.strftime('%d-%m-%Y')
                        st.session_state.df_procesado_sin_formato_total['Fecha Lanzamiento'] = st.session_state.df_procesado_sin_formato_total['Fecha Lanzamiento'].dt.strftime('%d-%m-%Y')

                        # Exportamos el fichero en formato excel 97/2000 (XLS)
                        st.session_state.df_procesado_total.to_excel('archivo_procesado.xls',engine='xlwt',index=False)
                        st.session_state.exported_file = True
                        st.session_state.process_ok = True

            except Exception as e:
                st.error(f"¡Error al procesar el fichero: {str(e)}")
                st.error(traceback.format_exc())

    # Si todo ha ido bien, mostramos los resultados en pantalla
    if st.session_state.process_ok:
        st.write("Fichero procesado:")
        st.dataframe(st.session_state.df_procesado_total)

        st.write("Registros no exportables:")
        st.dataframe(st.session_state.df_procesado_sin_formato_total)

        num_filas = st.session_state.df_procesado_total.shape[0]
        st.success("El fichero procesado ha sido exportado exitosamente. Total de filas: **"+ str(num_filas) +"**")

    # Mostrar el botón de descarga si el archivo ha sido exportado
    if st.session_state.exported_file:
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
        

