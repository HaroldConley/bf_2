# La idea: renovar las películas con mejor retorno (ROI=ganancias/presupuesto) para las productoras.
# Asumo que si la película tuvo un alto retorno para la productora, su relación (reproducciones)/(valor renovar)
# también será favorable.

# Los datos de presupuesto y retorno son de las siguientes base de datos de Kaggle
# https://www.kaggle.com/datasets/utkarshx27/movies-dataset
# https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset

import pandas as pd

# Deshabilitando alertas
import warnings
warnings.filterwarnings("ignore")

#################  Inportando datos
movies_raw = pd.read_csv('data/processed/movies_07_h18.csv', sep=',')
movies_financial_1_raw = pd.read_csv('data/external/movie_dataset.csv', sep=',')
movies_financial_2_raw = pd.read_csv('data/external/movies_metadata.csv', sep=',')


#################  Dejando solo las columnas que necesito
movies_financial_1 = movies_financial_1_raw.copy()
movies_financial_1 = movies_financial_1[['original_title', 'release_date', 'budget', 'revenue', 'popularity']]

movies_financial_2 = movies_financial_2_raw.copy()
movies_financial_2 = movies_financial_2[['original_title', 'release_date', 'budget', 'revenue']]


#################  Transformando datos
# movies_financial_1
release_year = []
for i in range(0, len(movies_financial_1)):
    try:
        year = int(pd.to_datetime(movies_financial_1['release_date'][i]).year)
    except ValueError:
        year = 0

    release_year.append(year)

movies_financial_1['release_year'] = release_year

# movies_financial_2
release_year = []
for i in range(0, len(movies_financial_2)):
    try:
        year = int(pd.to_datetime(movies_financial_2['release_date'][i]).year)
    except ValueError:
        year = 0

    release_year.append(year)

movies_financial_2['release_year'] = release_year

# columna budget de movies_financial_2
movies_financial_2['budget'] = pd.to_numeric(movies_financial_2['budget'], errors='coerce')


# Pasando todos los textos a minúsculas
movies_financial_1['original_title'] = movies_financial_1['original_title'].str.lower()
movies_financial_2['original_title'] = movies_financial_2['original_title'].str.lower()


################# Completando datos de movies_financial_1 con movies_financial_2
for i in range(0, len(movies_financial_1)):
    # budget
    if movies_financial_1.budget.iloc[i] < 7000 or pd.isnull(movies_financial_1.budget.iloc[i]):  # escogí 7000 pq hay budget demasiado bajos (irreales)
        movie_title = movies_financial_1['original_title'][i]
        rel_year = movies_financial_1['release_year'][i]
        rango_rel_year = [rel_year-1, rel_year, rel_year+1]  # Porque algunas movies tienen info inexacta
        df_posibilidades = movies_financial_2[movies_financial_2['original_title'] == movie_title]
        if len(df_posibilidades) > 1:
            for j in range(0, len(df_posibilidades)):
                budget_fin_1 = df_posibilidades['budget'].iloc[j]
                if df_posibilidades['release_year'].iloc[j] in rango_rel_year and budget_fin_1 >= 7000:
                    movies_financial_1.budget.iloc[i] = budget_fin_1
                    break
        elif len(df_posibilidades) == 1 and df_posibilidades['budget'].iloc[0] >= 7000:
            budget_fin_1 = df_posibilidades['budget'].iloc[0]
            movies_financial_1.budget.iloc[i] = budget_fin_1
        elif len(df_posibilidades) == 1:
            movies_financial_1.budget.iloc[i] = 0

    # revenue. Acá no filtré valores pequeños, pq puede ser que alguna película efectivamente recaudara poco.
    if movies_financial_1.revenue.iloc[i] == 0 or pd.isnull(movies_financial_1.revenue.iloc[i]):
        movie_title = movies_financial_1['original_title'][i]
        rel_year = movies_financial_1['release_year'][i]
        rango_rel_year = [rel_year-1, rel_year, rel_year+1]  # Porque algunas movies tienen info inexacta
        df_posibilidades = movies_financial_2[movies_financial_2['original_title'] == movie_title]
        if len(df_posibilidades) > 1:
            for j in range(0, len(df_posibilidades)):
                if df_posibilidades['release_year'].iloc[j] in rango_rel_year:
                    revenue_fin_1 = df_posibilidades['revenue'].iloc[j]
                    movies_financial_1.revenue.iloc[i] = revenue_fin_1
                    break
        elif len(df_posibilidades) == 1:
            revenue_fin_1 = df_posibilidades['revenue'].iloc[0]
            movies_financial_1.revenue.iloc[i] = revenue_fin_1


# Lamentablemente, no hay mucha información complementaria de 'budget' y 'revenue' entre
# ambas DB (tienen casi los mismos datos).
# Sin embargo, la columna 'popularity' de movies_financial_1_raw puede entregar un segundo valor para ordenar
# las preferencias sobre qué películas renovar.
# Por lo tanto, se jerarquizará primero por ROI y luego por popularidad.


################# Obteniendo el ROI (retorno sobre la inversión) de movies_financial_1 (que ya fue
# complementada con info de movies_financial_2)
roi_column = []
for i in range(0, len(movies_financial_1)):
    if movies_financial_1['budget'].iloc[i] != 0:
        roi = movies_financial_1['revenue'].iloc[i] / movies_financial_1['budget'].iloc[i] * 100
        roi_column.append(roi)
    else:
        roi_column.append(0)

movies_financial_1['roi'] = roi_column


#################  Ordenando en base al ROI y luego según puntaje de popularidad (popularity)
mejores_movies_sort = movies_financial_1[['original_title', 'release_year', 'roi', 'popularity']]
mejores_movies_sort = mejores_movies_sort.sort_values(by=['roi', 'popularity'], ascending=[False, False])


#################  Ordenar el catálogo de películas del cliente según el orden de 'renovar_df'
catalogo = movies_raw.copy()
catalogo = catalogo[['title', 'release_year']]

# Loop para crear un DF con las películas que se deben renovar, ordenadas por prioridad
columnas_renovar_df = ['title', 'release_year']
renovar_df = pd.DataFrame(columns=columnas_renovar_df)

for i in range(0, len(mejores_movies_sort)):
    title = mejores_movies_sort['original_title'].iloc[i]
    year = mejores_movies_sort['release_year'].iloc[i]
    rango_year = [year-1, year, year+1]
    df_coincidencias = catalogo[catalogo['title'] == title]

    if len(df_coincidencias) > 1:
        for j in range(0, len(df_coincidencias)):
            if df_coincidencias['release_year'].iloc[j] in rango_year:
                renovar_df = pd.concat([renovar_df, df_coincidencias], ignore_index=True)
                break
    elif len(df_coincidencias) == 1:
        if df_coincidencias['release_year'].iloc[0] in rango_year:
            renovar_df = pd.concat([renovar_df, df_coincidencias], ignore_index=True)


# Guardando DF
renovar_df.to_csv('data/processed/renovar_df.csv')
