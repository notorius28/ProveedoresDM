import pandas as pd
import procesadores.funcionesGenericas as fg
import procesadores.funcionesValidacion as fv
import json
import streamlit as st
import re
from procesadores.decoradores import multitab_property, dateontab_property

@multitab_property(True)
@dateontab_property(True)
def procesarExcel(data, nombre_hoja = None, multitab = False):

    # Obtener la fecha de lanzamiento desde el texto en la primera fila
    if multitab:
        release_date = fg.obtener_fecha_desde_texto(nombre_hoja)
    else: 
        release_date = fg.obtener_fecha_desde_texto(data.columns[0])

    # Aplica la función y maneja los NaN llenándolos con False antes de aplicar la máscara
    mask = data.apply(lambda row: row.notnull().all() or row.iloc[0] == 'REFERENCIA', axis=1).fillna(False)

    # Encuentra el índice de la primera fila que cumple con la condición
    referencia_row = mask[mask].index[0]

    # Eliminar filas anteriores a la fila de referencia
    data = data.iloc[referencia_row:].reset_index(drop=True)

    # Si la primera fila es 'REFERENCIA', usarla como encabezados
    if data.iloc[0, 0] == 'REFERENCIA':
        data.columns = data.iloc[0]
        data = data[1:].reset_index(drop=True)

    # Eliminar filas que no estén completamente rellenas
    data = data.dropna(how='any')

    #Establecemos el diseño de los campos del procesador
    templateColumns = ['Referencia Proveedor', 'GP', 'Precio Compra', 'Formato', 'Autor', 'Título', 'Sello']

    #Comprobamos la estructura
    fv.comprobarCampos(data, templateColumns)

    # Forzamos que la referencia sea un campo texto
    data['Referencia Proveedor'] = data['Referencia Proveedor'].astype(str)

    # Si el código de barras viene vacío, usamos la referencia del Proveedor
    data['Código de Barras'] = data['Referencia Proveedor'].astype(str).str.zfill(13)

    #Eliminamos espacios dobles
    data = data.applymap(fg.eliminar_dobles_espacios)

    # Creamos columnas vacías para Estilo y Comentarios
    data['Estilo'] = pd.Series(dtype=str)
    data['Comentarios'] = pd.Series(dtype=str)

    # Para el Autor, ponemos el artículo THE al final precedido de una coma
    data['Autor'] = data['Autor'].apply(fg.mover_the_al_final)

    # Aplicamos canonización de datos a términos como Varios Artistas o BSO
    data = fg.mapear_autor(data, 'Autor')

    # Convertir release_date a datetime si no lo es ya
    if not isinstance(release_date, pd.Timestamp):
        release_date = pd.to_datetime(release_date)

    # Rellenar todas las fechas de lanzamiento con la fecha obtenida
    data['Fecha Lanzamiento'] = release_date.strftime('%d-%m-%Y')

    #Si no es multipestaña, rellenamos el sello con el valor "UNIVERSAL"
    if multitab == False:
        data['Sello'] = 'UNIVERSAL'

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

    # Normalizamos el precio para evitar que se mezclen cifras con comas y puntos como separador decimal
    data['Precio Compra'] = data.apply(lambda row: fg.normalizar_precio(row['Precio Compra'], row.name), axis=1)

    # Ordenamos columnas
    columnas_ordenadas = ['Autor', 'Título', 'Sello', 'Fecha Lanzamiento', 'Referencia Proveedor', 'Código de Barras', 'Formato', 'Estilo','Comentarios','Precio Compra']
    data = data[columnas_ordenadas]

    return data, data_sin_formato
