#!/bin/bash

########################################################################
##### INSTRUCCIONES DE USO #############################################
########################################################################

# 1) Ubicar en una misma ruta: 
#	- las imagenes a reproyectar
#	- este script
#	(por precaucion, es conveniente excluir de esta ruta cualquier otro archivo de imagen que no se desee reproyectar)
#
# 2) Abrir una terminal bash (ej: terminal de ubuntu), y posicionarse en la ruta anterior (1), ejecutando:
#		cd <ruta>
#
# 3) Ejecutar la siguiente sentencia:
#
#	sh reproyector_gdalwarp.sh <'prefijo_entrada'> <'sufijo_entrada'> <'proj_entrada'> <'proj_salida'> <'prefijo_salida'> <'sufijo_salida'>
#	
#	donde:
#	<'prefijo_entrada'> = cadena de texto comun al principio del nombre de todos los archivos que se desea reproyectar
#							(Ej: 'LE7'; si no corresponde -si no existe un prefijo comun a todos los archivos-, entonces ingresar '')
#	<'sufijo_entrada'> = cadena de texto comun al final del nombre de todos los archivos que se desea reproyectar
#							(Ej: '.TIF'; si no corresponde, ingresar '')
# 	<'proj_entrada'> = definicion de la proyeccion de origen (la proyeccion de la imagen ANTES de reproyectar)
#							(Ej.: '+proj=utm +zone=20 +ellps=WGS84 +datum=WGS84 +units=m +no_defs', 'EPSG:4326')
	#						(ver www.spatialreference.org; ver man gdalwarp en bash -terminal ubuntu-)
# 	<'proj_salida'> = definicion de la proyeccion de destino (la proyeccion de la imagen DESPUES de reproyectar)
#
#	<'prefijo_salida'> = cadena de texto que se agregara al principio del nombre de todos las imagenes reproyectadas
#							(si no se desea agregar ningun prefijo, ingresar '')
#	<'sufijo_salida'> = cadena de texto que se agregara al final del nombre de todas las imagenes reproyectadas
#							(si no se desea agregar ningun sufijo, ingresar '')
#
#	EJEMPLO DE SENTENCIA:
#	sh gdalwarp_serial.bash LE .TIF '+proj=utm +zone=20 +ellps=WGS84 +datum=WGS84 +units=m +no_defs' '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs' warp_ _warp


########################################################################
########################################################################
########################################################################

for ar in `ls $1*$2`
do 
	nomsal=$5$ar$6
	
	echo
	echo $ar '->' $nomsal

	bash -c "gdalwarp -s_srs '$3' -t_srs '$4' -of 'ENVI' $ar $nomsal"

done

############
# DEPURACIONES

#~ partes=$(echo $ar | tr "/" "\n")
#~ echo ${partes[0]}
