"""
########################################################################
####### INSTRUCCIONES DE USO ###########################################
########################################################################

1) Descomprimir todas los archivos de imagenes LANDSAT en una carpeta vacia
	Deben quedar en la misma carpeta, todas las bandas descomprimidas -> un archivo de imagen (Ej.: TIFF, img) por cada banda de cada escena LANDSAT
	No importa si algunas imangenes quedan dentro de subcarpetas

2) en bash (linea de comandos Linux), ejecutar la orden:

python ruta_script ruta_imagenes ruta_resultados <banda deseada1><banda deseada2><banda deseada n>

EJEMPLO:
python /media/GUINDOWS_XP/IMAGENES/Landsat/tmp/stackear_landsat_v00.py
/media/GUINDOWS_XP/IMAGENES/Landsat/ORIGEN		# ruta donde se descomprimieron todas las bandas de todas las escenas
/media/GUINDOWS_XP/IMAGENES/Landsat/DESTINO		# ruta donde se ubicaran los stacks resultado

'345'											# bandas 3, 4 y 5 (En el estack final estan ordenadas de menor a mayor)

LO ANTERIOR DEBERIA EJECUTARSE EN UNA MISMA LINEA, ENTONCES:
python /media/GUINDOWS_XP/IMAGENES/Landsat/tmp/stackear_landsat_v00.py /media/GUINDOWS_XP/IMAGENES/Landsat/ORIGEN /media/GUINDOWS_XP/IMAGENES/Landsat/DESTINO 345

########################################################################
"""

import sys
import os
from osgeo import gdal
from osgeo import *
from osgeo.gdalconst import *
import glob

def listar_archivos(ruta):
	"""
	Lista recursivamente los archivos contenidos en ruta

	Argumentos
	-----------------
	ruta: Ruta al directorio donde estan los archivos a listar
	"""
		
	lista_rutas = []
	for carpeta in os.walk(ruta):
		dirpath = carpeta[0]
		archivos = carpeta[2]
	
		for archivo in archivos:
			lista_rutas.append(os.path.join(dirpath, archivo))
	
	lista_rutas.sort()
	return lista_rutas

def metadata_de_dataset(imagen):
	"""
	Devuelve los metadatos de georreferencia y estructura de la imagen dado uin archivo de imagen

	Argumentos
	------------------------
	imagen: Imagen de la que se quiere importar la info

	"""
	imagen_entrada = imagen
	
	## EXTRAE DATOS DEL ARCHIVO DE ENTRADA:
	georef = imagen_entrada.GetGeoTransform()
	projref = imagen_entrada.GetProjectionRef()
	nro_bandas = imagen_entrada.RasterCount
	x_size = imagen_entrada.RasterXSize
	y_size = imagen_entrada.RasterYSize
	
	return georef, projref, nro_bandas, x_size, y_size

def array_de_archivo(ruta, nro_banda, cuadro=False):
	"""
	Devuelve un array (numpy) dado un archivo y una banda seleccionada

	Argumentos
	---------------------
	ruta: string de la ruta al ARCHIVO
	nro_banda: entero de la banda que se quiere extraer
	"""
		
	imagen = gdal.Open(ruta)

	return array_de_dataset(imagen, nro_banda, cuadro)

def array_de_dataset(imagen, nro_banda, cuadro=False):
	"""
	Devuelve un arreglo de numpy dado un objeto de archivo de gdal y un numero de banda

	Argumentos
	-------------------
	imagen: objeto de gdal de la imagen
	nro_banda: entero de la banda que se quiere extraer
	"""
		
	layer=imagen.GetRasterBand(nro_banda)
	
	if cuadro==False:
		metadata = metadata_de_dataset(imagen)
		x = 0
		y = 0
		x_size = metadata[3]
		y_size = metadata[4]
	else:
		x = cuadro[0]
		y = cuadro[1]
		x_size = cuadro[2]
		y_size = cuadro[3]
	
	matriz = layer.ReadAsArray(x,y,x_size,y_size)
	
	return matriz

