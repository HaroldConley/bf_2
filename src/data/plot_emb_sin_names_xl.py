import pandas as pd
from langchain.document_loaders import DataFrameLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings


# Cargar el DataFrame desde un archivo CSV
movies = pd.read_csv('data/interim/movies_07_h11.csv')


# Db para la metadata
movies_db = movies[['movieId', 'title', 'release_year', 'plot_sin_nombres']]

# Creando el 'documento' con metadata
df_loader = DataFrameLoader(movies_db, page_content_column='plot_sin_nombres')
df_document = df_loader.load()

# Definiendo el modelo a usar para generar los embeddings
embedding_function = SentenceTransformerEmbeddings(model_name="sentence-t5-xl")

# Creando la base de datos vectorial
db = FAISS.from_documents(df_document, embedding_function)
# Guardando la base de datos
db.save_local('data/processed/xl_sin_nombres')
