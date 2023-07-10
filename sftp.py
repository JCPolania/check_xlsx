import pysftp
from dotenv import load_dotenv
import os

load_dotenv()

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

host = os.getenv("SF_HOST")
user = os.getenv("SF_USER")
password = os.getenv("SF_PASSWORD")
key_password= os.getenv("SF_SECURITY_KEY")

def create_connection_sftp():
    try: 
        with pysftp.Connection(host=host, username=user, private_key='./pem.pem', private_key_pass=password, cnopts = cnopts) as sftp:
            with sftp.cd("/home/validadorpr/Pruebas"):
                # sftp.put("file")
                print("Conexión a la Sftp con exito")

    except Exception as e:
        print("Error en la conexión a la sftp.", e)
    


