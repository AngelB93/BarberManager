import os
import pytds
from dotenv import load_dotenv

load_dotenv()

def conectar():
    conexion = pytds.connect(
        server=os.getenv("DB_SERVER"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conexion