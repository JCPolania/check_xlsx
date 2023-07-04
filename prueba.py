import mysql.connector
from dotenv import load_dotenv
import os


load_dotenv()

host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
database = os.getenv('DB_DATABASE')

def create_connection():
    try: 
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database
                                    )
        
        if connection.is_connected():
            # print("Conexión exitosa a la base de datos")
            return connection
    except Exception as e:
        # print("Errror en la conexión a la base de datos.", e)
        return None



def read_ivr_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT operador FROM ivr_2")

        rows = cursor.fetchall()

        strings = [row[0] for row in rows]
        return strings
        

    except Exception as e:
        print("Error al leer la tabla IVR_2", e)


def get_ivr_data():
    connection = create_connection()
    
    if connection:
        ivr_data = read_ivr_table(connection)
        connection.close()
        return ivr_data
    else: 
        print("No se logró establecer la conexión a la base de datos.")
        return None

    


