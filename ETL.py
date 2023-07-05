#Importamos las librerias
import pandas as pd
import numpy as np
import json
import ast
import re

#cargamos el dataframe
#Creamos el data set, a partir del CSV
df = pd.read_csv('movies_dataset.csv')

df1= pd.read_csv('credits.csv')

# tratamos el dataset movies
#Cambio a numerico el tipo de datos de la columna ID
df['id'] = pd.to_numeric(df['id'], errors='coerce')

#Observo cuales son las columnas sin ID
df[df['id'].isnull()]

#Se eliminarlan la columnas
df = df.dropna(subset=['id'])

#Cambio el tipo de dato de float a int de la columna, para que coincida en ambos df
df['id'] = df['id'].astype(int)

"""Combinamos los dataframe"""
df3= pd.merge(df, df1, on='id', how='inner')

#df3.head()

#df3.shape
#(45572, 26)Posee 45538 filas y 26 columnas 

"""Eliminar las columnas que no se utilizan video,imdb_id,adult,original_title,poster_path y homepage."""
#Se emplea una mascara para eliminar las columnas
columns_drop = ['video', 'imdb_id', 'adult', 'original_title', 'poster_path', 'homepage']
df4 = df3.drop(columns_drop, axis=1)

""" Desanidarlos campos que contienen diccionarios """

class Desanidar:
    
    @staticmethod
    def convertir_a_str(valor):
        '''La función verifica si el valor es una lista o
         un diccionario y lo convierte en una representación de 
         cadena de JSON utilizando json.dumps(). Si el valor no 
         es una lista o un diccionario, se convierte a una 
         cadena normal utilizando str.'''
        if isinstance(valor, (list, dict)):
            return json.dumps(valor)
        return str(valor)
    
    
    @staticmethod
    def extraer_nombres(valor):
        '''La función toma el parámetro "valor" y busca todas
         las coincidencias de texto que sigan un patrón específico 
         utilizando expresiones regulares. El patrón busca las 
         coincidencias de texto en el formato 'name': 'valor', 
         donde "valor" es cualquier texto entre comillas simples. 
         '''
        pattern = r"'name': '([^']*)'"
        coincidencias = re.findall(pattern, valor)
        if len(coincidencias) > 0:
            nombre = coincidencias[0]
            return nombre
        else:
            return None
    
    @staticmethod
    def extraer_director(valor):
        '''Esta funcion toma el parametro valor efine un patrón de expresión regular 
        pattern  busca coincidencias de texto que sigan el formato 'Director', 
        'name': 'valor', extrayendo el nombre del director Utiliza la función 
        re.findall(pattern, valor) de lo contraio devuelve None'''
        pattern = r"'Director', 'name': '([^']*)'"
        coincidencias = re.findall(pattern, valor)
        if len(coincidencias) > 0:
            nombre = coincidencias[0]
            return nombre
        else:
            return None
    
    
    @staticmethod
    def convertir_a_dicc(column):
        '''Toma el parametro llamado column aplica una transformación a cada valor de 
        la columna utilizando el método apply. verificando si el valor x es nulo utiliza
        la  literal_eval lo convertirá de un objeto a un diccionario. '''
        return column.apply(lambda x: ast.literal_eval(x) if pd.notna(x) else np.nan)
    
    
    @staticmethod
    def desanidar_columna(column):
        '''Esta funcion desanida una columna que contiene listas de diccionarios. 
        Cada diccionario dentro de la lista tiene un atributo 'name'. La función extrae 
        los valores de 'name' de cada diccionario dentro de la lista y los concatena en una 
        sola cadena separada por comas. Si un valor en la columna no es una lista, se asigna 
        np.nan como valor nulo en la columna transformada'''
        return column.apply(lambda x: ', '.join([d['name'] for d in x]) if isinstance(x, list) else np.nan)
    
    
    @staticmethod
    def convertir_a_dicc_btc(column):
        '''Esta función convierte los valores de una columna en objetos de diccionario.
        Si un valor en la columna es nulo, se asigna un diccionario vacío {} como valor 
        en la columna transformada. Si un valor no es nulo, se evalúa la cadena de texto 
        como un diccionario y se devuelve el objeto de diccionario correspondiente.'''
        return column.apply(lambda x: {} if pd.isna(x) else ast.literal_eval(x))
    
    @staticmethod
    # Función para desanidar la columna "belongs_to_collection" y obtener solo los nombres de las colecciones
    def desanidar_btc(column):
      return column.apply(lambda x: x['name'] if isinstance(x, dict) and 'name' in x else np.nan)


'''Aplicacion de las fuciones a la data'''

# Convertir los strings de las columnas en diccionarios
df4['belongs_to_collection'] = Desanidar.convertir_a_dicc_btc(df4['belongs_to_collection'])
# Desanidar el campo "belongs_to_collection" y obtener solo los nombres de las colecciones a las que pertenecen
df4['belongs_to_collection'] = Desanidar.desanidar_btc(df4['belongs_to_collection'])

df4['production_companies'] = Desanidar.convertir_a_dicc(df4['production_companies'])
df4['production_companies'] = Desanidar.desanidar_columna(df4['production_companies'])

df4['production_countries'] = Desanidar.convertir_a_dicc(df4['production_countries'])
df4['production_countries'] = Desanidar.desanidar_columna(df4['production_countries'])

df4['spoken_languages'] = df4['spoken_languages'].apply(Desanidar.convertir_a_str).apply(Desanidar.extraer_nombres)

