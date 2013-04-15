########################################################################
##
## Grillador MODIS
##
########################################################################
## Gonzalo Garcia Accinelli
## gonzalogacc@gmail.com
## Jose M. Clavijo
## joseclavijo@gmail.com
########################################################################
"""
EJECUTAR (todo en la misma linea):

python grilla_mas_interseccion_v2.1.py <shape_mascara> <shape_salida> <umbral_completitud> <tamanio_pixel>

/media/docs/josecla/donmario/area_estudio/area_estudio_dissolve.shp		# archivo shape mascara
/media/docs/josecla/donmario/area_estudio/grillas/MOD_1km				# archivo shape de salida
0.75																	# umbral de completud de pixel
926.625433139															# tamanyo de pixel en x e y (x=y)

"""

from osgeo import ogr
import sys

########################################################################
## Info a completar
archivo = sys.argv[1]
destino = sys.argv[2]

## Shared area prop
proporcion_dentro = float(sys.argv[3])

## Pixel size
#dim_x = dim_y = 0.25
#dim_x = dim_y = 926.6563583
dim_x = dim_y = float(sys.argv[4])

########################################################################
## LEFT
x_inicial = 0

## TOP
y_inicial = 0

########################################################################
## Creacion del archivo
driver = ogr.GetDriverByName('ESRI shapefile')

## Crear un datasource y una capa dentro crea los archivos
grilla = driver.CreateDataSource(destino)
lyr_grilla = grilla.CreateLayer('grilla', geom_type = ogr.wkbPolygon)

## Creo al menos un campo en el shape
fld_grilla = ogr.FieldDefn('id', ogr.OFTInteger)
lyr_grilla.CreateField(fld_grilla)
form_feat = lyr_grilla.GetLayerDefn()

##########################################################################
## recorrida de celdas, calculo de puntos y creacion de poligonos
## cada esquina del poligono Cxy
## Cxy=((Xn,Yn),(Xn,Yn+dim),(Xn+dim,Yn),(Xn+dim,Yn+dim))

def lista_poligonos(archivo):
	## Carga el datasource de la grilla
	driver = ogr.GetDriverByName('ESRI shapefile')
	ds = driver.Open(archivo)
	capa = ds.GetLayer()
	feature = capa.GetFeature(0)	
	geom_contorno = feature.GetGeometryRef()
	
	coleccion = []
	while feature:
		coleccion.append(feature)
		feature = capa.GetNextFeature()
	return coleccion

plantilla = lista_poligonos(archivo)


def wkt_celda(x, y):
	
	nx = (x_inicial - x * dim_x)
	ny = (y_inicial - y * dim_y)
	wkt="POLYGON(("+str(nx)+" "+str(ny)+", "+str(nx+dim_x)+" "+str(ny)+", "+str(nx+dim_x)+" "+str(ny+dim_y)+", "+str(nx)+" "+str(ny+dim_y)+", "+str(nx)+" "+str(ny)+"))"

	return wkt

def interseccion(geom_celda, goem_feat, proporcion_dentro):
	if proporcion_dentro == 1:
		if geom_feat.Contains(geom_celda):
			return True
	else:
		area_intersectada = geom_feat.Intersection(geom_celda).GetArea()
		if area_intersectada > proporcion_dentro * dim_x * dim_x:
			return True
	return None

def escribir_celda(lyr_grilla, geom_celda):	
	## Creacion del feature
	feature = ogr.Feature(form_feat)
	feature.SetGeometryDirectly(geom_celda)
	##print 'Adentro'
	lyr_grilla.CreateFeature(feature)

def offsets(feature):
    geometria = feature.GetGeometryRef()

    limites = geometria.GetEnvelope()

    xmin = int((x_inicial - limites[0]) / dim_y) + 1
    xmax = int((x_inicial - limites[1]) / dim_y) + 1
    ymin = int((y_inicial - limites[2]) / dim_y) + 1
    ymax = int((y_inicial - limites[3]) / dim_y) + 1

    return xmin, ymin, xmax, ymax

if __name__ == '__main__':
    cont = 1
    for poligono in plantilla:
	    print 'Procesado poligono %d de %d' %(cont, len(plantilla))
	    geom_feat = poligono.GetGeometryRef()
	    xmin, ymin, xmax, ymax = offsets(poligono)

	    rango_x = range(xmax, xmin)
	    rango_y = range(ymax, ymin)
	
	    for x in rango_x:
		
		    for y in rango_y:
		        wkt_geom = wkt_celda(x,y)
    			geom_celda = ogr.CreateGeometryFromWkt(wkt_geom)
			
	    		if interseccion(geom_celda, geom_feat, proporcion_dentro) == True:
				escribir_celda(lyr_grilla, geom_celda)
            cont += 1

"""
######### PENDIENTES ############
- que se ubique solo en que cuadrante del planeta esta
- implementar opcion de obtener shp de centroides
"""
