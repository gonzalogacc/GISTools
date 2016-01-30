#!/usr/bin/python env

import psycopg2 as pg
import pandas as pd
import sys

def consultarChunk(cursor, tabla_centroides, columna_id, id_min, id_max):
  """ Con la tabla de centroides genera un dataframe de IV filtrado  """
    
  ## Consultar los valoresde IV
  cursor.execute("SELECT v.%s as id, r.fecha, st_value(r.rast, v.the_geom) from rasters.mod13q1_evi as r, %s as v where gid >= %s and gid < %s and st_contains(r.the_geom, v.the_geom);" \
                          %(columna_id, tabla_centroides, id_min, id_max, ))
  evi = cursor.fetchall()
  pd_evi = pd.DataFrame(evi, columns = ['id', 'fecha', 'indice'])

  ## Consultar los valores de Qc
  cursor.execute("SELECT v.%s as id, r.fecha, st_value(r.rast, v.the_geom) from rasters.mod13q1_qa as r, %s as v where gid >= %s and gid < %s and st_contains(r.the_geom, v.the_geom);" \
                          %(columna_id, tabla_centroides, id_min, id_max, ))
  qa = cursor.fetchall()
  pd_qa = pd.DataFrame(qa, columns = ['id', 'fecha', 'qa'])

  pd_join = pd.merge(pd_evi, pd_qa, on = ['id', 'fecha'])
  return pd_join

def filtrarIndice(df_indice):
  """ Se eliminan los valores del dataframe que no complen con el criterio especificado """

  ## Generar un vector de condiciones
  criterion = df_indice['qa'].map(lambda x: not (int(x) & 32768 == 32768 or int(x) & 16384 == 16384 or int(x) & 1024 == 1024 or int(x) & 192 != 64))

  ## aplicar las condiciones al df original
  df_filtrado = df_indice[criterion]
  
  return df_filtrado


if __name__ == '__main__':
  user = ""
  dbname = ""
  password = ""
  database_ip = ""
  conexion = pg.connect('user = %s dbname = %s password = %s host = %s' %(user, dbname, password, database_ip))
  cursor = conexion.cursor()

  inicio = int(sys.argv[2])
  fin = int(sys.argv[3])
  salto = int(sys.argv[4])

  nombre_tabla = sys.argv[1] ##'firmas_noa.centroides_bosques_niv3_19'

  for x in range(inicio, fin, salto):
    print "Consultando los ids del %s al %s" %(x, x+salto)
    resultado = filtrarIndice(consultarChunk(cursor, nombre_tabla, "id", x, x+salto))
    resultado = consultarChunk(cursor, nombre_tabla, "id", x, x+salto)
    resultado.to_csv("archivo_extracccion_firmas_%s_%s_%s.csv" %(nombre_tabla, x, x+salto))