df4['director'] = df4['crew'].apply(Desanidar.convertir_a_str).apply(Desanidar.extraer_director)

df4 = df4.drop('crew', axis=1)

df4['cast'] = Desanidar.convertir_a_dicc(df4['cast'])
df4['cast'] = Desanidar.desanidar_columna(df4['cast'])

df4['genres'] = Desanidar.convertir_a_dicc(df4['genres'])
df4['genres'] = Desanidar.desanidar_columna(df4['genres'])


"""Los valores nulos de los campos revenue, budget deben ser rellenados por el número 0."""

#Cambiamos el tipo de dato de las columnas a int.
df4['budget'] = df4['budget'].astype(float)
df4['revenue'] = df4['revenue'].astype(float)
df4.dtypes

#Opción B: df['budget'] = pd.to_numeric(df['budget'], errors='coerce')

#Rellenamos los nulos con 0
df4['budget'] = df4['budget'].fillna(0)

#Rellenamos los nulos con 0
df4['revenue'] = df4['revenue'].fillna(0)

"""Se  eliminan los valores nulos del campo release_date"""

df4['release_date'].isnull().sum() #Hay 87 registros nulos
df4 = df.dropna(subset=['release_date']) #Eliminamos los registros nulos de la columna 'release_date'


'''Normalizamos el formato de las fechas'''

# Convertir la columna de fechas a tipo datetime
df4['release_date'] = pd.to_datetime(df4['release_date'], errors='coerce')

# Verificar el formato de las fechas y contar los registros que no cumplen con el formato deseado
formato_deseado = '%Y-%m-%d'
registros_incorrectos = df4['release_date'].dt.strftime(formato_deseado) != df4['release_date']

# Contar el número de registros incorrectos
cantidad_registros_incorrectos = registros_incorrectos.sum()

print(cantidad_registros_incorrectos)

#Creamos columna 'release_year' y la rellenamos con los años de 'release_date'
df4['release_year'] = df4['release_date'].dt.year
print(df4['release_year'])

#Creamos columna 'release_month' y la rellenamos con los meses de 'release_date'
df4['release_month'] = df4['release_date'].dt.month
print(df4['release_month'])

#Creamos columna 'release_day' y la rellenamos con los dias de 'release_date'
df4['release_day'] = df4['release_date'].dt.day
print(df4['release_day'])

"""Crear la columna con el retorno de inversión, llamada return con los campos revenue y budget, dividiendo estas dos últimas revenue / budget, cuando no hay datos disponibles para calcularlo, deberá tomar el valor 0."""

# Crear la columna 'return' y calcular el retorno de inversión
df4['return'] = df4['revenue'].div(df4['budget'], fill_value=0)

# Establecer el valor 0 en los casos donde budget sea 0 o haya valores faltantes en revenue o budget
df4.loc[(df4['budget'] == 0) | (df4['revenue'].isnull()) | (df4['budget'].isnull()), 'return'] = 0

#Elimino la columna tagline, xq presenta casi el 50% de registros nulos
columns_delete = ['tagline' ]
df4 = df4.drop(columns_delete, axis=1)

#Relleno la columna runtine con la media de duraciones de todas las peliculas
valor_medio = df4['runtime'].mean()
df4['runtime'] = df4['runtime'].fillna(valor_medio)

#Relleno los nulos de la columna spoken_languages con su valor modal 
valor_modal = df4['spoken_languages'].mode().values[0]
df4['spoken_languages'] = df4['spoken_languages'].fillna(valor_modal)

#Relleno los nulos de la columna original_language con su valor modal 
valor_modal = df4['original_language'].mode().values[0]
df4['original_language'] = df4['original_language'].fillna(valor_modal)

#Relleno los nulos de Overview con 'Sin descripcion'
df4['overview'] = df4['overview'].fillna('Sin descripcion')

#Relleno los nulos de Director con 'Sin director'
df4['director'] = df4['director'].fillna('Sin director')

#Relleno los nulos de Status con 'Sin informacion'
df4['status'] = df4['status'].fillna('Sin informacion')

#Relleno los nulos de belongs_to_collection con 'Sin informacion'
df4['belongs_to_collection'] = df4['belongs_to_collection'].fillna('Sin informacion')

#Pasar a string, los datos object
df4['belongs_to_collection'] = df4['belongs_to_collection'].astype(str)
df4['genres'] = df4['genres'].astype(str)
df4['original_language'] = df4['original_language'].astype(str)
df4['overview'] = df4['overview'].astype(str)
df4['production_companies'] = df4['production_companies'].astype(str)
df4['production_countries'] = df4['production_countries'].astype(str)
df4['spoken_languages'] = df4['spoken_languages'].astype(str)
df4['status'] = df4['status'].astype(str)
df4['title'] = df4['title'].astype(str)
df4['cast'] = df4['cast'].astype(str)
df4['director'] = df4['director'].astype(str)

df4['belongs_to_collection'] = df4['belongs_to_collection'].astype(str)

#Renombro las columnas belongs_to_colection y cast
df4.rename(columns={'belongs_to_collection': 'collection_movie'}, inplace=True)
df4.rename(columns={'cast': 'actors'}, inplace=True)

df4['earns'] = df4['revenue'] - df4['budget']

# Pasar a minúscula los registros de todas las columnas
df4 = df4.applymap(lambda x: x.lower() if isinstance(x, str) else x)

df4 = df4.reset_index(drop=True)

df4.to_csv('movies_final.csv', index=False)

df4['director'].values

df4.info()

df4.head()