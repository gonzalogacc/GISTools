#/bin/bash

#
# Descompresion de subdatasets de MODIS, ndvi, evi y qa
#

for archivo in $(ls | grep MOD)
do
    eval gdal_translate \"HDF4_EOS:EOS_GRID:$archivo:MODIS_Grid_16DAY_250m_500m_VI:250m 16 days NDVI\" ndvi_$archivo
    eval gdal_translate \"HDF4_EOS:EOS_GRID:$archivo:MODIS_Grid_16DAY_250m_500m_VI:250m 16 days EVI\" evi_$archivo
    eval gdal_translate \"HDF4_EOS:EOS_GRID:$archivo:MODIS_Grid_16DAY_250m_500m_VI:250m 16 days VI Quality\" qa_$archivo
done

