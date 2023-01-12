#!/usr/bin/python3
# -*- coding:utf-8 -*-

from os import listdir, makedirs, remove
from os.path import exists, splitext, basename, realpath
from shutil import rmtree
from sys import argv
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from wand.image import Image
import yaml
import webbrowser
from datetime import datetime

rTmp = "./tmp/"
notificaciones = []
html_notificacion = """<!DOCTYPE html><html><head><meta charset="utf-8">
<meta http-equiv='cache-control' content='no-cache'><meta http-equiv='expires' content='0'><meta http-equiv='pragma' content='no-cache'><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__titulo__</title><style>
* { font-family: sans-serif; color: #111; }
body { display: flex; justify-content: center; }
h1 { padding: 0; margin: .5em; }
header { text-align:center; margin: 0 0 30px 0; max-width: 800px; }
li { list-style: none; margin: 2px 0; padding: 6px 12px; border-radius: 3px; }
b { color: #111; background: #fff; padding: 2px 4px; border-radius: 5px; margin: 0 11px 0 0; font-size: .8em; }
.container { padding: 30px; }
.error { background: #fc7b7b; }
.atencion { background: #ffeb3b; }
.listo { background: #84f36a; }
</style></head><body><div class="container">
<header><h1>__titulo__</h1><p>Fecha de notificación: __fecha__</p></header>
<section><ul>__notificaciones__</ul></section></div></body></html>
"""

def mostrar_notificaciones():
    lNot = []
    for i, text in enumerate(notificaciones):
        style = text.split('!')[0].lower()
        lNot.append(f'<li class="{style}"><b>{i}</b>{text}</li>')
    ree = {
        '__titulo__': 'Imágenes a PDF : Notificación',
        '__fecha__': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '__notificaciones__': ''.join(lNot[::-1])
    }

    html = html_notificacion
    for k in ree.keys():
        v = ree[k]
        html = html.replace(k, v)

    aNot = 'log_notificacion.html'
    with open(aNot, 'w') as f:
        f.write(html)

    webbrowser.open(aNot)

def notificar(text):
    global notificaciones
    notificaciones.append(text)

def filtro_extension(lista, ee):
    r = []
    for a in lista:
        if splitext(a)[-1].strip('.').lower() in ee:
            r.append(a)
        else:
            notificar(f'ATENCION! El archivo "{a}" fué ignorado por extensión.')
    return r

def filtro_ignorar(lista, ii):
    r = []
    for a in lista:
        if not a in ii:
            r.append(a)
        else:
            notificar(f'ATENCION! Se ignoró el archivo "{a}".')
    return r

def filtro_utilizar(lista, ruta):
    r = []
    for a in lista:
        if exists(f'{ruta}{a}'):
            r.append(a)
        else:
            notificar(f'ATENCION! No existe el archivo "{a}".')
    return r

def ordenar(lista, modo):
    if modo == '09-az':
        return sorted(lista)
    elif modo == 'za-90':
        return sorted(lista, reverse=True)
    else:
        notificar(f'ATENCION! El modo de orden "{modo}" no existe.')
        return lista

def mm_a_px(mm, dpi):
    return int(mm * 0.039370 * dpi)


def procesar_imagen(arc, seteo, general):
    im = Image(filename=arc)
    pag = {'ancho': im.width, 'alto': im.height}
    k = 'paleta'

    if k in seteo['ajustes']:
        kpal = seteo['ajustes'][k]
        paletas = {
            'gris': 'grayscale',
            'rgb': 'truecolor',
            'bn': 'bilevel'
        }
        if kpal in list(paletas.keys()):
            im.type = paletas[kpal]
        else:
            notificar(f'ATENCION! La paleta "{pal} no es válida."')

    k = 'niveles'
    if k in seteo['ajustes']:
        d = seteo['ajustes'][k]
        im.level(d['negro'], d['blanco'], d['gama'])

    k = 'redimensionar'
    if k in seteo['ajustes']:
        d = seteo['ajustes'][k]
        kmed = d['medida']
        if not kmed in general['medidas']:
            raise Exception(f'ERROR: La medida de hoja "{kmed}" no está registrada.')
        pag['ancho'] = mm_a_px(general['medidas'][kmed][0], seteo['dpi'])
        pag['alto'] = mm_a_px(general['medidas'][kmed][1], seteo['dpi'])

        ian, ial = pag['ancho'], pag['alto']

        if ('encajar' in d) and (d['encajar']):
            ian = ian - mm_a_px(d['margen'][0] * 2, seteo['dpi'])
            ial = ial - mm_a_px(d['margen'][1] * 2, seteo['dpi'])
            im.transform(resize=f'{ian}x{ial}')
        else:
            im.transform(resize=f'{ian}x{ial}!')


    im2 = Image(width=pag['ancho'],
                height=pag['alto'],
                background=general['color_pagina'],
                resolution=seteo['dpi'],
                units='pixelsperinch')

    im2.composite(im, gravity='center')

    im2.convert('jpeg')
    im2.interlace_scheme = 'jpeg'
    im2.format = 'jpeg'
    im2.compression = general['compresion_jpg'][0]
    im2.compression_quality = general['compresion_jpg'][1]

    arcF = r'---img-temporal.jpg'
    im2.save(filename=arcF)
    im3 = Image(filename=arcF)
    remove(arcF)

    return im3

