# Código para recomendar películas a usuarios nuevos
# La idea: el usuario nuevo debe ingresar entre 0 y 3 géneros. Se le recomendarán las pelis más
# vistas de cada género. Si no ingresa género, se le recomendarán las 10 pelis más vistas.
# Usaré el género predicho por el LLM, porque es más conciso que los originales del DB.

import pandas as pd
import pickle

################################################### Importar datos
# Importar lista de géneros
with open('data/processed/generos_simples_unicos.pkl', 'rb') as file:
    generos = pickle.load(file)

# Importando los datos
# DF de las top_tep (tt) más vistas por género o vistas en total.
df_tt_vistas = pd.read_csv('data/processed/df_tt_vistas.csv', sep=',')
df_tt_action = pd.read_csv('data/processed/df_tt_action.csv', sep=',')
df_tt_adventure = pd.read_csv('data/processed/df_tt_adventure.csv', sep=',')
df_tt_crime = pd.read_csv('data/processed/df_tt_crime.csv', sep=',')
df_tt_family = pd.read_csv('data/processed/df_tt_family.csv', sep=',')
df_tt_fantasy = pd.read_csv('data/processed/df_tt_fantasy.csv', sep=',')
df_tt_horror = pd.read_csv('data/processed/df_tt_horror.csv', sep=',')
df_tt_mystery = pd.read_csv('data/processed/df_tt_mystery.csv', sep=',')
df_tt_romance = pd.read_csv('data/processed/df_tt_romance.csv', sep=',')
df_tt_scifi = pd.read_csv('data/processed/df_tt_scifi.csv', sep=',')
df_tt_thriller = pd.read_csv('data/processed/df_tt_thriller.csv', sep=',')

# Generación de diccionario de géneros de películas
genero_movies = {
    'fantasy': df_tt_fantasy[['title', 'release_year']],
    'family': df_tt_family[['title', 'release_year']],
    'crime': df_tt_crime[['title', 'release_year']],
    'action': df_tt_action[['title', 'release_year']],
    'romance': df_tt_romance[['title', 'release_year']],
    'scifi': df_tt_scifi[['title', 'release_year']],
    'adventure': df_tt_adventure[['title', 'release_year']],
    'horror': df_tt_horror[['title', 'release_year']],
    'mystery': df_tt_mystery[['title', 'release_year']],
    'thriller': df_tt_thriller[['title', 'release_year']]
}


# Función recomendar si NO escoge género
def new_recom_sin():
    return df_tt_vistas[['title', 'release_year']]

# Función recomendar con UN género
def new_recom_uno(genero):
    return genero_movies[genero]

# Función recomendar con DOS géneros
def new_recom_dos(genero1, genero2):
    df_aux1 = genero_movies[genero1].iloc[0:5]
    df_aux2 = genero_movies[genero2].iloc[0:5]
    return pd.concat([df_aux1, df_aux2], axis=0)

# Función para recomendar con TRES géneros
def new_recom_tres(genero1, genero2, genero3):
    df_aux1 = genero_movies[genero1].iloc[0:4]
    df_aux2 = genero_movies[genero2].iloc[0:3]
    df_aux3 = genero_movies[genero3].iloc[0:3]
    return pd.concat([df_aux1, df_aux2, df_aux3], axis=0)

# Función para recopilar todas las anteriores en una sola
def new_recom(genero1='vacio', genero2='vacio', genero3='vacio'):
    # Verifica que los géneros ingresados estén en el catálogo
    if genero1 != 'vacio' and genero1 not in generos:
        return "Algún género ingresado no existe. Escoger entre 'fantasy', 'family', 'crime', 'action', 'romance', 'scifi', 'adventure', 'horror', 'mystery', 'thriller'."
    if genero2 != 'vacio' and genero2 not in generos:
        return "Algún género ingresado no existe. Escoger entre 'fantasy', 'family', 'crime', 'action', 'romance', 'scifi', 'adventure', 'horror', 'mystery', 'thriller'."
    if genero3 != 'vacio' and genero3 not in generos:
        return "Algún género ingresado no existe. Escoger entre 'fantasy', 'family', 'crime', 'action', 'romance', 'scifi', 'adventure', 'horror', 'mystery', 'thriller'."

    if genero1 == 'vacio':
        df_recom = new_recom_sin()
        return df_recom

    if genero1 != 'vacio' and genero2 == 'vacio':
        df_recom = new_recom_uno(genero1)
        return df_recom

    if genero1 != 'vacio' and genero2 != 'vacio' and genero3 == 'vacio':
        if genero1 == genero2:  # si son iguales, los trata como uno solo
            df_recom = new_recom_uno(genero1)
            return df_recom

        df_recom = new_recom_dos(genero1, genero2)  # cuando son diferentes
        return df_recom

    if genero1 != 'vacio' and genero2 != 'vacio' and genero3 != 'vacio':
        if genero1 == genero2 and genero1 == genero3:  # todos iguales
            df_recom = new_recom_uno(genero1)
            return df_recom

        if genero1 == genero2:  # si son iguales, los trata como uno solo
            df_recom = new_recom_dos(genero1, genero3)
            return df_recom

        if genero1 == genero3:  # si son iguales, los trata como uno solo
            df_recom = new_recom_dos(genero1, genero2)
            return df_recom

        if genero2 == genero3:  # si son iguales, los trata como uno solo
            df_recom = new_recom_dos(genero1, genero2)
            return df_recom

        df_recom = new_recom_tres(genero1, genero2, genero3)
        return df_recom
