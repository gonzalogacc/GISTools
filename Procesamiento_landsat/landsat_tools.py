

import sys, os, glob
import re


def filtroRutas (ruta):
	"""
	Devuelve una lista de rutas de imagenes tif filtradas dado un directorio raiz
	
	Argumentos
	---------------------
	rutas: directorio raiz para recolectar las rutas
	"""
	## expresion regular que filtra los archivos terminados en tif
	reg = re.compile('([^\s]+(\.(?i)(TIF|tif))$)')
	
	## recorrelos directorios haciendo las comparaciones
	lista_rutas = []
	for carpeta in os.walk(ruta):
		dirpath = carpeta[0]
		archivos = carpeta[2]
	
		for archivo in archivos:
			if reg.match(archivo):
				lista_rutas.append(os.path.join(dirpath, archivo))
	
	return lista_rutas


def refabricarNombre (archivo_entrada, archivo_salida):
	"""
	Devuelve las posiciones de los elemnetos en la imagen segun la fuente matchenado con las regex
	
	Argumentos
	----------------------------
	nombre_archivo: nombre del archivo del que se quiere identificar la fuente
	"""
	## seria mejor ponerlo de a pares sin importar la fuente asi la exp es la key y el diccionario tiene las posiciones
	expresiones_regulares = {'.*LANDSAT_[12]_MSS_[0-9]{8,}_[0-9]{3,}_[0-9]{3,}_L[1-8]_BAND[1-7].*': {'fecha':[], 'path':[], 'row':[]}, 
							'L[1-7]{1,}[0-9]{6,}_[0-9]{3,}[12][09][0-9]{2,}[01][0-9][0123][0-9]_B[1-7].*': {'fecha':[], 'path':[], 'row':[]}, 
							'L[1-7][0-9][12][0-9]{2,}[0-3][0-9]{2,}_[0-9]{11,}_B[1-6][01].*': {'fecha':[], 'path':[], 'row':[]},} ## diccionario de las expresiones regulares con su respectiva fuente
	
	
	
if __name__ == '__main__':
	imagenes = filtroRutas('/home/lart/Escritorio/imagenes_origenes/')
	
	for imagen in imagenes:
		## LE72270852013084EDC00_B4.TIF
		reg2 = re.compile('LE.*')
		##reg2 = re.compile('.*LE.*')
		
		## Para machear solo me tengo que quedar con la ultima parte de la ruta qe corresponde al nombre del archivo 
		if reg2.match(imagen.split('/')[-1]):
			print imagen
