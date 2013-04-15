########################################################################
##
## Ejecucion de la funcion r.what en paralelo
##
########################################################################
## Gonzalo Garcia Accinelli, Jose M. Clavijo
## garciaac@agro.uba.ar, joseclavijo@gmail.com


import grass.script.core as grass
import time, csv
import multiprocessing 
import os, sys


def consulta_punto(args):
	'''
	Toma una lista de coordenadas con [[lon, lat, idpix], lista]
	Salida: crea un archivo por consulta
	'''
	import grass.script.core as grass
	import os
	
	lon = args[0][0]
	lat = args[0][1]
	id_pixel = args[0][2]
	lista = args[1]
	
	nombre = os.path.join(os.getcwd() + '/salida_' + str(lon) + '_' + str(lat) + '.csv')
	##nombre_archivo = 'salida_' + str(lon) + '_' + str(lat) + '.csv'
	##nombre = os.path.join(ruta_salida, nombre_salida)
	
	archivo_salida = open(nombre, 'w')
	
	coordenadas = str(lon)+","+str(lat)
	print 'procesando coordenadas --> ', coordenadas
	
	dato = grass.parse_command('r.what', flags = 'n', input = lista, east_north = coordenadas)
	
	try:
		zonda = float((dato.items()[1])[0].split('|')[-1])
	except:
		zonda = (dato.items()[1])[0].split('|')[-1]
		
	if isinstance(zonda, float) == True:
		valores = (dato.items()[1])[0].split('|')
		encabezado = (dato.items()[0])[0].split('|')

	elif isinstance(zonda, str) == True:
		valores = (dato.items()[0])[0].split('|')
		encabezado = (dato.items()[1])[0].split('|')
		
	lat = valores[0]
	lon = valores[1]
	
	for i in range(3,len(valores)):
		
		archivo_salida.write(str(lat)+','+str(lon)+','+str(id_pixel)+','+str(valores[i])+','+str(encabezado[i])+'\n')
		
	archivo_salida.close()


def filtro_img(radical):
	lista_img = grass.list_strings('rast')
	lista_sel = []
	for img in lista_img:
	
		if img[:len(radical)] == radical:
			lista_sel.append(img)
	return lista_sel

def get_coordenadas(coordinates_file):
	'''
	formato del archivo de coordenadas:
	Salida de la funcion v.out.ascii aplicada a un shape de centroides.
	sino un archivo de texto separado por '|' con las siguientes columnas en el sistema de coordenadas del proyecto
	lon|lat|id
	'''

	archivo_coordenadas = csv.reader(open(coordinates_file, 'r'), delimiter = '|', quoting = csv.QUOTE_NONNUMERIC)
	coordenadas = []
	for idlatlon in archivo_coordenadas:
		coordenadas.append(idlatlon) 
	
	return coordenadas


def proceso(coordinates_file, radical):
	
	lista_seleccion = filtro_img(radical)
	coordenadas = get_coordenadas(coordinates_file)
	
	args = []
	for par in coordenadas:
		args.append([par, lista_seleccion])
		
	t_inicial = time.time()	
	
	## Bloque para ejecucion en paralelo
	consultas = multiprocessing.Pool(processes = 2)
	resultados = consultas.map_async(func=consulta_punto, iterable=args)
	consultas.close()
	consultas.join()
		
	print 'tiempo', time.time() - t_inicial

		
proceso(sys.argv[1], sys.argv[2])
