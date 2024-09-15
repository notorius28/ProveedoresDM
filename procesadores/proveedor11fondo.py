import pandas as pd
import procesadores.funcionesGenericas as fg
import procesadores.funcionesValidacion as fv
import json
import re
from procesadores.decoradores import multitab_property

@multitab_property(False)
def procesarExcel(data, nombre_hoja = None):

    #Establecemos el diseño de los campos del procesador
    templateColumns = ['Referencia Proveedor', 'Descripción Producto', 'Código de Barras', 'Formato', 'Stock', 'Precio Compra']

    #Comprobamos la estructura
    fv.comprobarCampos(data, templateColumns)

    # Forzamos que la referencia sea un campo texto
    data['Referencia Proveedor'] = data['Referencia Proveedor'].astype(str)

    # Si el código de barras viene vacío, usamos la referencia del Proveedor
    data['Código de Barras'] = data['Código de Barras'].fillna(data['Referencia Proveedor'])

    # Forzamos a texto el código de barras, rellenando con ceros hasta 13 caracteres
    data['Código de Barras'] = data['Código de Barras'].astype(str).str.zfill(13)

    # Eliminamos espacios dobles
    data = data.applymap(fg.eliminar_dobles_espacios)

    # Creamos columnas vacías para Estilo, Comentarios, Fecha de Lanzamiento y Sello
    data['Estilo'] = pd.Series(dtype=str)
    data['Comentarios'] = pd.Series(dtype=str)
    data['Fecha Lanzamiento'] = pd.Series(dtype=str)
    data['Sello'] = pd.Series(dtype=str)

    # Usamos str.split() para separar la columna en dos usando '.-' como separador y limpiamos espacios en blanco adicionales
    separacion_autor_titulo = data['Descripción Producto'].str.split('.-', n=1, expand=True)
    separacion_autor_titulo.columns = ['Autor', 'Título']
    data = data.join(separacion_autor_titulo)
    data['Autor'] = data['Autor'].str.strip()
    data['Título'] = data['Título'].str.strip()

    # Para el Autor, ponemos el artículo THE al final precedido de una coma
    data['Autor'] = data['Autor'].apply(fg.mover_the_al_final)

    # Aplicamos canonización de datos a términos como Varios Artistas o BSO
    data = fg.mapear_autor(data, 'Autor')

    # Ponemos todos los textos en mayúsculas
    data = data.applymap(lambda x: x.upper() if isinstance(x, str) else x)

    # Para los formatos, eliminamos el espacio en blanco entre la cantidad y el soporte
    #data['Formato'] = data['Formato'].str.split().agg("".join)
    data['Formato'] = data.apply(lambda row: fg.eliminar_espacios_en_blanco(row['Formato'], row.name), axis=1)

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

    # Detectamos las filas con autor o título vacío
    referencias_sin_titulo_o_autor = data[(data['Autor'].isna()) | (data['Título'].isna()) | (data['Autor'] == '') | (data['Título'] == '')]

    # Detectamos filas con caracteres no ASCII
    regex_ascii = re.compile(r'[^\x00-\x7F]+')
    data_no_ascii = data[data.apply(lambda row: row.astype(str).apply(lambda x: bool(regex_ascii.search(x))).any(), axis=1)] 

    # Añadir estas filas a data_sin_formato
    data_no_exportada = pd.concat([data_sin_formato, referencias_sin_titulo_o_autor, data_no_ascii])

    # Mapeamos formatos del diccionario
    data['Formato'] = data['Formato'].map(dict_formats)

    # Quitamos del excel de salida las filas sin formato mapeados y sin autor o título
    #data = data.dropna(subset=['Formato']) 
    #data = data.dropna(subset=['Autor'])
    #data = data.dropna(subset=['Título'])

    data  = data.drop(data_no_exportada.index)

    # Normalizamos el precio para evitar que se mezclen cifras con comas y puntos como separador decimal
    #data['Precio Compra'] = data['Precio Compra'].apply(fg.normalizar_precio)
    data['Precio Compra'] = data.apply(lambda row: fg.normalizar_precio(row['Precio Compra'], row.name), axis=1)

    # Ordenamos columnas
    columnas_ordenadas = ['Autor', 'Título', 'Sello', 'Fecha Lanzamiento', 'Referencia Proveedor', 'Código de Barras', 'Formato', 'Estilo','Comentarios','Precio Compra']
    data = data[columnas_ordenadas]

    return(data, data_no_exportada)