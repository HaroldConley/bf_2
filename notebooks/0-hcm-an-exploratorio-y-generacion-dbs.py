# Código para hacer análisis exploratorio de los datos y transformaciones.-

import seaborn as sns
import matplotlib.pyplot as plt
import spacy
import pickle
from transformers import pipeline
from transformers import AutoTokenizer
import pandas as pd
import numpy as np


# Deshabilitando alertas
import warnings
warnings.filterwarnings("ignore")

# Para ver todas las columnas de DF
#pd.set_option('display.max_columns', None)

# Importando los datos
movies_raw = pd.read_csv('data/raw/movies.csv', sep=',')
inter_raw = pd.read_csv('data/raw/interactions.csv', sep=',')

# Cambio de nombre de columnas a nombres "manejables"
movies_raw.columns = ['unnamed', 'release_year', 'title', 'origin', 'director', 'cast', 'genre', 'wiki_page', 'plot',
                      'movieId', 'title_2', 'genres']

inter_raw.columns = ['unnamed', 'userId', 'movieId', 'timestamp']

# Transformaciones
inter_raw.timestamp = pd.to_datetime(inter_raw.timestamp, unit='s')  # Deja la columna como fecha

inter_raw = inter_raw[['userId', 'movieId', 'timestamp']]
# Guardando DF modificado
inter_raw.to_csv('inter_08_h11.csv')

inter = pd.read_csv('data/interim/inter_08_h11.csv', sep=',')

# Manejando DF inter
inter['timestamp'] = pd.to_datetime(inter['timestamp'])

# Ordenando inter en base al timestamp y al usuario
# Crear un DataFrame vacío con las columnas a necesitar
cols_df_inter_sort = ['userId', 'movieId', 'timestamp', 'tiempo_viendo']
df_inter_sort = pd.DataFrame(columns=cols_df_inter_sort)

for user_id in inter.userId.unique():
    tiempo_viendo = [31]  # No se puede obtener este dato, así que se asume un valor y que se vio la película
    df_aux = inter[inter['userId'] == user_id][['userId', 'movieId', 'timestamp']].sort_values(by='timestamp', ascending=False)

    for i in range(1, len(df_aux)):
        delta_t = (df_aux.timestamp.iloc[i-1] - df_aux.timestamp.iloc[i]).total_seconds() / 60
        tiempo_viendo.append(delta_t)

    df_aux['tiempo_viendo'] = tiempo_viendo
    df_inter_sort = pd.concat([df_inter_sort, df_aux], ignore_index=True)

# Identificando si el usuario vio o no la película. Se considera vista si estuvo más de 30 minutos
# y menos de 4 horas viéndola
vista = []

for tiempo in df_inter_sort.tiempo_viendo:
    if tiempo > 30 and tiempo < 241:
        vista.append(1)  # 1: movie vista
    else:
        vista.append(0)  # 0: movie NO vista

df_inter_sort['vista'] = vista

# Guardando DF modificado
df_inter_sort.to_csv('data/processed/inter_08_h17.csv')


###############################################################################################################
#######                                        Explorando                                            ##########
#######         ¿Cuántos 'origin' diferentes hay y cuántos datos tiene cada uno?          #####################
###############################################################################################################
print(movies_raw.origin.value_counts())

# Los de 'origin' de NO habla inglesa, ¿tienen 'plot' en inglés?
# (Revisé a mano pq eran pocos. Si fueran más, hay que aplicar algún detector de lenguaje o LLM)
# Configura pandas para mostrar todas las filas
pd.set_option('display.max_rows', None)
print(movies_raw[~movies_raw['origin'].isin(['American', 'British', 'Canadian', 'Australian'])][['title', 'plot']])
# Todos en inglés


# ¿Cuántas palabras tienen los plots? ##################################################################
# Calcular la cantidad de palabras en cada texto y agregarlo como una nueva columna 'CantidadPalabras'
movies_raw['CantidadPalabras'] = movies_raw['plot'].apply(lambda x: len(x.split()))

# Configurar el estilo de Seaborn (opcional)
sns.set(style="whitegrid")

# Crear un histograma utilizando Seaborn
plt.figure(figsize=(8, 5))
sns.histplot(movies_raw['CantidadPalabras'], bins=50, color='skyblue')
plt.xlabel('Cantidad de Palabras')
plt.ylabel('Frecuencia')
plt.title('Histograma de la Cantidad de Palabras en los Textos')

# Mostrar el histograma
plt.show()

###############################################################################################################
#################              ¿Cuántos géneros diferentes hay?               #################################
###############################################################################################################
print(movies_raw.genre.value_counts())
print(movies_raw.genres.value_counts())

# Mi intención es medir la calidad de las recomendaciones viendo que el género de las recomendaciones sea similar
# o el mismo de la película 'Input'.

