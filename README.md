# Brain Food
Desafío técnico

## Estructura

* README.md: README con la información del proyecto
* data
  * external: datos de fuentes externas al proyecto
  * interim: datos generados en pasos intermedios
  * processed: datos finales utilizados en los modelos
  * raw: data original del proyecto
* notebooks: códigos de prueba o para generar datos intermedios
* references: textos de referencia y enunciado
* reports: informes generados para el cliente
* requirements.txt: archivo para instalar paquetes necesarios para replicar el trabajo
* src: archivo fuente con los códigos utilizados
  * data: códigos que generan la data usada por el proyecto final
  * models: modelos de recomendación finales
* main.py: código principal que orquesta a los modelos de recomendaciones
* Dockerfile: imagen Docker para levantar el contenedor

```
├───.idea
│   └───inspectionProfiles
├───data
│   ├───external
│   ├───interim
│   ├───processed
│   │   └───xl_sin_nombres
│   └───raw
├───notebooks
├───references
├───reports
│   └───figures
├───src
│   ├───data
│   ├───models
│   │   └───__pycache__
│   └───__pycache__
```

