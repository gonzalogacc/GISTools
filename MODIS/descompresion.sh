#/bin/bash

#
# Descompresion de subdatasets de MODIS
#
##HDF4_EOS:EOS_GRID:"MOD13Q1.A2000129.h13v12.005.2006279203505.hdf":MODIS_Grid_16DAY_250m_500m_VI:250m 16 days NDVI

for archivo in $(ls | grep MOD)
do
	eval gdal_translate \"HDF4_EOS:EOS_GRID:$archivo:MODIS_Grid_16DAY_250m_500m_VI:250m 16 days NDVI\" ndvi_$archivo
done

