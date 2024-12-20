import re
from datetime import datetime
import json
import streamlit as st

def obtener_fecha_desde_texto(text):
    # Lista de patrones
    patterns = [
        (r'(\d{1,2})\s(\w+)\s(\d{2,4})', lambda match: match.groups()),
        (r'(\d{1,2})\sDE\s(\w+)\s(\d{4})', lambda match: match.groups()),
        (r'(\d{1,2})\sDE\s(\w+)\sDE\s(\d{4})', lambda match: match.groups()),
        (r'(\d{1,2})\s(\w+)', lambda match: (*match.groups(), f"{datetime.now().year % 100:02d}"))
    ]

    # Diccionario para convertir meses en español a números
    months = {
        'ENERO': '01', 'FEBRERO': '02', 'MARZO': '03', 'ABRIL': '04',
        'MAYO': '05', 'JUNIO': '06', 'JULIO': '07', 'AGOSTO': '08',
        'SEPTIEMBRE': '09', 'OCTUBRE': '10', 'NOVIEMBRE': '11', 'DICIEMBRE': '12'
    }
    
    for pattern, processor in patterns:
        match = re.search(pattern, text)
        if match:
                day, month, year = processor(match)
                
                # Convertir el mes a un número
                month_num = months.get(month.upper())
                if month_num:
                    # Convertir el año a un entero y ajustar al siglo XXI si es necesario
                    year = int(year)
                    if year < 100:  # Si el año tiene dos dígitos
                        year += 2000
                    
                    # Formatear la fecha como cadena
                    date_str = f"{year}-{month_num}-{day.zfill(2)}"
                    return date_str
    return None  # No se encontró una fecha válida

def eliminar_dobles_espacios(texto):
    if isinstance(texto, str):
        return texto.replace(r'\s+', ' ')
    else:
        return texto

def mover_the_al_final(texto):
    #Comprobamos primero que la cadena es texto y está rellena
    if isinstance(texto, str) and texto.strip():
        palabras = texto.split()
        if len(palabras) >= 2 and palabras[0].upper() == 'THE':
            return ' '.join(palabras[1:] + [', THE']).replace(' , THE',', THE')
        else:
            return texto
    else:
        return(texto)
    
def texto_es_numerico(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def mapear_autor(data, column):
    #Leemos el diccionario de formatos para mapearlos con el fichero
    with open('diccionarios/artistas.json', 'r', encoding='utf-8') as f:
        dict_autor = json.load(f)
    data['AutorNormalizado'] = data[column]
    data[column] = data[column].map(dict_autor)
    data[column] = data[column].fillna(data['AutorNormalizado'])
    return data

def extraer_fecha(texto):
    # Definir la expresión regular para fechas dd/mm/YYYY
    regex = r"\b(\d{2}/\d{2}/\d{4})\b"
    # Buscar la primera coincidencia en el texto
    coincidencia = re.search(regex, texto)    
    # Si hay una coincidencia, devolver el valor encontrado
    if coincidencia:
        return coincidencia.group(1)
    else:
        return None
    
def extraer_edicion_del_formato(data, dict_formats):
    # Ordenar términos por longitud descendente para evitar coincidencias parciales
    terminos = list(dict_formats.keys())
    terminos.sort(key=len, reverse=True)

    #Para los formatos que incluyen variación de color o edición, dejamos el formato solo como LP y añadimos la variación al Título
    patronFormato = r'^(' + '|'.join(re.escape(term) for term in terminos) + r')\s+(.+)'
    data[['FormatoIzq', 'VariaciónDer']] = data['Formato'].str.extract(patronFormato, expand=True)
    conjuntoConVariacion = data['VariaciónDer'].notna()
    data.loc[conjuntoConVariacion, 'Título'] = data.loc[conjuntoConVariacion, 'Título'].astype(str) + ' (EDICIÓN ' + data['FormatoIzq'] + ' ' + data.loc[conjuntoConVariacion, 'VariaciónDer'] + ')'
    data.loc[conjuntoConVariacion, 'Formato'] = data['FormatoIzq']

    return data

def dataframe_en_mayusculas_excepto_una_columna(df, exclude_column):
    for column in df.columns:
        if column != exclude_column:
            df[column] = df[column].apply(lambda x: x.upper() if isinstance(x, str) else x)
    return df

def normalizar_precio(valor, indice):
    errores = []  
    try:
        # Convertir a string por si no lo es
        precio_str = str(valor)
        # Convertimos las comas a punto para que Pandas lo interpreta como decimal
        if ',' in precio_str:
            precio_str = precio_str.replace(',', '.')
        # Convertimos el string a float y luego lo dejamos en formato de coma como decimal
        return float(precio_str)
    except Exception as e:
        # Si hay un error, lo agregamos a la lista de errores con la fila afectada
        errores.append(f"Error en fila {indice}, valor: {valor}, mensaje: {e}")
        return valor  # Retorna el valor original si falla
    
def eliminar_espacios_en_blanco(valor, indice):
    errores = []  
    try:
        # Si el valor es una cadena, eliminamos los espacios
        return ''.join(valor.split()) if isinstance(valor, str) else valor
    except Exception as e:
        # Si hay un error, lo agregamos a la lista de errores con la fila afectada
        errores.append(f"Error en fila {indice}, valor: {valor}, mensaje: {e}")
        return valor  # Retorna el valor original si falla

def reemplazar_caracteres_no_validos(df, columna):
    df[columna] = df[columna].str.replace('\u2033', '"', regex=False)
