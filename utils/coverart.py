import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import time

# Función para obtener el release ID de MusicBrainz
def get_release_id(barcode, title, artist):
    url = f"https://musicbrainz.org/ws/2/release/"
    #query = f'barcode:{barcode} AND release:{title} AND artist:{artist}'
    query = f'barcode:{barcode}'
    params = {
        'query': query,
        'fmt': 'json'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json()
    if results['releases']:
        return results['releases'][0]['id']
    return None

# Función para obtener la URL de la imagen desde Cover Art Archive
def get_cover_art_url(release_id):
    if release_id:
        cover_art_url = f"http://coverartarchive.org/release/{release_id}/front-500"
        return cover_art_url
    return None

# Función para descargar y abrir la imagen desde una URL
def download_image(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None
    

def buscarPortadasExcel(df):
    # Crear una nueva columna en el DataFrame para mostrar las imágenes con overlay
    for index, row in df.iterrows():
        codigoBarras = row['Código de Barras']
        titulo = row['Título']
        autor = row['Autor']
        releaseId = get_release_id(codigoBarras, titulo, autor)
        image_url = get_cover_art_url(releaseId)
        df.at[index, 'Enlace Portada'] = image_url
        print(titulo)
        time.sleep(0.4)

    return df
