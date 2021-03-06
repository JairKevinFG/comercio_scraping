import requests
from bs4 import BeautifulSoup
import pandas as pd

def main(url):
    allnotes = scrap_section(url)
    data = obtener_data(allnotes)
    save_data(data)


def scrap_section(url):
    notes = []
    try:
        comercio = requests.get(url)
        if comercio.status_code == 200:
            s = BeautifulSoup(comercio.text, 'lxml')
            notas = s.findAll('div', attrs={
                'class': 'story-item'
            })
            for nota in notas:
                link = 'https://elcomercio.pe'+ nota.h2.a.get('href')
                notes.append(link)
            return notes
        else:
            print('No se pudo obtener la seccion', url)
    except:
        print('No se pudo obtener la seccion', url)


def obtener_data(allnotes):
    data = []
    for i, nota in enumerate(allnotes):
        print(f'Scrapeando nota {i + 1}/{len(allnotes)}')
        data.append(scrap_nota(nota))
    return data

def scrap_nota(url):
    try:
        nota = requests.get(url)
        if nota.status_code == 200:
            s_nota = BeautifulSoup(nota.text, 'html.parser')
            if '/videos/' in url:
                ret_dict = obtener_infovideo(s_nota)
                ret_dict['url'] = url
            else:
                ret_dict = obtener_info(s_nota)
                ret_dict['url'] = url
            return ret_dict
        else:
            print('No se pudo obtener la nota', url)
    except Exception as e:
        print(f'Error {e}')

def obtener_infovideo(s_nota):
    ret_dict = {}
    #Extraemos el titulo
    informacion = s_nota.find('div', attrs={'class': 'section-video__information'})
    if informacion:
        ret_dict['titulo'] = informacion.h1.get_text()
        ret_dict['subtitulo'] = informacion.p.get_text()
        print(ret_dict['titulo'])
    else:
        ret_dict['titulo'] = None
        ret_dict['subtitulo'] = None

    #Extraemos la imagen:
    imagen = s_nota.find('picture').img.get('src')
    try:
        img_req = requests.get(imagen)
        if img_req.status_code == 200:
            ret_dict['imagen'] = imagen
        else:
            ret_dict['imagen'] = None
    except:
        print('No se pudo obtener la imagen')

    #Extraemos fecha de publicacion
    publicacion = s_nota.find('ul', attrs={'class':'section-video__list-text'}).get_text()
    print(publicacion)
    if publicacion:
        ret_dict['publicacion'] = publicacion
    else:
        ret_dict['publicacion'] = None

    return ret_dict



def obtener_info(s_nota):
    ret_dict = {}

    # Extraemos el titulo y subtitulo
    titulo = s_nota.find('div', attrs={'class': 'sht'})
    if titulo:
        ret_dict['titulo'] = titulo.h1.get_text()
        ret_dict['subtitulo'] = titulo.h2.get_text()
    else:
        ret_dict['titulo'] = None
        ret_dict['subtitulo'] = None

    #Extraer imagen:
    imagen = s_nota.find('picture').img.get('src')
    try:
        img_req = requests.get(imagen)
        if img_req.status_code == 200:
            ret_dict['imagen'] = imagen
        else:
            ret_dict['imagen'] = None
    except:
        print('No se pudo obtener la imagen')

    #cuerpo

    cuerpo = s_nota.find('div', attrs={'class': 'story-contents__content'}).section.find_all('p', attrs={'itemprop': 'description'})
    ret_dict['cuerpo'] = ''
    if cuerpo:
        for p in cuerpo:
            ret_dict['cuerpo'] = ret_dict['cuerpo'] + p.get_text()
    else:
        ret_dict['cuerpo'] = None


    # fecha de publicacion y de actualizacion
    publicacion = s_nota.find('div',attrs={'class': 'story-contents__author-date'}).find_all('time')
    if publicacion:
        ret_dict['publicacion'] = publicacion[0].get('datetime')
        ret_dict['actualizacion'] = publicacion[1].get_text()
    else:
        ret_dict['publicacion'] = None
        ret_dict['actualizacion'] = None

    return ret_dict


def save_data(data):
    df = pd.DataFrame(data)
    df.to_csv('ultimasNoticiasComercio.csv')
    return df

if __name__ == "__main__":
    url = 'https://elcomercio.pe/ultimas-noticias/'
    main(url)
