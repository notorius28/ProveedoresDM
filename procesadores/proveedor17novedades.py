import pandas as pd
import procesadores.funcionesGenericas as fg
import json
import streamlit as st
import re

def procesarExcel(data, nombre_hoja = None):

    # Utilizamos una variable para controlar si el excel es multipestaña o no
    if nombre_hoja:
        multitab = True
    else:
        multitab = False

    # Obtener la fecha de lanzamiento desde el texto en la primera fila
    if multitab:
        release_date = fg.obtener_fecha_desde_texto(nombre_hoja)
    else: 
        release_date = fg.obtener_fecha_desde_texto(data.columns[0])

    # Encontrar la fila que contiene 'REFERENCIA' o está completamente llena
    referencia_row = data.apply(lambda row: row.notnull().all() or row.iloc[0] == 'REFERENCIA', axis=1).idxmax()

    # Eliminar filas anteriores a la fila de referencia
    data = data.iloc[referencia_row:].reset_index(drop=True)

    # Si la primera fila es 'REFERENCIA', usarla como encabezados
    if data.iloc[0, 0] == 'REFERENCIA':
        data.columns = data.iloc[0]
        data = data[1:].reset_index(drop=True)

    # Eliminar filas completamente vacías
    data = data.dropna(how='all')

    # Renombrar las columnas
    data.columns = ['Referencia Proveedor', 'GP', 'Precio Compra', 'Formato', 'Autor', 'Título', 'Sello']

    # Filtrar filas donde 'REFERENCIA' no es un número
    data = data[data['Referencia Proveedor'].astype(str).apply(str.isdigit)]

    # Forzar que la referencia sea un campo de texto
    data['Referencia Proveedor'] = data['Referencia Proveedor'].astype(str)

    # Usar la referencia para crear y copiar datos a 'Código de Barras'
    data['Código de Barras'] = data['Referencia Proveedor']

    # Crear columnas vacías para 'Estilo' y 'Comentarios'
    data['Estilo'] = ''
    data['Comentarios'] = ''

    # Mover 'THE' al final de 'Autor'
    data['Autor'] = data['Autor'].apply(fg.mover_the_al_final)
    # Mapear términos como 'Varios Artistas' o 'BSO'
    data = fg.mapear_autor(data, 'Autor')

    # Convertir release_date a datetime si no lo es ya
    if not isinstance(release_date, pd.Timestamp):
        release_date = pd.to_datetime(release_date)

    # Rellenar todas las fechas de lanzamiento con la fecha obtenida
    data['Fecha Lanzamiento'] = release_date.strftime('%d-%m-%Y')

    if multitab == False:
        # Rellenar 'Sello' con 'UNIVERSAL'
        data['Sello'] = 'UNIVERSAL'

    #Ponemos todos los textos en mayúsculas
    data = data.applymap(lambda x: x.upper() if isinstance(x, str) else x)

    #Leemos el diccionario de formatos para mapearlos con el fichero
    with open('diccionarios/formatos.json', 'r', encoding='utf-8') as f:
        dict_formats = json.load(f)
         # Ordenar términos por longitud descendente para evitar coincidencias parciales
        terminos = list(dict_formats.keys())
        terminos.sort(key=len, reverse=True)

    #Para los formatos que incluyen variación de color o edición, dejamos el formato solo como LP y añadimos la variación al Título
    patronFormato = r'^(' + '|'.join(re.escape(term) for term in terminos) + r')\s+(.+)'
    data[['FormatoIzq', 'VariaciónDer']] = data['Formato'].str.extract(patronFormato, expand=True)
    conjuntoConVariacion = data['VariaciónDer'].notna()
    data.loc[conjuntoConVariacion, 'Título'] = data.loc[conjuntoConVariacion, 'Título'].astype(str) + ' (EDICIÓN VINILO ' + data.loc[conjuntoConVariacion, 'VariaciónDer'] + ')'
    data.loc[conjuntoConVariacion, 'Formato'] = data['FormatoIzq']

    # Obtener los valores que no tienen equivalencia en el diccionario para la columna 'A'
    formatos_sin_equivalencia = data['Formato'].loc[~data['Formato'].isin(dict_formats.keys())]
    
    #Creamos un dataframe aparte con las filas excluidas por no encontrar un formato mapeado
    data_sin_formato = data.loc[data['Formato'].isin(formatos_sin_equivalencia)]
    
    #Mapeamos formatos del diccionario
    data['Formato'] = data['Formato'].map(dict_formats)

    #Quitamos del excel de salida las filas sin formato mapeados
    data = data.dropna(subset=['Formato'])

    #Ordenamos columnas
    columnas_ordenadas = ['Autor', 'Título', 'Sello', 'Fecha Lanzamiento', 'Referencia Proveedor', 'Código de Barras', 'Formato', 'Estilo','Comentarios','Precio Compra']
    data = data[columnas_ordenadas]

    return data, data_sin_formato
