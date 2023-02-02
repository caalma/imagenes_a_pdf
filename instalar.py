#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os
from os.path import realpath, join
from platform import system

os_actual = system()
ruta = realpath('./')
arc_ejecutable = join(ruta, 'imagenes_a_pdf.py')
nombre = 'Imágenes a PDF'
nombre_normalizado = 'imagenes_a_pdf'

if os_actual == 'Windows':

    from win32com.client import Dispatch

    arc_lnk = join(ruta, f'{nombre}.lnk')
    arc_icono = join(ruta, 'icono.ico')

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(arc_lnk)
    shortcut.Targetpath = arc_ejecutable
    shortcut.WorkingDirectory = ruta
    shortcut.IconLocation = arc_icono
    print(dir(shortcut))
    shortcut.save()

    print('Acceso directo creado correctamente.')

elif os_actual == 'Linux':
    arc_icono = join(ruta, 'icono.png')

    code = [
        '[Desktop Entry]',
        f'Name={nombre}',
        'GenericName=Conversor imágenes a pdf',
        'Comment=Convierte y compila imágenes de formato variado a documentos PDF.',
        'Keywords=image;conversor;pdf;',
        f'Icon={arc_icono}',
        'Type=Application',
        'Categories=Image;Office;',
        f'Exec={arc_ejecutable}',
        'Terminal=true'
        ]

    arc_desktop = join(ruta, f'{nombre_normalizado}.desktop')
    with open(arc_desktop, 'w') as f:
        f.write('\n'.join(code))

    print('Lanzador creado correctamente.')

else:
    print('Error: Sistema Operativo "{os_actual}" no está soportado.')
    quit()
