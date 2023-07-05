#Importamos las librerias
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from PIL import Image
import streamlit as st

#cargamos el dataframe
df = pd.read_csv('movies_final.csv', encoding='latin-1', sep=',', low_memory=False)

#Escogemos las columnas con las que vamos a trabajar
df = df[['title', 'collection_movie', 'original_language', 'genres', 'overview', 'popularity', 'production_companies', 'production_countries', 'release_date', 'actors', 'director']]


# Combinar las características en una sola columna
df['features'] = df.apply(lambda x: ' '.join(x.values.astype(str)), axis=1)


# Crear la matriz TF-IDF
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['features'])


# Creamos el modelo de vecinos más cercanos
knn_model = NearestNeighbors(metric='cosine', algorithm='brute')
# Entrenamos el modelo
knn_model.fit(tfidf_matrix)


def get_recommendations(title, knn_model, data, num_recommendations=5):
    # Obtener el índice de la película que coincide con el título
    idx = df[df['title'] == title].index[0]

    # Encontrar los vecinos más cercanos
    distances, indices = knn_model.kneighbors(tfidf_matrix[idx], n_neighbors=num_recommendations+1)

    # Obtener los índices de las películas más similares (excluyendo la película de consulta)
    movie_indices = indices.flatten()[1:]

    # Devolver las películas recomendadas
    return df['title'].iloc[movie_indices]


#funcion recomendaciones para el usuario
def user_input():
    movie_title = st.text_input('Título de la película')

    if st.button('Obtener recomendaciones'):
        if movie_title:
            recommendations = get_recommendations(movie_title, knn_model, df)

            st.subheader(f'Recomendaciones para "{movie_title}":')
            st.write(recommendations)
        else:
            st.write('Por favor, ingrese el título de una película.')


# Aplicación principal
def main():
    #titulo de la aplicacion
    st.title('Movie Recommendation 🎬 🍿')
    image = Image.open('Image/pel.PNG')
    st.image(image, width=700)
    # Llamar a la función user_input()
    user_input()

# Ejecutar la aplicación principal
if __name__ == '__main__':
    main()


