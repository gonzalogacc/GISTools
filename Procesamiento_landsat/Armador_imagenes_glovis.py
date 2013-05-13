########################################################################
##
## Unzip + Stack imagenes del INPE
##
########################################################################
## VARIABLES DE ENTRADA

# Indicar bandas que se quieren stackear:
bandas_sel = [1,2,3,4,5,7]

#Indicar nombre del archivo con links de descarga
links = 'links.txt'

## tipo de archivo:
##tipo_link = 'multiple'

########################################################################
########################################################################
import os, zipfile, gzip
from osgeo import gdal, gdalconst
from osgeo.gdalconst import *
import numpy as np
import scipy
import tarfile
import shutil

#LANDSAT_5_TM_20050717_227_085_L2_BAND1.tif.zip
#LANDSAT_7_ETMXS_20010918_225_084_L2_BAND2.tif.zip
#L5224085_08520061120_B10.TIF.gz
#p224r085_7dk20010114_z21_61.tif.gz
#LT51660682010137JSA00.tar.gz --> Formato descarga glovis NASA

directorio_base=os.getcwd()
os.chdir(directorio_base)

nombre_cab = ['LANDSAT_5_','LANDSAT_7_','L5','p', 'LT5', 'LT7', 'CBERS_2B_CCD', 'LE7']
nombre_col = ['tif.zip','tif.zip','.TIF.gz','.tif.gz','.tar.gz']	# deben tener el mismo largo, porque la comparacion no determino cantidad de letras a leer

sentencia = 'aria2c -i' + str(links)
#~ os.system(sentencia)

lista_directorios = []
archivos_erroneos = []

## untar
##tfile = tarfile.open(theTarFile)
##tfile.extractall(extractTarPath)

def filtros(archivo):
	
	if archivo[-7:] in nombre_col:
		if (archivo[:10] in nombre_cab) or (archivo[:3] in nombre_cab) or (archivo[0] in nombre_cab) or (archivo[:12] in nombre_cab):

			return True

def enumerar_imagenes(directorio):
	
	## Lista las imagenes diferentes que estan en el directorio
	dir_anterior = []
	lista_archivos = []
	archivos=os.listdir(directorio_base)
	lista_archivos.sort()
	
	for archivo in archivos:
		dir = directorio_base + '/' + archivo[:-7]
		dir_archivo = directorio_base + '/' + archivo
		
		if filtros(archivo) == True:
			lista_archivos.append(dir_archivo)
			
			if dir not in dir_anterior:
				lista_directorios.append(dir)
				
				## Creacion de la imagen de salida con los datos recopilados arriba
				try:
					os.mkdir(dir)
				except:
					pass
				##shutil.move(dir_archivo, dir)
				shutil.copy(dir_archivo, dir)
				
			dir_anterior = dir
	
	return lista_directorios

						
def descomprimir_archivos(directorio):
	## Bloque para imagenes que vienen en muchos archivos
	##for direct in directorio:
	os.chdir(directorio)
		
	for archivo in os.listdir(os.getcwd()):
			
		#Para L5 y l7, tanto en marylando como en INPE, es valida esta comparacion.
		#Al agregar otras fuentes de imagenes, REVISAR
		
		print 'Descomprimiendo:', archivo
		print archivo
		
		## sacar .gz
		arzip = gzip.open(archivo, mode='r')
		contenido = arzip.read()
		arzip.close()
								
		ar_descomp = open(archivo[:-3], 'w')
		ar_descomp.write(contenido)
		ar_descomp.close()

		## sacar .tar
		tfile = tarfile.open(archivo[:-3])
		tfile.extractall(os.getcwd())



def armado_imagen(directorio, bandas_sel):
	
	os.chdir(directorio)
	
	lista_archivos=os.listdir(directorio)
	lista_img=[]
	bandas_a_escribir = []

	for archivo in lista_archivos:
		if archivo[-4:]=='.tif' or archivo[-4:]=='.TIF':
			lista_img.append(archivo)
			
			print archivo[-7:]
			for caracter in archivo[-6:-5]:
				try:
					## si en los ultimos 6 caracteres del acrhivo hay un numero entre 1 y 9 asumo que es el caracter que indica el nro de banda
					int(caracter)
					if int(caracter) > 0 and int(caracter) < 9:
						if int(caracter) in bandas_sel:
							bandas_a_escribir.append(archivo)
				except:
					pass
	
	print bandas_a_escribir
	## esrcribe las bandas de mayor a menor
	lista_img.sort()
	bandas_a_escribir.sort()
	
	nombre_stack_cola = ''
	
	## revisar que hace esto que escribe muchos 1 en el nombre de salida
	for caracter in bandas_a_escribir:
		nombre_stack_cola = nombre_stack_cola + caracter
	
	nombre_stack_cola = nombre_stack_cola + '.tif'	
	nombre_stack_cab = lista_img[0][:-8]
	
	nombre_stack = 'Stack_'+nombre_stack_cab + '_' + nombre_stack_cola
	
	print
	print 'Generando stack:', lista_img
	print
	
	##imagen_en1 = gdal.Open(lista_img[0])
	imagen_en1 = gdal.Open(bandas_a_escribir[0])
	driver = imagen_en1.GetDriver()
	pixel_x = imagen_en1.RasterXSize
	pixel_y = imagen_en1.RasterYSize
	nrobandas_salida=len(bandas_a_escribir)
	georref = imagen_en1.GetGeoTransform()
	projec = imagen_en1.GetProjectionRef()

	img_salida=driver.Create(nombre_stack, pixel_x, pixel_y, nrobandas_salida, GDT_Byte)
	img_salida.SetGeoTransform(georref)
	img_salida.SetProjection(projec)
	
	########################################################################
	
	cont = 1
	for banda in bandas_a_escribir:

		print 'Escribiendo:', banda

		imagen_temp=gdal.Open(banda)
		banda_temp=imagen_temp.GetRasterBand(1)
		datos=banda_temp.ReadAsArray(0,0,pixel_x,pixel_y)

		img_salida.GetRasterBand(cont).WriteArray(datos)
		cont = cont + 1
	
	########################################################################
	

directorios = enumerar_imagenes(directorio_base)

for direct in directorios:
	print direct
	descomprimir_archivos(direct)

	armado_imagen(direct, bandas_sel)
