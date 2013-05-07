#!/bin/bash

########################################################################
##### INSTRUCCIONES DE USO #############################################
########################################################################

# 1) Ubicar en una misma ruta todas las imagenes a reproyectar
#	(por precaucion, es conveniente excluir de esta ruta cualquier otro archivo de imagen que no se desee reproyectar)
#
# 2) En una terminal bash (Ej., terminal de ubuntu), ejecutar la siguiente sentencia:
#
#	sh reproyector_gdalwarp.sh <'ruta'> <'prefijo_entrada'> <'sufijo_entrada'> <'proj_entrada'> <'proj_salida'> <'prefijo_salida'> <'sufijo_salida'>
#	
#	donde:
#	<'ruta'> = ruta donde se encuentran las imagenes a reproyectar
#	<'prefijo_entrada'> = cadena de texto comun al principio del nombre de todos los archivos que se desea reproyectar
#							(Ej: 'LE7'; si no corresponde -si no existe un prefijo comun a todos los archivos-, entonces ingresar '')
#	<'sufijo_entrada'> = cadena de texto comun al final del nombre de todos los archivos que se desea reproyectar
#							(Ej: '.TIF'; si no corresponde, ingresar '')
# 	<'proj_entrada'> = definicion de la proyeccion de origen (la proyeccion de la imagen ANTES de reproyectar)
#							(Ej.: '+proj=utm +zone=20 +ellps=WGS84 +datum=WGS84 +units=m +no_defs', 'EPSG:4326')
#							(ver www.spatialreference.org; ver man gdalwarp en bash -terminal ubuntu-)
# 	<'proj_salida'> = definicion de la proyeccion de destino (la proyeccion de la imagen DESPUES de reproyectar)
#
#	<'prefijo_salida'> = cadena de texto que se agregara al principio del nombre de todos las imagenes reproyectadas
#							(si no se desea agregar ningun prefijo, ingresar '')
#	<'sufijo_salida'> = cadena de texto que se agregara al final del nombre de todas las imagenes reproyectadas
#							(si no se desea agregar ningun sufijo, ingresar '')
#
#	EJEMPLO DE SENTENCIA:
# 	reproyector_gdalwarp.sh '/IMAGENES/STACKS_int/' 'LE' '.TIF' 'EPSG:32620' 'EPSG:4326' 'warp_' ''


########################################################################
########################################################################
########################################################################

for ar in `ls $1/$2*$3`
do 
	ar2=$(echo $ar | sed 's/^.*\///')
	nomsal=$1/$6$ar2$7
	
	echo $ar '->' $nomsal
	bash -c "gdalwarp -s_srs '$4' -t_srs '$5' -of 'ENVI' $ar $nomsal"
done
