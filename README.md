# Brain Food
Desafío técnico

Levantar el contenedor con el siguiente comando:
- docker run -p 5000:5000 nombre_imagen

## Estructura
```
├───data
│   ├───external: datos de fuentes externas al proyecto
│   ├───interim: datos generados en pasos intermedios
│   ├───processed: datos finales utilizados en los modelos
│   │   └───xl_sin_nombres: base de datos vectorial
│   └───raw: data original del proyecto
├───notebooks: códigos de prueba o para generar datos intermedios
├───references: textos de referencia y enunciado
├───reports: informes generados para el cliente
├───src: archivo fuente con los códigos utilizados
│   ├───data: códigos que generan la data usada
│   ├───models: modelos de recomendación finales
├ main.py: código principal que orquesta a los modelos de recomendaciones
├ Dockerfile: imagen Docker para levantar el contenedor
├ README.md: README con la información del proyecto
├ requirements.txt: archivo para instalar paquetes necesarios para replicar el trabajo
```

# Explicación secciones anexas al proyecto principal
## Monitoreo de la efectividad del modelo de recomendación
Se ha optado por evaluar la eficacia del modelo utilizando el siguiente indicador: el porcentaje de recomendaciones que el usuario visualiza en relación con el total de películas que ha visto. Esta métrica se calcula mediante la fórmula: (Número de recomendaciones vistas) / (Número de películas vistas) * 100.

Para ilustrar esta medida, he creado una base de datos artificial, la cual se encuentra en el archivo "exito_recomen_artificial.xlsx" y se genera utilizando el script "monitoreo_artificial.py". Los resultados obtenidos se presentan en forma de un histograma en Tableau. Cabe destacar que esta visualización puede ser configurada para funcionar con datos en tiempo real, permitiendo al cliente observar en tiempo real el porcentaje de películas vistas que son resultado de recomendaciones.
El link del Histograma de Tableau es:

https://public.tableau.com/app/profile/harold.conley/viz/Monitoreo_Recomendaciones/Dashboard1?publish=yes


## Experimentos con distintos modelos
Se llevaron a cabo experimentos utilizando dos variantes de un Large Language Model (LLM) especialmente entrenado para evaluar la similitud de oraciones, concretamente el modelo Sentence-T5, el cual se encuentra disponible en la página https://www.sbert.net/docs/pretrained_models.html. Estas dos variantes fueron denominadas como L y XL del modelo. Durante la evaluación, se consideraron dos escenarios: uno en el que se incluían entidades 'PERSON' (nombres de personas) y otro en el que no se incluían entidades.

La métrica utilizada para evaluar la similitud se basó en la distancia de Jaccard entre los géneros de la película 'Input' y las recomendaciones. En otras palabras, se buscaba determinar cuántos géneros presentes en el 'Input' coincidían con los géneros de las recomendaciones. Sorprendentemente, todos los modelos arrojaron resultados de distancia de géneros similares. Esto se realizó en el código comparar_modelos.py.

Además de la métrica automatizada, se realizó un análisis manual, que involucró la realización de pruebas y una evaluación subjetiva de si las recomendaciones guardaban coherencia con el tema o género de la película 'Input'. En este proceso, se observó que los modelos que utilizaban los plots de películas sin entidades 'PERSON' funcionaban significativamente mejor. Los modelos que incluían entidades tendían a recomendar películas en las que la única similitud era el nombre del personaje. Las recomendaciones entregadas por cada modelo se resumen en las bases de datos "exper_df_[MODELO].csv".

Dada esta observación, se tomó la decisión de emplear el modelo XL sin entidades para el proceso de recomendación, ya que demostró un rendimiento superior al brindar recomendaciones más coherentes y relevantes en función del contenido temático de la película 'Input'.


## Películas a renovar
Se creó una lista de películas con el propósito de determinar cuáles deben ser renovadas y en qué orden de prioridad. Esta lista, denominada "Lista_peliculas_a_renovar.xlsx", se ha organizado de manera que las películas más recomendadas para renovar ocupan las primeras posiciones, mientras que las menos recomendadas están al final.

Para tomar decisiones respaldadas sobre qué películas renovar y en qué secuencia, se han aplicado dos criterios principales. El primero de ellos es el Retorno sobre la Inversión (ROI), que se calcula como las ganancias de taquilla divididas por los gastos de producción y multiplicado por 100. La elección de este criterio se basa en la idea de que el ROI puede estar relacionado con la cantidad de personas que verán la película en la plataforma y el valor de los derechos de transmisión.

Además del ROI, se ha considerado la popularidad de las películas como un segundo criterio.

La información necesaria para tomar estas decisiones se ha recopilado a partir de dos bases de datos que contienen información financiera y de popularidad. El proceso de generación de la lista de renovación se ha llevado a cabo mediante el código implementado en el archivo "renovar.py".

Bases de datos:
- https://www.kaggle.com/datasets/utkarshx27/movies-dataset
- https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset
