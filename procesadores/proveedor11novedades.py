import pandas as pd
import procesadores.funcionesGenericas as fg
import procesadores.funcionesValidacion as fv
import json
import re
from procesadores.decoradores import multitab_property

@multitab_property(False)
def procesarExcel(data, nombre_hoja = None):

    #Establecemos el diseño de los campos del procesador
    templateColumns = ['Referencia Proveedor', 'Autor', 'Título', 'Comentarios', 'Serie', 'Código de Barras', 'Tipo Música', 'Fecha Lanzamiento', 'Precio Compra', 'Sello', 'Formato']

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

    # Creamos columnas vacías para Estilo
    data['Estilo'] = pd.Series(dtype=str)

    # Para el Autor, ponemos el artículo THE al final precedido de una coma
    data['Autor'] = data['Autor'].apply(fg.mover_the_al_final)

    # Aplicamos canonización de datos a términos como Varios Artistas o BSO
    data = fg.mapear_autor(data, 'Autor')

    # Convertimos la fecha de lanzamiento a formato dd/mm/YYYY
    data['Fecha Lanzamiento'] = data['Fecha Lanzamiento'].dt.strftime('%d-%m-%Y')

    # Ponemos todos los textos en mayúsculas, excepto Comentarios
    data = fg.dataframe_en_mayusculas_excepto_una_columna (data, 'Comentarios')

    # Para los formatos, eliminamos el espacio en blanco entre la cantidad y el soporte
    data['Formato'] = data['Formato'].str.split().agg("".join)

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
    data['Precio Compra'] = data['Precio Compra'].apply(fg.normalizar_precio)

    # Ordenamos columnas
    columnas_ordenadas = ['Autor', 'Título', 'Sello', 'Fecha Lanzamiento', 'Referencia Proveedor', 'Código de Barras', 'Formato', 'Estilo','Comentarios','Precio Compra']
    data = data[columnas_ordenadas]

    return(data, data_sin_formato)