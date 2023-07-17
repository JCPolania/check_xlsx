from flask import Flask, render_template, request, flash
import pandas as pd
# from werkzeug.utils import secure_filename
from database import get_ivr_data
# from sftp import create_connection_sftp
from dotenv import load_dotenv
import os
import mysql.connector


load_dotenv()
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/"
app.secret_key = os.getenv('C_SECRECT')


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
    valid_operators = get_ivr_data()
    return operador in valid_operators


@app.route("/")
def index():
    return render_template("index.html")





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
            flash(("success", "Todos los datos son correctos."))

            load_dotenv()
            host = os.getenv('LB_HOST')
            user = os.getenv('LB_USER')
            password = os.getenv('LB_PASSWORD')
            database = os.getenv('LB_DATABASE')

            # Función para crear y obtener la conexión a la base de datos
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


if __name__ == "__main__":
    app.run(debug=True)
