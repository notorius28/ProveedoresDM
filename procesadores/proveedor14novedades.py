import pandas as pd
import procesadores.funcionesGenericas as fg
import json
import re

def procesarExcel(data):

    # Renombramos las coumnas
    data.columns = ['Autor', 'Título', 'Referencia Proveedor', 'Formato', 'G.T', 'Precio Compra', 'Código de Barras', 'Sello', 'Fecha Lanzamiento']

    #Forzamos que la referencia y código de barras sean un campo texto
    data['Referencia Proveedor'] = data['Referencia Proveedor'].astype(str)
    data['Código de Barras'] = data['Código de Barras'].astype(str)

    #Eliminamos espacios dobles
    data = data.applymap(fg.eliminar_dobles_espacios)

        #Creamos columnas vacías para Estilo y Comentarios
    data['Estilo'] = pd.Series(dtype=str)
    data['Comentarios'] = pd.Series(dtype=str)

    #Para el Autora, ponemos el artículo THE al final precedido de una coma
    data['Autor'] = data['Autor'].apply(fg.mover_the_al_final)
    #Aplicamos canonización de datos a términos como Varios Artistas o BSO
    data = fg.mapearAutor(data, 'Autor')

    #Convertimos la fecha de lanzamiento a formato dd/mm/YYYY
    data['Fecha Lanzamiento'] = data['Fecha Lanzamiento'].dt.strftime('%d-%m-%Y')

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
    print(formatos_sin_equivalencia)
    data['Formato'] = data['Formato'].map(dict_formats)

    #Quitamos del excel de salida las filas sin formato mapeados
    data = data.dropna(subset=['Formato'])

    #Ordenamos columnas
    columnas_ordenadas = ['Autor', 'Título', 'Sello', 'Fecha Lanzamiento', 'Referencia Proveedor', 'Código de Barras', 'Formato', 'Estilo','Comentarios','Precio Compra']
    data = data[columnas_ordenadas]

    #Ponemos todos los textos en mayúsculas
    data = data.applymap(lambda x: x.upper() if isinstance(x, str) else x)

    return(data)