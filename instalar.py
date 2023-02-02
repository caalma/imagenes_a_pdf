#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os
from os.path import realpath, join
from platform import system

os_actual = system()
ruta = realpath('./')
arc_ejecutable = join(ruta, 'imagenes_a_pdf.py')
nombre = 'Imágenes a PDF'

if os_actual == 'Windows':

    from win32com.client import Dispatch

    arc_lnk = join(ruta, f'{nombre}.lnk')

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(arc_lnk)
    shortcut.Targetpath = arc_ejecutable
    shortcut.WorkingDirectory = ruta
    shortcut.IconLocation = join(ruta, 'icono.ico')
    print(dir(shortcut))
    shortcut.save()

elif os_actual == 'Linux':
    print('luego ....')