def agregar_metadata(nArc, metadatos={}, seteo={}, general={}):
    reader = PdfReader(nArc)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    k = 'redimensionar'
    if k in seteo['ajustes']:
        kmed = seteo['ajustes'][k]['medida']
        wPag = general['medidas'][kmed][0]
        hPag = general['medidas'][kmed][1]
        mdSize = '{wPag} x {hPag} mm'
    else:
        mdSize = 'Mix Sizes'

    metadatos['/Paper Size'] = mdSize
    metadatos['/Creator'] = 'PyPDF2'
    metadatos['/Created'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    writer.add_metadata(metadatos)

    with open(nArc, 'wb') as f:
        writer.write(f)


def multiimagen_a_pdf(seteo, general):
    rOri = seteo['ruta_imagenes']
    aDes = seteo['ruta_archivo_pdf']

    lArc = listdir(rOri)

    lArc = filtro_extension(lArc, general['tipos_de_imagenes_permitidos'])

    kUti= 'imagenes_a_utilizar'
    if kUti in seteo:
        lArc = filtro_utilizar(seteo[kUti], rOri)

    kIgn = 'imagenes_a_ignorar'
    if kIgn in seteo:
        lArc = filtro_ignorar(lArc, seteo[kIgn])

    tArc = len(lArc)

    if exists(rTmp):
        rmtree(rTmp)

    makedirs(rTmp, exist_ok=True)

    if tArc == 0:
        notificar('ATENCION! No hay imágenes que procesar.')
        return False
    elif tArc == 1:
        ai = lArc[0]
        im = procesar_imagen(f'{rOri}{ai}', seteo, general)
        im.save(filename=aDes)

    else:
        for ai in lArc:
            im = procesar_imagen(f'{rOri}{ai}', seteo, general)
            im.save(filename=f'{rTmp}{ai}.pdf')

        li = [f'{rTmp}{a}.pdf' for a in lArc]

        kOrd = 'orden'
        if kOrd in seteo:
            li = ordenar(li, seteo[kOrd])

        merger = PdfMerger()
        for pdf in li:
            merger.append(open(pdf, 'rb'))

        with open(aDes, "wb") as f:
            merger.write(f)


    if exists(aDes):
        mDat = seteo['metadatos'] if 'metadatos' in seteo else {}
        agregar_metadata(aDes, mDat, seteo, general )

    # FALTA borrar tmp
    if exists(rTmp):
        rmtree(rTmp)

    tPag = len(lArc)
    texPag = 'página' if tPag == 1 else 'páginas'
    notificar(f'LISTO! El pdf se guardó en: {aDes}.\nContiene {tPag} {texPag}.')
    return True

if __name__ == '__main__':
    try:
        control = ''
        with open('cfg.yml', 'r') as f:
            cfg = yaml.safe_load(f)

            if len(argv) == 1:
                # usa seteo de actua, de la configuracion
                seteos_solicitados = cfg['seteo_actual']
            elif len(argv) > 1:
                # usa los seteos solicitados por parámetro
                seteos_solicitados = argv[1:]

            for kset in seteos_solicitados:
                # usa los seteos solicitados por parámetro
                if kset in cfg['seteos']:
                    multiimagen_a_pdf(cfg['seteos'][kset], cfg['general'])
                    notificar(f'LISTO! Seteo "{kset}" finalizado.')
                else:
                    notificar(f'ATENCION! Algo extraño pasó con el seteo "{kset}".')
                    notificar(f'ERROR! El seteo "{kset}" no existe.')

    except Exception as e:
        notificar(f'ERROR! {e}')

    if True:
        mostrar_notificaciones()
