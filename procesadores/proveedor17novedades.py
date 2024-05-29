import pandas as pd
import procesadores.funcionesGenericas as fg
import json
import streamlit as st

def procesarExcel(data):
    # Obtener la fecha de lanzamiento desde el texto en la primera fila
    release_date = fg.obtener_fecha_desde_texto(data.columns[0])

    # Encontrar la fila que contiene 'REFERENCIA' o está completamente llena
    referencia_row = data.apply(lambda row: row.notnull().all() or row.iloc[0] == 'REFERENCIA', axis=1).idxmax()

    # Eliminar filas anteriores a la fila de referencia
    df_cleaned = data.iloc[referencia_row:].reset_index(drop=True)

    # Si la primera fila es 'REFERENCIA', usarla como encabezados
    if df_cleaned.iloc[0, 0] == 'REFERENCIA':
        df_cleaned.columns = df_cleaned.iloc[0]
        df_cleaned = df_cleaned[1:].reset_index(drop=True)

    # Eliminar filas completamente vacías
    df_cleaned = df_cleaned.dropna(how='all')

    # Renombrar las columnas
    df_cleaned.columns = ['Referencia Proveedor', 'GP', 'Precio Compra', 'Formato', 'Autor', 'Título', 'Sello']

    # Filtrar filas donde 'REFERENCIA' no es un número
    df_cleaned = df_cleaned[df_cleaned['Referencia Proveedor'].astype(str).apply(str.isdigit)]

    # Forzar que la referencia sea un campo de texto
    df_cleaned['Referencia Proveedor'] = df_cleaned['Referencia Proveedor'].astype(str)

    # Usar la referencia para crear y copiar datos a 'Código de Barras'
    df_cleaned['Código de Barras'] = df_cleaned['Referencia Proveedor']

    # Crear columnas vacías para 'Estilo' y 'Comentarios'
    df_cleaned['Estilo'] = ''
    df_cleaned['Comentarios'] = ''

    # Mover 'THE' al final de 'Autor'
    df_cleaned['Autor'] = df_cleaned['Autor'].apply(fg.mover_the_al_final)
    # Mapear términos como 'Varios Artistas' o 'BSO'
    df_cleaned = fg.mapear_autor(df_cleaned, 'Autor')

    # Convertir release_date a datetime si no lo es ya
    if not isinstance(release_date, pd.Timestamp):
        release_date = pd.to_datetime(release_date)

    # Rellenar todas las fechas de lanzamiento con la fecha obtenida
    df_cleaned['Fecha Lanzamiento'] = release_date.strftime('%d-%m-%Y')

    # Rellenar 'Sello' con 'UNIVERSAL'
    df_cleaned['Sello'] = 'UNIVERSAL'

    # Ordenar columnas
    columnas_ordenadas = ['Autor', 'Título', 'Sello', 'Fecha Lanzamiento', 'Referencia Proveedor', 'Código de Barras', 'Formato', 'Estilo','Comentarios','Precio Compra']
    df_cleaned = df_cleaned[columnas_ordenadas]

    # Convertir texto a mayúsculas
    df_cleaned = df_cleaned.applymap(lambda x: x.upper() if isinstance(x, str) else x)

    # Leer el diccionario de formatos
    with open('diccionarios/formatos.json', 'r', encoding='utf-8') as f:
        dict_formats = json.load(f)
    
    # Mapear los formatos
    df_cleaned['Formato'] = df_cleaned['Formato'].map(dict_formats)

    # Eliminar filas sin formato mapeado
    df_cleaned = df_cleaned.dropna(subset=['Formato'])

    # Obtener filas excluidas por no encontrar un formato mapeado
    data_sin_formato = df_cleaned[~df_cleaned['Formato'].isin(dict_formats.values())]

    return df_cleaned, data_sin_formato
