import pandas as pd
import procesadores.funcionesGenericas as fg
import procesadores.funcionesValidacion as fv
import json
from datetime import datetime, timedelta
import re
from procesadores.decoradores import multitab_property, dateontab_property

@multitab_property(False)
@dateontab_property(False)
def procesarExcel(data, nombre_hoja = None):

    # Establecemos el diseño de los campos del proveedor
    templateColumns = ['Product Reference Number', 'Artist', 'Title', 'Local Marketing Company', 'Conf.', 'Component units', 'Release date', 'Price code', 'Unit PPD', 'Currency', 'Disponibilidad']

    # Comprobamos la estructura (debe tener mismo número de columnas y nombres)
    fv.comprobarCamposNombreExacto(data, templateColumns)

    # Renombramos las columnas para que coincidan con las del template
    data.columns = ['Código de Barras', 'Autor', 'Título', 'Sello', 'Formato', 'Component units', 'Fecha Lanzamiento', 'Price code', 'Precio Compra', 'Currency', 'Disponibilidad']

    # Filtramos en este procesador para retornar lanzamientos de los últimos 30 días
    data['Fecha Lanzamiento'] = pd.to_datetime(data['Fecha Lanzamiento'])
    hoy = datetime.today()
    hace_un_mes = hoy - timedelta(days=30)
    data = data[data['Fecha Lanzamiento'] >= hace_un_mes]

    # Convertimos la fecha de lanzamiento a formato dd/mm/YYYY
    data['Fecha Lanzamiento'] = data['Fecha Lanzamiento'].dt.strftime('%d-%m-%Y')

    # Forzamos a texto el código de barras, rellenando con ceros hasta 13 caracteres
    data['Código de Barras'] = data['Código de Barras'].astype(str).str.zfill(13)

    # Eliminamos espacios dobles
    data = data.applymap(fg.eliminar_dobles_espacios)

    # Usar el código de barras para crear la referencia del proveedor
    data['Referencia Proveedor'] = data['Código de Barras']

    # Creamos columnas vacías para Estilo y Comentarios
    data['Estilo'] = pd.Series(dtype=str)
    data['Comentarios'] = pd.Series(dtype=str)

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