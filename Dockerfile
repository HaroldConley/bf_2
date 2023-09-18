# Use una imagen base de Python 3.10
FROM python:3.10-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /

# Crear carpetas dentro del contenedor
RUN mkdir -p /src/models/
RUN mkdir -p /data/processed/
RUN mkdir -p /data/processed/xl_sin_nombres/

# Copiar los archivos de la aplicación al contenedor
COPY main.py .
COPY src/models/new.py /src/models/
COPY src/models/old.py /src/models/
COPY data/processed/movies_07_h18.csv /data/processed/
COPY data/processed/inter_08_h17.csv /data/processed/
COPY data/processed/generos_simples_unicos.pkl /data/processed/
COPY data/processed/df_tt_vistas.csv /data/processed/
COPY data/processed/df_tt_action.csv /data/processed/
COPY data/processed/df_tt_adventure.csv /data/processed/
COPY data/processed/df_tt_crime.csv /data/processed/
COPY data/processed/df_tt_family.csv /data/processed/
COPY data/processed/df_tt_fantasy.csv /data/processed/
COPY data/processed/df_tt_horror.csv /data/processed/
COPY data/processed/df_tt_mystery.csv /data/processed/
COPY data/processed/df_tt_romance.csv /data/processed/
COPY data/processed/df_tt_scifi.csv /data/processed/
COPY data/processed/df_tt_thriller.csv /data/processed/
COPY data/processed/xl_sin_nombres/index.faiss /data/processed/xl_sin_nombres/

# Instalar las dependencias necesarias
RUN pip install Flask pandas faiss-cpu

# Exponer el puerto en el que se ejecuta la aplicación Flask
EXPOSE 5000

# Comando para ejecutar la aplicación Flask (ajustado para 'main.py')
CMD ["python", "main.py"]