def stack_job(ruta_sal, rutas_en, driver_nom='GTiff', tipo_dato=GDT_Int16):
	"""
	Devuelve un stack en el formato especificado dada una ruta al directorio donde estan las imagenes
	que se quieren apilar

	Argumentos:
	----------------------
	ruta_sal: string de la ruta final del archivo
	rutas_en: iterable con las rutas a las bandas para armar la imagen
	driver_nom: Formato gdal del archivo de salida
	tipo_dato: tipo de datos en formato gdal

	"""
	
	print
	for i in rutas_en:
		print i
	print '	->', ruta_sal
	
		
	img1 = gdal.Open(rutas_en[0])
	georef, projref, nro_bandas, x_size, y_size = metadata_de_dataset(img1)
	nro_bandas = len(rutas_en)
	
	driver = gdal.GetDriverByName(driver_nom)
	
	img_sal = driver.Create(ruta_sal, x_size, y_size, nro_bandas, tipo_dato)
	img_sal.SetGeoTransform(georef)
	img_sal.SetProjection(projref)
	
	layindex = 0
	for rt in rutas_en:
		layindex = layindex + 1
		
		datos = array_de_archivo(rt, 1)
		
		layer_sal = img_sal.GetRasterBand(layindex)	
		layer_sal.WriteArray(datos,0,0)
	
	img_sal = None
	del img_sal

## Expresion regular para machear los tif (funcion agregada documentar)
def filtroArchivos (regex):
	""" 
	Devuelve un iterable de los archivos del directorio que satisfacen 
	la expresion regular planteada, puede devolver una lista vacia 
	ES CASE SENSITIVE!!!
	
	Argumentos
	------------------------
	regex: Expresion regular que coincide con las extensiones de los archivos, no es case sensitive, no es necesario aca
	
	"""
	return glob.glob(regex)


def setImagenes (lista_imagenes):
	""" 
	Crea un set de imagenes unicas dao un diccionario o una tupla de imagenes de un directorio 
	
	Argumentos
	------------------------------
	lista_imagenes: iterable con todos los noombres de las imagenes del directorio para crear el set
	"""
	nombre_escenas = []
	for imagen in lista_imagenes:
		nombre_escenas.append(imagen.split('_')[0])
	return list(set(nombre_escenas))

def filtrarArchivosImagenes (ruta):
	""" Devuelve los archivos de imagen que terminan en una 
	extension determinada listada en la lista de extensiones 
	dada una ruta al directorio de trabajo 
	
	Argumentos
	---------------------
	ruta: ruta al directorio de trabajo
	"""
	
	extensiones = ['*.TIF', '*.TIFF', '*.tiff', '*.tif']	
	lista_archivos = []
	for ext in extensiones:
		lista_archivos.extend(filtroArchivos(ext))
	return lista_archivos

def procesarEscena (escena):
	""" 
	Procesa una escena dado el nombre que debe tener, se encarga de filtrar las escenas y las bandas correspondientes 
	
	Argumentos
	---------------------
	escena: nombre de la escena a procesar, generalmente viene de la lista de escenas de la funcoin anterior
	"""
		
	destino = os.path.join(ruta_resultados, escena)
	
	regex = ''.join([escena,'_B[',bandas,']????'])
	rutas_bandas = sorted(glob.glob(regex))

	stack_job(destino, rutas_bandas)


if __name__ == '__main__':
	
	ruta_actual = sys.argv[1]
	ruta_resultados = sys.argv[2]
	bandas = sys.argv[3]
	
	##cambia la ejecucion al directorio deseado
	os.chdir(ruta_actual)
	
	lista_archivos = filtrarArchivosImagenes(ruta_actual)
	nombre_escenas = setImagenes(lista_archivos)
	print nombre_escenas
	
	for escena in nombre_escenas:
		procesarEscena(escena)
