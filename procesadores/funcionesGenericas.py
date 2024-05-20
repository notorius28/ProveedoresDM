import re
from datetime import datetime
import json

def obtener_fecha_desde_texto(text):
    # Definir la expresión regular para extraer la fecha con y sin año
    date_pattern_with_year = r'(\d{1,2})\s(\w+)\s(\d{2})'
    date_pattern_without_year = r'(\d{1,2})\s(\w+)'
    
    # Intentar encontrar una fecha con año primero
    match = re.search(date_pattern_with_year, text)
    if match:
        day, month, year = match.groups()
    else:
        # Intentar encontrar una fecha sin año
        match = re.search(date_pattern_without_year, text)
        if match:
            day, month = match.groups()
            # Obtener el año actual
            year = datetime.now().year % 100  # Tomar los dos últimos dígitos del año actual
            year = f"{year:02d}"
        else:
            return None  # No se encontró una fecha válida
    
    # Diccionario para convertir meses en español a números
    months = {
        'ENERO': '01', 'FEBRERO': '02', 'MARZO': '03', 'ABRIL': '04',
        'MAYO': '05', 'JUNIO': '06', 'JULIO': '07', 'AGOSTO': '08',
        'SEPTIEMBRE': '09', 'OCTUBRE': '10', 'NOVIEMBRE': '11', 'DICIEMBRE': '12'
    }
    
    # Convertir el mes a un número
    month_num = months.get(month.upper())
    if month_num:
        # Asumimos que el año es del siglo XXI
        date_str = f"20{year}-{month_num}-{day.zfill(2)}"
        return date_str
    return None

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

def mapearAutor(data, column):
    #Leemos el diccionario de formatos para mapearlos con el fichero
    with open('diccionarios/artistas.json', 'r', encoding='utf-8') as f:
        dict_autor = json.load(f)
    data['AutorNormalizado'] = data[column]
    data[column] = data[column].map(dict_autor)
    data[column] = data[column].fillna(data['AutorNormalizado'])
    return data