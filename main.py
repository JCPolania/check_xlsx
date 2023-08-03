from flask import Flask, render_template, request, flash, redirect, url_for
import pandas as pd
from database import read_ivr_table
from dotenv import load_dotenv
import os
import mysql.connector
from flask_login import LoginManager, UserMixin, login_user, login_required
from flask_caching import Cache
from functools import lru_cache

config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 2419200

}

load_dotenv()
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/"
app.secret_key = os.getenv('C_SECRECT')


cache = Cache(app, config={
    "CACHE_TYPE": "simple",  
    "CACHE_DEFAULT_TIMEOUT": 60 * 60 * 24 * 28  
})

cache = Cache(app, config=config)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


def validar_formato_fecha(fecha):
    try:
        if fecha != pd.to_datetime(fecha, format="%Y-%m-%d %H:%M:%S").strftime(
            "%Y-%m-%d %H:%M:%S"
        ):
            return False
        else:
            return True
    except ValueError:
        return False


def validar_identificacion(id):
    return len(str(id)) <= 21


# def validar_resultado_maquina(resultado):
#     valid_results = [
#         "ABANDON",
#         "NO-ANSWER",
#         "FAILED",
#         "NORMAL_CLEARING",
#         "CALL_REJECTED",
#         "ANSWER-MACHINE-MSG",
#     ]
#     return resultado in valid_results

def validar_tipo_call(call):
    valid_call = [
        "REG",
        "out_pre"
    ]
    return call in valid_call


def validar_telefono(telefono):
    return len(str(telefono)) <= 10


def validar_operador(operador):
    valid_operators = read_ivr_table()
    return operador in valid_operators
    

host = os.getenv('LB_HOST')
user = os.getenv('LB_USER')
password = os.getenv('LB_PASSWORD')
database = os.getenv('LB_DATABASE')


def validar_credenciales(correo, contrasena):
    try:
        
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)

        cursor = connection.cursor()

        query = "SELECT * FROM credenciales WHERE user = %s AND password = %s"
        cursor.execute(query, (correo, contrasena))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result:
            return True
        else:
            return False

    except Exception as e:
        print("Error al validar las credenciales:", e)
        return False
    
  #Agregar nuevos usuarios  
db_config = {
    'host': os.getenv('LB_HOST'),
    'user': os.getenv('LB_USER'),
    'password': os.getenv('LB_PASSWORD'),
    'database': os.getenv('LB_DATABASE')
}
    
def validar_admin(correo, contrasena):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = "SELECT * FROM admin WHERE user = %s AND password = %s"
        cursor.execute(query, (correo, contrasena))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return User(result[0]) 
        else:
            return None

    except Exception as e:
        print("Error al validar las credenciales:", e)
        return None

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/', methods=['POST'])
def login():
    correo = request.form['correo']
    contrasena = request.form['contrasena']

    if validar_credenciales(correo, contrasena):
        return render_template('index.html')
    else:
        return "Credenciales incorrectas"


@app.route("/upload", methods=["POST"])
def upload():
    try:
        #Lectura de archivo
        file = request.files["file"]
        df = pd.read_excel(file)
        errores = []

        #Validaciones de info
        for i, row in df.iterrows():
            if not validar_tipo_call(row["tipo_call"]):
                errores.append((i, "tipo_call", row["tipo_call"]))
            if not validar_identificacion(row["Identificacion"]):
                errores.append((i, "Identificacion", row["Identificacion"]))
            # if not validar_resultado_maquina(row["resultado_maquina"]):
            #     errores.append((i, "resultado_maquina", row["resultado_maquina"]))
            if not validar_telefono(row["telefono"]):
                errores.append((i, "telefono", row["telefono"])) 
            if not validar_formato_fecha(str(row["fecha"])):
                errores.append((i, "fecha", row["fecha"]))
            if not validar_operador(row["operado_por"]):
                errores.append((i, "operado_por", row["operado_por"]))
        if errores:
            for error in errores:
                flash(
                    (
                        "Error en:",
                        f"Fila: {error[0]+2}, campo: {error[1]}, valor: {error[2]}",
                    )
                )
        else:
            flash("Success, Todos los datos son correctos.")

            load_dotenv()
            host = os.getenv('LB_HOST')
            user = os.getenv('LB_USER')
            password = os.getenv('LB_PASSWORD')
            database = os.getenv('LB_DATABASE')

            def create_connection():
                try:
                    connection = mysql.connector.connect(
                        host=host,
                        user=user,
                        password=password,
                        database=database
                    )
                    if connection.is_connected():
                        flash("Conexión a la base de datos exitosa")
                        return connection
                except Exception as e:
                    flash("Error en la conexión a la base de datos.", e)
                    return None

            def read_load_table(connection):
                try:
                    cursor = connection.cursor()
                    df = pd.read_excel(file)                    
                    for index, fila in df.iterrows():
                        sql_insertar = f"""
                        INSERT INTO valip (tipo_call, id_campana, nombre_cliente, apellido_cliente, identificacion, resultado_maquina, telefono, fecha, operado_por)
                        VALUES ('{fila[0]}', '{fila[1]}', '{fila[2]}', '{fila[3]}', '{fila[4]}', '{fila[5]}', '{fila[6]}', '{fila[7]}', '{fila[8]}')
                        """
                        cursor.execute(sql_insertar)    
                    connection.commit()
                    cursor.close()
                    flash("Cargue de datos a la tabla exitoso")
                except Exception as e:
                    flash("Error en el cargue a la base de datos.", e)
            
            conexion = create_connection()
            if conexion:
                read_load_table(conexion)
                conexion.close()
    except Exception as e:
        flash(f"Error: {str(e)}")

    return render_template("index.html")


#Validar usuarios admin
@app.route('/admin', methods=['GET'])
def login2():
    return render_template('login_admin.html')

@app.route('/admin', methods=['POST', 'GET'])
def login_admin():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        
        user = validar_admin(correo, contrasena)
        if user:
            login_user(user)
            return redirect(url_for('add_user'))
        else:
            return "Credenciales incorrectas"

    return render_template('login_admin.html')

@app.route('/admin/add_user', methods=['GET'])
@login_required
def add_user():
    return render_template('admin.html')


@app.route('/admin/add_user', methods=['POST'])
@login_required
def admin_superadmin():
    correo = request.form['username']
    contrasena = request.form['password']
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO credenciales (user, password) VALUES (%s, %s)"
        values = (correo, contrasena)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        print("Se agrego correctamente")
        return "Usuario agregado correctamente"

    except Exception as e:
        print('Error al guardar usuario', e)
        return "Error al guardar usuario: " + str(e)


if __name__ == "__main__":
    app.run(debug=True)
