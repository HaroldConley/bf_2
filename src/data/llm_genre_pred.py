# Código para implementar un LLM predictor de género
from transformers import pipeline
from transformers import AutoTokenizer
import pandas as pd
import numpy as np


# Carga el LLM para predecir el género de las películas basado en el plot
pipe = pipeline("text-classification", model="zayedupal/movie-genre-prediction_distilbert-base-uncased")

# Carga el tokenizador del modelo
tokenizer = AutoTokenizer.from_pretrained('zayedupal/movie-genre-prediction_distilbert-base-uncased')

def genre_predict(plot):
    # Acortar el plot hasta que su token mida menos de 512
    while len(tokenizer.encode(plot)) > 512:
        largo_plot = len(plot.split())
        plot = ' '.join(plot.split()[:(largo_plot - 25)])

    # Predice el género
    genre = pipe(plot, top_k=3)

    # Prepara la entrega para informar solo géneros relevantes
    labels_seleccionados = []
    suma_scores = 0.0

    for elemento in genre:
        labels_seleccionados.append(elemento['label'])
        suma_scores += elemento['score']

        if suma_scores >= 0.5:
            break

    labels_continuos = ' '.join(labels_seleccionados)

    return labels_continuos


# Cargar el DataFrame desde un archivo CSV
movies = pd.read_csv('data/interim/movies_07_h11.csv')

# Aplica la función 'genre_predict' a la columna 'plot'
movies['genre_predict'] = movies['plot'].apply(genre_predict)

# Guardando DF con columna 'genre_predict'
movies.to_csv('data/processed/movies_07_h18.csv')
