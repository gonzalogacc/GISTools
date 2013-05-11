

import sys, os, glob
import re
import string
import shutil

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


def refabricarNombre (ruta):
	"""
	Devuelve las posiciones de los elemnetos en la imagen segun la fuente matchenado con las regex
	
	Argumentos
	----------------------------
	nombre_archivo: nombre del archivo del que se quiere identificar la fuente
	"""
	## seria mejor ponerlo de a pares sin importar la fuente asi la exp es la key y el diccionario tiene las posiciones
	expresiones_regulares = {'.*LANDSAT_[12]_MSS_[0-9]{8,}_[0-9]{3,}_[0-9]{3,}_L[1-8]_BAND[1-7].*': {'anio':(14, 18), 'mes':(18, 20), 'dia':(20, 22), 'path':(23, 26), 'row':(27, 30), 'banda': (38,39)}, 
						'L[1-7]{1,}[0-9]{6,}_[0-9]{3,}[12][09][0-9]{2,}[01][0-9][0123][0-9]_B[1-7].*': {'anio':(13, 17), 'mes':(17, 19), 'dia':(19, 21), 'path':(3, 6), 'row':(6, 9), 'banda': (23, 24)}, 
						'L[1-7][0-9][12][0-9]{2,}[0-3][0-9]{2,}_[0-9]{11,}_B[1-6][01].*': {'anio':(13, 17), 'mes':(17, 19), 'dia':(19, 21), 'path':(3, 6), 'row':(6, 9), 'banda': (23, 24)}} ## diccionario de las expresiones regulares con su respectiva fuente
	
	imagenes = filtroRutas(ruta)
	
	expresiones = expresiones_regulares.keys()
	for exp in expresiones:
		reg2 = re.compile(exp)
		
		for imagen in imagenes:
			ruta_imagen = imagen.split('/')
			im = ruta_imagen[-1]
			
			
			
			if reg2.match(im):
				
				print im
				
				print ruta_imagen[:-2]
				patron = expresiones_regulares[exp]
				shutil.copy(imagen, os.path.join('/documentos/temp/imagenes_origenes', parseName(im, patron)))

def parseName (nombre, patron):
	""" devuelve los componentes del nombre dado una cadena y un patron para parsear"""
	
	nom = 'IMAGEN'
	for item in ['anio', 'mes', 'dia', 'path', 'row', 'banda']:
		algo = nombre[patron[item][0]: patron[item][1]]
		nom = nom +'_'+ algo
	
	return nom
	

	
if __name__ == '__main__':
	
	refabricarNombre('/documentos/temp/imagenes_origenes')
	
	