# Como hay muchos 'géneros', transformaré, limpiaré y agruparé para manejar una cantidad razonable de géneros
# Modificaciones varias (pasar a minúsculas, eliminar separadores (comas, barras, slash, etc.)
# A minúsculas
movies_raw['genre'] = movies_raw['genre'].str.lower()
movies_raw['genres'] = movies_raw['genres'].str.lower()

# Eliminar separadores
movies_raw['genre'] = movies_raw['genre'].str.replace('[,/|]', ' ', regex=True)
movies_raw['genres'] = movies_raw['genres'].str.replace('[,/|]', ' ', regex=True)

# Dejar 'unknown' en blanco
movies_raw['genre'] = movies_raw['genre'].str.replace('unknown', '', regex=True)

# Unir columnas 'genre' y 'genres'
movies_raw['genre_unit'] = movies_raw['genre'] + ' ' + movies_raw['genres']

# Cambiando géneros
# Acá tuve que darle jerarquía a diferentes géneros. Esto es subjetivo, y se puede afinar hablando
# con un experto.
lista_generos_simples = [
    'children',
    'thriller',
    'horror',
    'biography',
    'fantasy',
    'animation',
    'musical'
]

lista_generos_simples_2 = [
    'drama',
    'action',
    'romance',
    'series'
]

for genero in lista_generos_simples:
    print(genero)
    print(movies_raw['genre_unit'].str.contains(f'{genero}', case=False).any())

# Géneros compuestos (¿existen?): Sí.
print(movies_raw['genre_unit'].str.contains('comedy', case=False).any() and
      movies_raw['genre_unit'].str.contains('drama', case=False).any())

print(movies_raw['genre_unit'].str.contains('comedy', case=False).any() and
      movies_raw['genre_unit'].str.contains('romance', case=False).any())

print(movies_raw['genre_unit'].str.contains('action', case=False).any() and
      movies_raw['genre_unit'].str.contains('drama', case=False).any())

print(movies_raw['genre_unit'].str.contains('action', case=False).any() and
      movies_raw['genre_unit'].str.contains('comedy', case=False).any())

print(movies_raw['genre_unit'].str.contains('comedy', case=False).any() and
      movies_raw['genre_unit'].str.contains('mystery', case=False).any())

# Creo la columna con los nuevos géneros. Al inicio será una copia de la actual columna, pero se irá
# actualizando iterativamente.
movies_raw['genre_new'] = movies_raw['genre_unit'].copy()

# Géneros simples
for i in range(0, len(movies_raw)):
    for genero in lista_generos_simples:
        if genero in movies_raw['genre_new'][i]:
            movies_raw['genre_new'][i] = genero
            break

# Comedy: Sola o Géneros compuestos
lista_comedy = ['romance', 'action', 'mystery', 'drama']
for i in range(0, len(movies_raw)):
    if 'comedy' in movies_raw['genre_new'][i]:
        movies_raw['genre_new'][i] = 'comedy'
        for subgen in lista_comedy:
            if subgen in movies_raw['genre_unit'][i]:
                movies_raw['genre_new'][i] = 'comedy' + ' ' + subgen
                break

# Géneros simples 2
for i in range(0, len(movies_raw)):
    for genero in lista_generos_simples_2:
        if 'comedy' in movies_raw['genre_new'][i]:
            break
        elif genero in movies_raw['genre_new'][i]:
            movies_raw['genre_new'][i] = genero
            break

# western to action
for i in range(0, len(movies_raw)):
    if 'western' in movies_raw['genre_new'][i]:
        movies_raw['genre_new'][i] = 'action'

# documentary
for i in range(0, len(movies_raw)):
    if 'documentary' in movies_raw['genre_new'][i]:
        movies_raw['genre_new'][i] = 'documentary'

# sci-fi
for i in range(0, len(movies_raw)):
    if 'sci-fi' in movies_raw['genre_new'][i]:
        movies_raw['genre_new'][i] = 'sci-fi'

# war to action
for i in range(0, len(movies_raw)):
    if 'war' in movies_raw['genre_new'][i]:
        movies_raw['genre_new'][i] = 'action'

lista_final = ['children', 'comedy action', 'horror', 'comedy', 'drama',
               'thriller', 'comedy drama', 'comedy romance', 'romance', 'musical',
               'action', 'fantasy', 'biography', 'comedy mystery', 'documentary',
               'sci-fi', 'animation']

# seccion 'other'
for i in range(0, len(movies_raw)):
    for otro in lista_final:
        if otro in movies_raw['genre_new'][i]:
            otro_flag = 0
            break
        else:
            otro_flag = 1

    if otro_flag == 1:
        movies_raw['genre_new'][i] = 'other'

# Chequeo
movies_raw[['genre_unit', 'genre_new']]
movies_raw['genre_new'].value_counts()
movies_raw['genre_new'].unique()


# guardando datos relevantes
movies_raw.to_csv('data/interim/movies_06_h14.csv')


###############################################################################################################
####              Eliminación de entidades 'PERSON' (nombres de personas) de los plots               ##########
####                para enfocar la similitud de plot en la trama y no en nombres.                   ##########
###############################################################################################################
# Eliminación de nombres de 'plot'
# Extracción de nombres
# Cargar el modelo en_core_web_trf
nlp = spacy.load("en_core_web_trf")

