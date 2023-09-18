# Código principal que recopila las funciones para usuarios nuevos y antiguos (new y old)
from src.models.new import new_recom
from src.models.old import recom_sg_userid
from flask import Flask, request
import pandas as pd

app = Flask(__name__)

# Ruta para usuario nuevo
@app.route('/get_new_user_recommendation/')
def endpoint_new():
    genero1 = request.args.get('genero1')
    genero2 = request.args.get('genero2')
    genero3 = request.args.get('genero3')

    # Establecer valores predeterminados si no se proporcionan
    if genero1 is None:
        genero1 = 'vacio'

    if genero2 is None:
        genero2 = 'vacio'

    if genero3 is None:
        genero3 = 'vacio'

    recomendaciones = new_recom(genero1, genero2, genero3)

    # Manejar distintos tipos de datos de salida (hay 'str' y 'Dataframes')
    if isinstance(recomendaciones, pd.DataFrame):
        recomendaciones = recomendaciones.to_html()

    return recomendaciones


# Ruta para endpoint_2
@app.route('/get_old_user_recommendation/')
def endpoint_old():
    userid = request.args.get('userid')

    if userid is None:  # mensaje cuando no se ha ingresado usuario
        return 'Ingresar Id de usuario.'

    # Manejo de tipo de variables (la función necesita un float)
    try:
        userid = float(userid)
    except ValueError:
        userid = userid

    recomendaciones = recom_sg_userid(userid)

    # Manejar distintos tipos de datos de salida (hay 'str' y 'Dataframes')
    if isinstance(recomendaciones, pd.DataFrame):
        recomendaciones = recomendaciones.to_html()

    return recomendaciones

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
