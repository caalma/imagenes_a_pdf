  # Imágenes a pdf

> Utilidad para componer múltiples imágenes en un documento pdf.

## Instalación
Con el siguiente paso se crearán accesos directos o shortcut al ejecutable correspondiente. Soporta sistemas operativos Linux y Windows.
1. Ejecutar `instalar.py`.

## Modo de uso
1. Configurar rutas y seteos dentro de `cfg.yml`.
2. Ejecutar `imagenes_a_pdf.py`.

## Requerimientos
+ imagemagick
+ python3
  + pypdf2
  + wand
  + pywin32 (sólo en windows)

## Falta
+ Verificar la medida de página del pdf no se ajusta a lo esperado.