# Función para eliminar nombres de personas
def eliminar_nombres(texto):
    doc = nlp(texto)
    palabras_sin_nombres = [token.text for token in doc if token.ent_type_ != "PERSON"]
    return " ".join(palabras_sin_nombres)

# Aplicar la función a la columna "plot"
movies_raw['plot_sin_nombres'] = movies_raw['plot'].apply(eliminar_nombres)

# Guardando DF con columna 'plot_sin_nombres'
movies_raw.to_csv('data/interim/movies_07_h11.csv')


################################################################################################
####                Los géneros de la base de datos original son poco concisos           #######
####         así que se utiliza un transformer entrenado para predecir el género        #######
####                                    en base al plot.                                 #######
################################################################################################
# Código para implementar un LLM predictor de género

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


#####################################################################################
####                Listas de géneros existentes en 'genre_predict'           #######
#####################################################################################
# Importando db
movies = pd.read_csv('data/processed/movies_07_h18.csv', sep=',')

# Crear una lista de géneros simples únicos
generos_simples_unicos = []

# Iterar a través de los géneros compuestos
for genero_compuesto in movies.genre_predict.unique():
    # Dividir el género compuesto en sus partes simples
    partes_simples = genero_compuesto.split()

    # Iterar a través de las partes simples
    for parte_simple in partes_simples:
        # Verificar si la parte simple no está en la lista de géneros simples únicos
        if parte_simple not in generos_simples_unicos:
            # Agregar la parte simple a la lista de géneros simples únicos
            generos_simples_unicos.append(parte_simple)

# Guardar la variable generos_simples_unicos en un archivo
with open('data/processed/generos_simples_unicos.pkl', 'wb') as file:
    pickle.dump(generos_simples_unicos, file)


#####################################################################################
####                         Lista pelis más vistas                           #######
#####################################################################################
# Importar datos
inter = pd.read_csv('data/processed/inter_08_h17.csv', sep=',')
movies = pd.read_csv('data/processed/movies_07_h18.csv', sep=',')

# Importar lista de géneros
with open('data/processed/generos_simples_unicos.pkl', 'rb') as file:
    generos = pickle.load(file)


# pelis vistas
pelis_vistas = inter[inter['vista'] == 1].movieId


############ DF 10 pelis más vistas
top_ten_vistas = pelis_vistas.value_counts()[0:10].index.tolist()

cols_df_tt_vistas = ['title', 'release_year']
df_tt_vistas = pd.DataFrame(columns=cols_df_tt_vistas)

for peli_id in top_ten_vistas:
    fila_df_tt_vistas = movies[movies['movieId'] == peli_id][['title', 'release_year']]
    df_tt_vistas = pd.concat([df_tt_vistas, fila_df_tt_vistas], axis=0)

# Guardando DF
df_tt_vistas.to_csv('df_tt_vistas.csv')


############ DF 10 más vistas (un DF por 'genre_predict')
# ranking más vistas (más repetidas)
ranking_vistas = pelis_vistas.value_counts().index.tolist()

# loop para generar un DF con las 10 pelis más vistas de cada género
for genero in generos:
    print(genero)
    cols_df_tt = ['title', 'release_year']
    df_tt = pd.DataFrame(columns=cols_df_tt)

    contador = 0

    # Primero intento con películas con el género 'puro', no compuesto (por ej: no 'action' + 'crime'; solo 'action')
    for peli_id in ranking_vistas:
        peli_genero = movies[movies['movieId'] == peli_id]['genre_predict'].iloc[0].split()

        # revisa si la peli tiene el género buscado y si solo tiene un género puro
        if genero in peli_genero and len(peli_genero) == 1:
            fila_df_tt = movies[movies['movieId'] == peli_id][['title', 'release_year']]
            df_tt = pd.concat([df_tt, fila_df_tt], axis=0)
            contador = contador + 1

        if contador == 10:
            # Guardando DF
            df_tt.to_csv(f'df_tt_{genero}.csv')
            break

    # Si no se alcanzan 10 películas del género puro, continúo con mezcla de DOS géneros
    if contador < 10:
        for peli_id in ranking_vistas:
            peli_genero = movies[movies['movieId'] == peli_id]['genre_predict'].iloc[0].split()
            peli_genero_primario = movies[movies['movieId'] == peli_id]['genre_predict'].iloc[0].split()[0]

            # revisa si la peli tiene el género buscado y si solo tiene un género puro
            if genero in peli_genero and len(peli_genero) == 2 and peli_genero_primario == genero:
                fila_df_tt = movies[movies['movieId'] == peli_id][['title', 'release_year']]
                df_tt = pd.concat([df_tt, fila_df_tt], axis=0)
                contador = contador + 1

            if contador == 10:
                # Guardando DF
                df_tt.to_csv(f'df_tt_{genero}.csv')
                break
