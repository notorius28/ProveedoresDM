import pandas as pd
import procesadores.funcionesGenericas as fg
import json
import re
import numpy as np

def procesarExcel(data, nombre_hoja = None):

    # Renombramos las coumnas
    data.columns = ['Fecha Lanzamiento', 'Referencia Proveedor', 'Código de Barras', 'Autor', 'Título', 'Formato', 'Serie', 'Precio Compra', 'Estilo',  'Sello', 'Stock']

    # Forzamos que la referencia sea un campo texto
    data['Referencia Proveedor'] = data['Referencia Proveedor'].astype(str)

    # Eliminamos espacios dobles
    data = data.applymap(fg.eliminar_dobles_espacios)

    # Creamos columnas vacías para Estilo, Comentarios y Fecha Lanzamiento
    data['Estilo'] = pd.Series(dtype=str)
    data['Comentarios'] = pd.Series(dtype=str)

    # Forzamos a texto el código de barras, rellenando con ceros hasta 13 caracteres
    data['Código de Barras'] = data['Código de Barras'].astype(str).str.zfill(13)

    # Para el Autor, ponemos el artículo THE al final precedido de una coma
    data['Autor'] = data['Autor'].apply(fg.mover_the_al_final)

    # Aplicamos canonización de datos a términos como Varios Artistas o BSO
    data = fg.mapear_autor(data, 'Autor')

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
    # Ponemos como nulos los registros en 'VariaciónDer' cuyo valor sea "Vinilo", para que no se repita esa palabra
    data.loc[data['VariaciónDer'] == "VINILO", 'VariaciónDer'] = np.nan
    conjuntoConVariacion = data['VariaciónDer'].notna()

    # Solo ponemos la variante para los formatos LP en este proveedor
    data.loc[(data['FormatoIzq'] == "LP") & (data['VariaciónDer'].notna()), 'Título'] =  data.loc[conjuntoConVariacion, 'Título'].astype(str) + ' (EDICIÓN VINILO ' + data.loc[conjuntoConVariacion, 'VariaciónDer'] + ')' 
    data.loc[conjuntoConVariacion, 'Formato'] = data['FormatoIzq']

    # Obtener los valores que no tienen equivalencia en el diccionario para la columna 'A'
    formatos_sin_equivalencia = data['Formato'].loc[~data['Formato'].isin(dict_formats.keys())]

    # Creamos un dataframe aparte con las filas excluidas por no encontrar un formato mapeado
    data_sin_formato = data.loc[data['Formato'].isin(formatos_sin_equivalencia)]

    # Mapeamos formatos del diccionario
    data['Formato'] = data['Formato'].map(dict_formats)

    # Quitamos del excel de salida las filas sin formato mapeados
    data = data.dropna(subset=['Formato'])

    # Ordenamos columnas
    columnas_ordenadas = ['Autor', 'Título', 'Sello', 'Fecha Lanzamiento', 'Referencia Proveedor', 'Código de Barras', 'Formato', 'Estilo','Comentarios','Precio Compra']
    data = data[columnas_ordenadas]

    return(data, data_sin_formato)