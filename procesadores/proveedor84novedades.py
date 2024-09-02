import pandas as pd
import procesadores.funcionesGenericas as fg
import procesadores.funcionesValidacion as fv
import json
import re
from procesadores.decoradores import multitab_property

@multitab_property(False)
def procesarExcel(data, nombre_hoja = None):

    # Obtener la fecha de lanzamiento desde el texto en la primera fila
    release_date = fg.obtener_fecha_desde_texto(data.columns[0])

    # Iterar sobre las filas para encontrar la primera que cumpla una de las condiciones: o tiene todos los datos rellenos o la primera columna se llama REFERENCIA
    for idx in data.index:
        row = data.iloc[idx]
        if pd.isna(row.iloc[0]):
            print ("El fichero contiene líneas vacías")
        else: 
            if row.notnull().all() or row.iloc[0] == 'REFERENCIA':
                referencia_row = idx
                break
    else:
        referencia_row = None  # Si no se encuentra una fila que cumpla con las condiciones

    # Eliminar todas las filas anteriores a la fila que contiene "REFERENCIA"
    df_cleaned = data.iloc[referencia_row:].reset_index(drop=True)

    if row.iloc[0] == 'REFERENCIA': 
        # Asignar la primera fila como los nuevos encabezados
        df_cleaned.columns = df_cleaned.iloc[0]
        df_cleaned = df_cleaned[1:].reset_index(drop=True)

    # Eliminar filas que están completamente vacías
    df_cleaned = df_cleaned.dropna(how='all')
    data = df_cleaned

    #Establecemos el diseño de los campos del procesador
    templateColumns = ['Referencia Proveedor', 'Autor', 'Título', 'Formato', 'Código de Barras', 'Precio Compra', 'Serie', 'Comentarios', 'Portada',  'Observaciones']

    #Comprobamos la estructura
    fv.comprobarCampos(data, templateColumns)

    # Para el precio, reemplazamos el símbolo de decimal de punto a coma
    data['Precio Compra'] = data['Precio Compra'].astype(str).str.replace('.', ',')

    # Forzamos que la referencia sea un campo texto
    data['Referencia Proveedor'] = data['Referencia Proveedor'].astype(str)

    # Si el código de barras viene vacío, usamos la referencia del Proveedor
    data['Código de Barras'] = data['Código de Barras'].fillna(data['Referencia Proveedor'])

    # Forzamos a texto el código de barras, rellenando con ceros hasta 13 caracteres
    data['Código de Barras'] = data['Código de Barras'].astype(str).str.zfill(13)

    # Eliminamos espacios dobles
    data = data.applymap(fg.eliminar_dobles_espacios)

    # Creamos columnas vacías para Estilo, Sello y Fecha Lanzamiento
    data['Estilo'] = pd.Series(dtype=str)
    data['Sello'] = pd.Series(dtype=str)

    # Para el Autor, ponemos el artículo THE al final precedido de una coma
    data['Autor'] = data['Autor'].apply(fg.mover_the_al_final)

    # Aplicamos canonización de datos a términos como Varios Artistas o BSO
    data = fg.mapear_autor(data, 'Autor')

    # Convertir release_date a datetime si no lo es ya
    if not isinstance(release_date, pd.Timestamp):
        release_date = pd.to_datetime(release_date)

    # Rellenar todas las fechas de lanzamiento con la fecha obtenida
    data['Fecha Lanzamiento'] = release_date.strftime('%d-%m-%Y')

    # Ponemos todos los textos en mayúsculas, excepto Comentarios
    data = fg.dataframe_en_mayusculas_excepto_una_columna (data, 'Comentarios')

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
    columnas_ordenadas = ['Autor', 'Título', 'Sello', 'Fecha Lanzamiento', 'Referencia Proveedor', 'Código de Barras', 'Formato', 'Estilo', 'Comentarios', 'Precio Compra']
    data = data[columnas_ordenadas]

    return(data, data_sin_formato)