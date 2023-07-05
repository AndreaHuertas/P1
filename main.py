from fastapi import FastAPI, Response
import pandas as pd

app = FastAPI(title='Movie Recommendation',
              description='Esta app recomienda películas con características similares.',
              version='1.0.1')

df = pd.read_csv('movies_final.csv', encoding='utf8', sep=',')


#Método que permite obtener la cantidad de peliculas por lenguaje
@app.get("/movies_language/{language:str}")
def movies_language(language):
    movie_language = df[df['original_language'].str.contains(language, na=False)]
    cantidad_films = len(movie_language)

    respuesta = {
        'lenguaje': language,
        'cantidad de peliculas': cantidad_films
    }

    return respuesta



#Método que permite obtener la duración de peliculas y año
@app.get("/duration_movies/{movie}")
def duration_movies(movie):
    movie_fill = df[df['title'].str.contains(movie, na=False)]
    duration = movie_fill['runtime'].values[0] if not movie_fill.empty else None
    year = movie_fill['release_year'].values[0] if not movie_fill.empty else None

    respuesta = {
        'pelicula': movie,
        'duracion': duration,
        'Anio': year
    }

    return respuesta




#Método que permite obtener información sobre la franquicia (coleccién) 
@app.get("/collection/{collection}")
def collection(collection):
   collection_films = df[df['collection_movie'].str.contains(collection, na=False)]
   cantidad_films=len(collection_films)
   ganancia_total = collection_films['earns'].sum()
   promedio = collection_films['earns'].mean()

   respuesta = {
      'cantidad_peliculas':[cantidad_films],
      'ganancia_total':[ganancia_total],
      'promedio':[round(promedio,0)]
      }
   return respuesta



#Método que permite obtener la cantidad de peliculas producidas por país
@app.get("/movie_country/{country}")
def movie_country(country):
    country_films = df[df['production_countries'].str.contains(country, na=False)]
    cantidad_films = len(country_films)

    respuesta = {
      'pais':[country],
      'cantidad_peliculas': [cantidad_films]
      }
    return respuesta     



# Método que permite obtener información sobre la productora ingresada       
@app.get("/successful_producers/{producer}")
def successful_producers(producer):
    # Reemplazar valores NaN en la columna 'production_companies' por una cadena vacía
    df['production_companies'] = df['production_companies'].fillna('')

    # Filtrar por la productora y contar las películas
    producer_films = df[df['production_companies'].str.contains(producer, na=False)]
    cantidad_films = len(producer_films)

    # Calcular el retorno total
    total_return = producer_films['return'].sum()

    respuesta = {
        'productora':[producer],
        'retorno': [round(total_return,3)],
        'cantidad_peliculas': [cantidad_films]
    }
    return respuesta



# Método que permite obtener información sobre un director ingresado
@app.get("/director/{director}")
def get_director(director):
    director_films = df[df['director'] == director]
    cantidad_films = len(director_films)
    total_return = director_films['return'].sum()
    presupuesto = director_films['budget'].sum()
    ganancias = director_films['earns'].sum()

    respuesta = {
        'director': [director],
        'titulo': list(director_films['title']),
        'fecha': list(director_films['release_date']),
        'retorno': [round(total_return, 3)],
        'presupuesto': [presupuesto],
        'ganancias': [ganancias]
    }
    return respuesta