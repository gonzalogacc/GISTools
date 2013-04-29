'''
########################################################################
####### INSTRUCCIONES DE USO ###########################################
########################################################################

1) Descomprimir todas los archivos de imagenes LANDSAT en una carpeta vacia
	Deben quedar en la misma carpeta, todas las bandas descomprimidas -> un archivo de imagen (Ej.: TIFF, img) por cada banda de cada escena LANDSAT
	No importa si algunas imangenes quedan dentro de subcarpetas

2) en bash (linea de comandos Linux), ejecutar la orden:

python ruta_script ruta_imagenes ruta_resultados 'ubicacion primer caracter de nro de banda, cantidad de caracteres para nro de banda' 'banda deseada1, banda deseada2, banda deseada n'

EJEMPLO:
python /media/GUINDOWS_XP/IMAGENES/Landsat/tmp/stackear_landsat_v00.py
/media/GUINDOWS_XP/IMAGENES/Landsat/tmp			# ruta donde se descomprimieron todas las bandas de todas las escenas
/media/GUINDOWS_XP/IMAGENES/Landsat/tmp/STACKS	# ruta donde se ubicaran los stacks resultado
'23,1' 											# el nro de banda se encuentra en el caracter nro 23 del nombre de las imagenes. Ocupa un solo caracter, ej: '1' (si fuera '01', ocupa dos caracteres)
'3,4,5'											# bandas 3, 4 y 5

LO ANTERIOR DEBERIA EJECUTARSE EN UNA MISMA LINEA, ENTONCES:
python /media/GUINDOWS_XP/IMAGENES/Landsat/tmp/stackear_landsat_v00.py /media/GUINDOWS_XP/IMAGENES/Landsat/tmp /media/GUINDOWS_XP/IMAGENES/Landsat/tmp/STACKS '23,1' '3,4,5'


########################################################################
########################################################################
########################################################################
'''

########################################################################
######### 	ENTRADAS		############################################
########################################################################

extensiones = ['.TIF', '.TIFF', '.tiff', 'tif']

########################################################################
########################################################################
########################################################################

import sys
import os
from osgeo import gdal
from osgeo import *
from osgeo.gdalconst import *

pos = [int(sys.argv[3].split(',')[0]),int(sys.argv[3].split(',')[1])]
bandas = sys.argv[4].split(',')
ruta_actual = sys.argv[1]
ruta_resultados = sys.argv[2]


def listar_archivos(ruta):
	"""
	Lista recursivamente los archivos contenidos en ruta

	Argumentos
	-----------------
	ruta: Ruta al directorio donde estan los archivos a listar
	"""
	import os
		
	lista_rutas = []
	for carpeta in os.walk(ruta):
		dire = carpeta[0]
		archivos = carpeta[2]
	
		for arch in archivos:
			a = dire + '/' + arch
			lista_rutas.append(a)
	
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
		
	imagen = gdal.Open(ruta)

	return array_de_dataset(imagen, nro_banda, cuadro)

def array_de_dataset(imagen, nro_banda, cuadro=False):
		
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

def stack_job(ruta_sal, rutas_en, driver_nom='GTiff', tipo_dato=GDT_Float32):
	
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


########################################################################
########################################################################
########################################################################

os.chdir(ruta_actual)

lista_archivos = listar_archivos(ruta_actual)

### CREAR DICCIONARIO CON NOMBRE Y UBICACION DE CADA BANDA LANDSAT:
dic_imagenes = {}
for r in lista_archivos:
	nombreimagen = r.split('/')[-1]
	
	igual = False
	for ex in extensiones:
		if nombreimagen[-len(ex):] == ex:
			igual = True
	
	# SI ES UN ARCHIVO DE IMAGEN, LO AGREGA A LA LISTA
	if igual:
		dic_imagenes[nombreimagen] = r
### ===


#############################
# SUPONE QUE HAY DOS O CLASES DE NOMBRES DE IMAGEN, QUE UNO ES EL DE LAS BANDAS COMUNES (1 a 5, y 7) Y OTRO EL DE LAS DE TEMPERATURA Y PANCROMATICA (6.1, 6.2 y/o 8):
# 	Comunes: LE72280852012361EDC00_B1.TIF 	...	LE72280852012361EDC00_B5.TIF
#	Otras: LE72270852013036EDC00_B6_VCID_1.TIF	... LE72270852013036EDC00_B6_VCID_1.TIF

# SUPONE QUE PARA LAS BANDAS DE INTERES (1 a 5, y 7) EL NOMBRE ES MAS CORTO QUE PARA LAS DEMAS
#	=> SELECCIONA EL TAMANYO DE NOMBRE MAS CHICO:
tamanyo_preferido = 99999999999
for i in dic_imagenes:
	if len(i) < tamanyo_preferido:
		tamanyo_preferido = len(i)

# CREAR LISTA CON EL NOMBRE DE CADA ESCENA, SIN LA PARTE VARIABLE DE NUMERO DE BANDA:
nombre_escenas = []
for i in dic_imagenes:
	if len(i) == tamanyo_preferido:
		nombre_escenas.append(i[:pos[0]] + i[pos[0]+pos[1]:])

nombre_escenas = list(set(nombre_escenas))
nombre_escenas.sort()

################################

# PARA CADA ESCENA, SELECCIOANR LAS BANDAS DESEADAS Y ARMAR EL STACK:
for i in nombre_escenas:
	
	destino = ruta_resultados + '/' + i
	
	rutas_bandas = []
	for b in bandas:
		nombanda = i[:pos[0]] + str(b) + i[pos[0]+pos[1]-1:]
		rutas_bandas.append(dic_imagenes[nombanda])
	
	stack_job(destino, rutas_bandas)


