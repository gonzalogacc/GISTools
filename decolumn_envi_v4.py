
########################################################################
##
## Decolumn version 4
##
########################################################################
## 

import csv, os, sys

def levantarArchivo (archivo_entrada, archivo_salida):
	"""
	Dado un csv de una extraccion de ENVI lo devuelve como una lista y su encabezado aparte
	
	argumentos:
	-----------
	ruta_archivo: ruta al archivo a procesar
	
	devuelve:
	lista: lista de listas con los valores por linea
	encabezado: 
	"""
	csv_entrada=csv.reader(open(archivo_entrada,'rb'), delimiter='|', dialect='excel')
	csv_salida=csv.writer(open(archivo_salida, 'wb'))
	
	lista = []
	encabezado = []
	
	for linea in csv_entrada:

		if linea[0][0] == ';':
			
			encabezado.append(linea[0][1:])
			
		else:
			lista.append(linea[0])
	
	## limpiar el encabezado de los espacios variables
	encabezado_limpio = [a for a in encabezado[-1].split(' ') if a != '']
	
	## limpiar el cuerpo de la tabla de los espacios variables
	matriz_limpia = []
	for fila in lista:
		tmp_list= []
		for a in fila.split(' '):
			if a != '':
				tmp_list.append(a)		
		matriz_limpia.append(tmp_list)
	
	##crear un diccionario con los datos y escribirlos al archivo
	## primero escribe encabezado
	csv_salida.writerow(['ID','x','y','lon','lat','banda', 'value'])
	
	for linea in matriz_limpia:
		
		for n in range(5, len(encabezado_limpio)):

			csv_salida.writerow([linea[0], linea[1], linea[2], linea[3], linea[4], encabezado_limpio[n], linea[n]])
	
	return 0


if __name__ == '__main__':

	## Cambiar cada corrida
	archivo_entrada = sys.argv[1]
	archivo_salida = archivo_entrada[:-4]+'_decolumn.csv'
	
	
	levantarArchivo(archivo_entrada, archivo_salida)
