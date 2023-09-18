# Código para generar las recomendaciones a los clientes antiguos (old)
import pandas as pd
import faiss


# Importando los datos
movies = pd.read_csv('data/processed/movies_07_h18.csv', sep=',')
inter = pd.read_csv('data/processed/inter_08_h17.csv', sep=',')

# Datos necesarios
lista_usuarios = inter.userId.unique().tolist()


# Cargando el indexado del vectorstore guardado
index = faiss.read_index("data/processed/xl_sin_nombres/index.faiss")


#########################################################################################
##########################          Recomendaciones           ###########################
#########################################################################################

# Función para obtener 10 recomendaciones dada una movie_id (entrega lista con movie_id y lista con puntaje similitud)
def recom_movies(movie_id):
    # Encontrar el índice de la película 'input'
    index_input = int(movies[movies['movieId'] == movie_id].index[0])

    # Recupera el vector correspondiente
    vector = index.reconstruct(index_input)

    # Convierte el vector individual en una matriz de consulta
    query_matrix = vector.reshape(1, -1)

    # Busca las distancias y los índices de los vectores vecinos (similares)
    distancias, indices_similares = index.search(query_matrix, 11)

    # Se crea la lista con las ids de las 10 películas con plots más similares a la película 'input'
    top_ten_movie_ids = []  # lista vacía para llenar

    for ind in indices_similares[0]:
        top_ten_movie_ids.append(movies.iloc[ind][['movieId']]['movieId'])

    top_ten_movie_ids.pop(0)  # elimina el primer id (que es el de la película 'input')

    return top_ten_movie_ids


# Función para obtener un DF de recomendaciones basadas en una lista de Ids de películas
def df_recomen(lista_movies):
    # Crear un DataFrame vacío con las columnas a necesitar
    cols_df_recomend = ['movie_id']
    df_recomend = pd.DataFrame(columns=cols_df_recomend)

    # Listas vacías para ir llenando
    col_movieid = []

    for movie_id in lista_movies:
        top_ten_movie_ids = recom_movies(movie_id)

        # Guardando los datos
        col_movieid.extend(top_ten_movie_ids)

    # Creando el DF con la información de las distintas recomendaciones
    df_recomend['movie_id'] = col_movieid

    return df_recomend


# Función que remueve las películas que el usuario ya vio de un DF de recomendaciones
def remover_vistas(user_id, df_recom):
    lista_vistas = inter[inter['vista'] == 1]
    vistas_usuario = lista_vistas[lista_vistas['userId'] == user_id].movieId.to_list()
    movies_no_vistas = df_recom[~df_recom['movie_id'].isin(vistas_usuario)]

    return movies_no_vistas


# Función que entrega recomendaciones para un userId, basada en las últimas películas vistas
def recom_sg_userid(user_id):
    # verifica la existencia del usuario
    if user_id not in lista_usuarios:
        return "El usuario ingresado no existe."

    # genera una lista con las últimas películas vistas por el usuario (máx 10)
    lista_vistas = inter[inter['userId'] == user_id]
    lista_vistas = lista_vistas[lista_vistas['vista'] == 1].movieId.to_list()

    if len(lista_vistas) > 10:
        lista_vistas = lista_vistas[0:10]


    # usa la función df_recom para obtener las películas recomendadas y sus datos
    df_pelis_recom = df_recomen(lista_vistas)


    # usa la función remover_vistas para sacar de las recomendaciones las pelis que ya vio
    df_pelis_recom_no_vistas = remover_vistas(user_id, df_pelis_recom)

    # busca las pelis más repetidas en las recomendaciones (máximo 10)
    recomendadas = []  # por defecto está vacía
    if df_pelis_recom_no_vistas['movie_id'].duplicated().any():  # entra si hay repetidas
        repetidas = df_pelis_recom_no_vistas.movie_id.value_counts()
        repetidas = repetidas[repetidas > 1].index.tolist()  # lista de pelis repetidas, ordenadas por repetición
        recomendadas = repetidas

    # si no alcanza a recomendar 10, llena la recomendación con los mejores puntajes de similitud
    # que no estén entre las ya recomendadas
    if len(recomendadas) < 10:
        # eliminar las pelis ya usadas en 'repetidas'
        df_recomen_sin_repetidas = df_pelis_recom_no_vistas[~df_pelis_recom_no_vistas['movie_id'].isin(recomendadas)]

        cuantas_agregar = 10 - len(recomendadas)
        pelis_a_agregar = df_recomen_sin_repetidas.movie_id.tolist()[0:cuantas_agregar]
        recomendadas.extend(pelis_a_agregar)

    # entrega los nombres de las 10 pelis recomendadas, en orden
    cols_df_recomendaciones = ['title', 'release_year']
    df_recomendaciones = pd.DataFrame(columns=cols_df_recomendaciones)

    for peli_id in recomendadas:
        fila_df_recomendaciones = movies[movies['movieId'] == peli_id][['title', 'release_year']]
        df_recomendaciones = pd.concat([df_recomendaciones, fila_df_recomendaciones], axis=0)

    return df_recomendaciones

