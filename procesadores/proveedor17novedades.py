import pandas as pd
import procesadores.funcionesGenericas as fg

def procesarExcel(data):

    num_filas = data.shape[0]
    print("El número de filas del DataFrame es:", num_filas)

    # Comprobamos si, en la primera fila, viene un texto con una fecha para usarla luego como Fecha de Lanzamiento
    release_date = fg.obtener_fecha_desde_texto(data.columns[0])
    print(release_date)

    # Iterar sobre las filas para encontrar la primera que cumpla una de las condiciones: o tiene todos los datos rellenos o la primera columna se llama REFERENCIA
    for idx in data.index:
        row = data.iloc[idx]
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

    # Renombramos las coumnas
    df_cleaned.columns = ['Referencia Proveedor', 'GP', 'Precio Compra', 'Formato', 'Autor', 'Título', 'Sello']

    # Filtrar filas donde "REFERENCIA" no es un número
    df_cleaned = df_cleaned[df_cleaned['Referencia Proveedor'].apply(fg.texto_es_numerico)]

    data = df_cleaned

    #Forzamos que la referencia sea un campo texto
    data['Referencia Proveedor'] = data['Referencia Proveedor'].astype(str)

    #Usamos el valor de REFERENCIA para crear y copiar sus datos a Código de Barras
    barCode = data['Referencia Proveedor'].copy().rename('Código de Barras')
    data['Código de Barras'] = barCode

    #Creamos columnas vacías para Estilo y Comentarios
    data['Estilo'] = pd.Series(dtype=str)
    data['Comentarios'] = pd.Series(dtype=str)

    #Para el Artista, ponemos el artículo THE al final precedido de una coma
    data['Autor'] = data['Autor'].apply(fg.mover_the_al_final)

    #Aplicamos canonización de datos a términos como Varios Artistas o BSO
    dict_autor = {'VARIOUS ARTISTS': 'VARIOS ARTISTAS', 'VARIOUS': 'VARIOS ARTISTAS', 'VARIOS': 'VARIOS ARTISTAS', 'VARIOS BSO': 'BANDA SONORA', 'VARIOS OST': 'BANDA SONORA', 'BSO' : 'BANDA SONORA' }
    data['AutorNormalizado'] = data['Autor']
    data['Autor'] = data['Autor'].map(dict_autor)
    data['Autor'] = data['Autor'].fillna(data['AutorNormalizado'])

    #Rellenamos todas las fechas de lanzamiento con la que hemos obtenido de la primera celda del excel
    data['Fecha Lanzamiento'] = pd.to_datetime(release_date)
    data['Fecha Lanzamiento'] = data['Fecha Lanzamiento'].dt.strftime('%d-%m-%Y')

    #El sello se rellena con "UNIVERSAL"
    data['Sello'] = 'UNIVERSAL'

    columnas_ordenadas = ['Autor', 'Título', 'Sello', 'Fecha Lanzamiento', 'Referencia Proveedor', 'Código de Barras', 'Formato', 'Estilo','Comentarios','Precio Compra']
    data = data[columnas_ordenadas]

    #Ponemos todos los textos en mayúsculas
    data = data.applymap(lambda x: x.upper() if isinstance(x, str) else x)

    dict_formats = {'LP': 'LP','CD': 'CD', 'VINILO':'LP'}
    # Obtener los valores que no tienen equivalencia en el diccionario para la columna 'A'
    formatos_sin_equivalencia = data['Formato'].loc[~data['Formato'].isin(dict_formats.keys())]

    print(formatos_sin_equivalencia)

    data['Formato'] = data['Formato'].map(dict_formats)

    #Quitamos del excel de salida las filas sin formato mapeados
    data = data.dropna(subset=['Formato'])

    return data
