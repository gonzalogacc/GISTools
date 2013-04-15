##############################################################################################
##
## Importador de imagenes rasters a psql
##
##############################################################################################
## cambios en v3:
##	- cambia el script raster2psql al standard de postgis 2.0 con el correspondiente cambio en las opciones de los flags
##	- se incorporo la capacidad de importar directamente los subdatasets de los hdf
##
##############################################################################################
## Nota: si da error "password not supplied" o parecido, hacer 'export PGPASSWORD=postgres' en la terminal, previo a correr el script
##############################################################################################
## falta que se fije si la tabla exiaste y si existe que aga un append y sino que cree la tabla

import os
import sys
sys.path.append('/home/garciaac/scripts/gonjo_mods/')
import rutas
from rutas import seleccionar_lineas, listar_archivos
import multiprocessing
from osgeo import gdal

#~ #def r2pg(ruta, database, tabla, flags):
def r2pg(args):
	ruta = args[0]
	database = args[1]
	tabla = args[2]
	flags = args[3]
	host = args[4]
	carga_subdataset = args[5]

	def get_subdataset(carga_subdataset):
		hdf = gdal.Open(ruta)
		sdsdict = hdf.GetMetadata('SUBDATASETS')
		sdslist =[sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]
		names=[]
		for l in sdslist:
			names.append(l)
	
		for subd in names:
			if carga_subdataset in subd:
				subdataset = subd

		return subdataset
			
	nomtemp = '/tmp/temp_' + ruta.split('/')[-1] + '.sql'
	
	if carga_subdataset != 'no':
		sen_generar ='raster2pgsql ' +flags +' "'+get_subdataset(carga_subdataset)+'" '+tabla+' -t '+str(bloque)+' -s '+str(srid)+' >'+nomtemp
	else:
		sen_generar ='raster2pgsql ' +flags +' "'+ruta+'" '+tabla+' -t '+str(bloque)+' -s '+str(srid)+' >'+nomtemp
	sen_cargar = 'psql -w -h '+host+' -U postgres -d '+database+' -f '+nomtemp
	sen_borrar = 'rm ' + nomtemp
	
	print sen_generar
	print sen_cargar
	print sen_borrar

	os.system(sen_generar)
	os.system(sen_cargar)
	os.system(sen_borrar)

########################################################################
# ENTRADAS:###
##############

dir_en = '/mnt/lart-nas/lartproc/imagenes/MOD13A2'
tabla = 'mod13a2_ndvi_1km'
bloque = '100x100'
srid = 96842
host = '10.1.1.239'
database = 'VAR_SAT'
#~ carga_subdataset = 'LST_Day_1km'	## PARA HDF, con SUBDATASETS
carga_subdataset = 'no'			## PARA GEOTIFF, sin SUBDATASETS
########################################################################
########################################################################

archivos_procesar = listar_archivos(dir_en)
## Comentar si en la carpeta de origen solo estan las imagenes a cargar
archivos_procesar = seleccionar_lineas(archivos_procesar, sufijos=[['.hdf.NDVI',0]])

#~ #print archivos_procesar

for i in archivos_procesar:
	print i
raw_input('ENTER para procesar los archivos listados')

os.system('export PGPASSWORD=postgres')

# CARGAR EL PRIMER ARCHIVO CREANDO LA TABLA: ver linea del loop mas abajo, corregir
#r2pg([archivos_procesar[0],database,tabla,'-c -F -I', host, carga_subdataset])

raw_input()

# CARGAR LOS DEMAS ARCHIVOS EN PARALELO

argumentos = []
#Descomentar si se cargan los archivos creando una tabla <<-- corregir!!! que busque si la tabla existe y sino la crea
#for ruta in archivos_procesar[1:]:
for ruta in archivos_procesar:
	argumentos.append([ruta, database, tabla, '-a -F', host, carga_subdataset])
##"""
cola = multiprocessing.Pool(processes=3)
results = cola.map_async(func=r2pg, iterable=argumentos)
cola.close()
cola.join()
##"""
##SECUENCIAL:
##results = map(r2pg, argumentos)



