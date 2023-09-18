# La idea es crear una lista artificial de películas vistas por cada usuario, imitando datos reales.
# Luego, se compara (para cada usuario) cuántas películas vistas estaban entre las recomendaciones.
# Con esa información se puede hacer un monitoreo de si el sistema de recomendación entrega buenas o
# malas recomendaciones.

import random
import pandas as pd
from src.models.old import recom_sg_userid
import seaborn as sns
import matplotlib.pyplot as plt


#################  Importando datos
movies_raw = pd.read_csv('data/processed/movies_07_h18.csv', sep=',')
inter_raw = pd.read_csv('data/processed/inter_08_h17.csv', sep=',')

#################  Arreglando datos
movies = movies_raw.copy()
movies = movies[['title', 'release_year']]


############################################################################################################
################             Creacion datos artificiales para cada usuario          ########################
############################################################################################################
random.seed(2017)

columnas_df_vistas = ['title', 'release_year', 'user_id']
df_vistas = pd.DataFrame(columns=columnas_df_vistas)

for user_id in inter_raw['userId'].unique():
    #user_id = 1
    #  definir cuantas películas vio (entre 0 y 10, al azar)
    pelis_vistas = random.randint(0, 10)

    # definir cuántas de esas películas son de las recomendadas (0 a 100%, al azar)
    recom_vistas = random.randint(0, pelis_vistas)


    # crear df de películas vistas:
    # llenar con las recomendadas
    recomendaciones_df = recom_sg_userid(user_id)
    indices = list(range(10))
    indices_random = random.sample(indices, recom_vistas)

    columnas_df_vistas_usuario = ['title', 'release_year']
    df_vistas_usuario = pd.DataFrame(columns=columnas_df_vistas_usuario)

    for indice in indices_random:
        df_vistas_usuario = pd.concat([df_vistas_usuario, recomendaciones_df.iloc[[indice]]], ignore_index=True)


    # rellenar con otras al azar del catálogo que no estén en las recomendaciones
    if (pelis_vistas - recom_vistas) > 0:

        indices_random = random.sample(list(range(len(movies_raw))), 20)  # 20 para que pueda iterar si hay películas repetidas con las recomendaciones (que se supone, no vio)

        lista_titulos_recomendaciones = recomendaciones_df.title.tolist()

        for indice in indices_random:  # asegurar que no incluya pelis de las recomendaciones
            #indice = 545
            titulo = movies.iloc[indice].title
            year = movies.iloc[indice].release_year

            if titulo in lista_titulos_recomendaciones:
                for j in range(0, len(recomendaciones_df)):  # recorre el df para asegurar que sea la misma peli y no un alcance de nombres
                    #j = 0
                    if titulo == recomendaciones_df.iloc[j].title and year != recomendaciones_df.iloc[j].release_year:
                        df_vistas_usuario = pd.concat([df_vistas_usuario, movies.iloc[[indice]]], ignore_index=True)
                        break
            else:
                df_vistas_usuario = pd.concat([df_vistas_usuario, movies.iloc[[indice]]], ignore_index=True)

            if len(df_vistas_usuario) == pelis_vistas:
                break

    df_vistas_usuario['user_id'] = user_id
    # crear un db con las películas vistas (artificial)
    df_vistas = pd.concat([df_vistas, df_vistas_usuario], ignore_index=True)

# Guardando DF de lo que vieron los usuarios
df_vistas.to_csv('data/processed/df_vistas_artificial.csv')


############################################################################################################
#############        Uso datos artificiales para medir éxito de las recomendaciones         ################
############################################################################################################

#################  Importando datos
df_vistas = pd.read_csv('data/processed/df_vistas_artificial.csv', sep=',')

# comparar, para cada usuario, la lista de películas vistas con la lista de recomendaciones
lista_users_que_vieron = df_vistas['user_id'].unique()  # algunos usuarios no vieron películas

porc_exito_recom = []
for user_id in lista_users_que_vieron:
    #user_id = 564
    exitos = 0
    recom_df = recom_sg_userid(user_id)
    df_vistas_usuario = df_vistas[df_vistas['user_id'] == user_id]

    for j in range(0, len(df_vistas_usuario)):
        #j = 0
        titulo_visto = df_vistas_usuario['title'].iloc[j]
        year_visto = df_vistas_usuario['release_year'].iloc[j]

        for k in range(0, len(recom_df)):
            #k = 0
            titulo_recom = recom_df['title'].iloc[k]
            year_recom = recom_df['release_year'].iloc[k]

            if titulo_visto == titulo_recom and year_visto == year_recom:
                exitos = exitos + 1
                break

    porc_exito_recom_usuario = round(exitos / len(df_vistas_usuario) * 100, 1)  # saca % de éxito en las recomendaciones
    porc_exito_recom.append(porc_exito_recom_usuario)  # crear un DB con los % de éxito


# usar el DB para hacer un histograma con la tasa de éxito. Con esto se puede monitorear el rendimiento del algoritmo.
sns.histplot(porc_exito_recom, bins=20, kde=True)
plt.xlabel('Valores')
plt.ylabel('Frecuencia')
plt.title('Histograma')
plt.show()

# Exportar el DataFrame a un archivo Excel para usar en Tableau
# Crear un DataFrame de pandas a partir de la lista
df = pd.DataFrame({'Porc_exito': porc_exito_recom})
df.to_excel('reports/exito_recomen_artificial.xlsx', index=False)
