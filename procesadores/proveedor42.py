import pandas as pd
import procesadores.funcionesGenericas as fg
import json
from datetime import datetime, timedelta
import re

def procesarExcel(data):

    # Renombramos las coumnas
    data.columns = ['Product Reference Number', 'Artist', 'Title', 'Local Marketing Company', 'Conf.', 'Component units', 'Release date', 'Price code', 'Unit PPD', 'Currency', 'Av. Stock']

    
    ##Filtramos en este procesador para retornar lanzamientos de los últimos 30 días##
    data['Release date'] = pd.to_datetime(data['Release date'])
    # Obtener la fecha actual
    hoy = datetime.today()
    # Calcular la fecha correspondiente a 30 días antes
    hace_un_mes = hoy - timedelta(days=30)

    # Filtrar el DataFrame para incluir solo los lanzamientos de los últimos 30 días
    data = data[data['Release date'] >= hace_un_mes]

    #Convertimos la fecha de lanzamiento a formato dd/mm/YYYY
    data['Release date'] = data['Release date'].dt.strftime('%d-%m-%Y')

    #Forzamos que la referencia sea un campo texto
    data['Product Reference Number'] = data['Product Reference Number'].astype(str)

    #Eliminamos espacios dobles
    data = data.applymap(fg.eliminar_dobles_espacios)

    #Usamos el valor de REFERENCIA para crear y copiar sus datos a Código de Barras
    barCode = data['Product Reference Number'].copy().rename('Código de Barras')
    data['Código de Barras'] = barCode

    #Creamos columnas vacías para Estilo y Comentarios
    data['Estilo'] = pd.Series(dtype=str)
    data['Comentarios'] = pd.Series(dtype=str)

    #Para el Artista, ponemos el artículo THE al final precedido de una coma
    data['Artist'] = data['Artist'].apply(fg.mover_the_al_final)
    #Aplicamos canonización de datos a términos como Varios Artistas o BSO
    data = fg.mapear_autor(data, 'Artist')

    #Renombramos las columnas
    data.rename(columns={"Artist":"Autor","Title":"Título","Local Marketing Company":"Sello","Release date":"Fecha Lanzamiento", "Product Reference Number":"Referencia Proveedor", "Conf.":"Formato", "Unit PPD":"Precio Compra"}, inplace=True)
    
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
