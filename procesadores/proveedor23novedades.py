import pandas as pd
import procesadores.funcionesGenericas as fg
import json
import streamlit as st
import re

def procesarExcel(data, nombre_hoja = None):
    # Comprobar si, en la celda B3, viene un texto con una fecha para usarla luego como Fecha de Lanzamiento
    release_date = fg.extraer_fecha(data.iat[1,1])

    # Iterar sobre las filas para encontrar la primera que cumpla una de las condiciones: o tiene todos los datos rellenos o la primera columna se llama INTÉRPRETE
    for idx in data.index:
        row = data.iloc[idx]
        if row.notnull().all() or row.iloc[0] == 'INTÉRPRETE':
            referencia_row = idx
            break
    else:
        referencia_row = None  # Si no se encuentra una fila que cumpla con las condiciones

    # Eliminar todas las filas anteriores a la fila que contiene "REFERENCIA"
    data = data.iloc[referencia_row:].reset_index(drop=True)  

    if row.iloc[0] == 'INTÉRPRETE': 
    # Asignar la primera fila como los nuevos encabezados
        data.columns = data.iloc[0]
        data = data[1:].reset_index(drop=True)

    # Eliminar filas que están completamente vacías o que no tengan título
    data = data.dropna(how='all')
    data = data.dropna(subset=['TÍTULO'])

    # Renombramos las coumnas
    data.columns = ['Autor', 'Título', 'Referencia Proveedor', 'Código de Barras','Formato', 'Precio Compra',  'Estilo Proveedor', 'Sello']

    # Forzamos que la referencia sea un campo texto
    data['Referencia Proveedor'] = data['Referencia Proveedor'].astype(str)

    # Forzamos a texto el código de barras, rellenando con ceros hasta 13 caracteres
    data['Código de Barras'] = data['Código de Barras'].astype(str).str.zfill(13)

    # Filtramos las filas donde 'Código de Barras' no es un número
    data = data[data['Código de Barras'].astype(str).apply(str.isdigit)]

    # Eliminamos espacios dobles
    data = data.applymap(fg.eliminar_dobles_espacios)

    # Creamos columnas vacías para Estilo y Comentarios
    data['Estilo'] = pd.Series(dtype=str)
    data['Comentarios'] = pd.Series(dtype=str)

    # Para el Autor, ponemos el artículo THE al final precedido de una coma
    data['Autor'] = data['Autor'].apply(fg.mover_the_al_final)

    # Aplicamos canonización de datos a términos como Varios Artistas o BSO
    data = fg.mapear_autor(data, 'Autor')

    # Asignamos la fecha de lanzamiento global del fichero
    data['Fecha Lanzamiento'] = release_date

    # Forzamos el precio de compra a tipo float, para que podamos multiplicar su valor después
    data['Precio Compra'] = data['Precio Compra'].astype(float)

    # Aplicamos un 0,30 al precio 
    data['Precio Compra'] = data['Precio Compra'] * 0.3

    # Ponemos todos los textos en mayúsculas
    data = data.applymap(lambda x: x.upper() if isinstance(x, str) else x)

    # Leemos el diccionario de formatos para mapearlos con el fichero
    with open('diccionarios/formatos.json', 'r', encoding='utf-8') as f:
        dict_formats = json.load(f)
         # Ordenar términos por longitud descendente para evitar coincidencias parciales
        terminos = list(dict_formats.keys())
        terminos.sort(key=len, reverse=True)

    # Para los formatos que incluyen variación de color o edición, dejamos el formato solo como LP y añadimos la variación al Título
    patronFormato = r'^(' + '|'.join(re.escape(term) for term in terminos) + r')\s+(.+)'
    data[['FormatoIzq', 'VariaciónDer']] = data['Formato'].str.extract(patronFormato, expand=True)
    conjuntoConVariacion = data['VariaciónDer'].notna()
    data.loc[conjuntoConVariacion, 'Título'] = data.loc[conjuntoConVariacion, 'Título'].astype(str) + ' (EDICIÓN VINILO ' + data.loc[conjuntoConVariacion, 'VariaciónDer'] + ')'
    data.loc[conjuntoConVariacion, 'Formato'] = data['FormatoIzq']

    # Obtener los valores que no tienen equivalencia en el diccionario para la columna 'A'
    formatos_sin_equivalencia = data['Formato'].loc[~data['Formato'].isin(dict_formats.keys())]
    
    # Creamos un dataframe aparte con las filas excluidas por no encontrar un formato mapeado
    data_sin_formato = data.loc[data['Formato'].isin(formatos_sin_equivalencia)]
    
    # Mapeamos formatos del diccionario
    data['Formato'] = data['Formato'].map(dict_formats)

    # Quitamos del excel de salida las filas sin formato mapeados
    data = data.dropna(subset=['Formato'])

    #Ordenamos columnas
    columnas_ordenadas = ['Autor', 'Título', 'Sello', 'Fecha Lanzamiento', 'Referencia Proveedor', 'Código de Barras', 'Formato', 'Estilo','Comentarios','Precio Compra']
    data = data[columnas_ordenadas]

    return data, data_sin_formato
