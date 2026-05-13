from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

#funcion para crear la conexion mediante .env
def get_engine():
  
    host     = os.getenv("DB_HOST", "localhost")
    port     = os.getenv("DB_PORT", "5433")
    name     = os.getenv("DB_NAME", "ecommerce_db")
    user     = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres123")

#genera una ulr de conexion a la base de datos
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"

    engine = create_engine(url)
    return engine

#funcion para verificar una correcta conexion.
def verificar_conexion():

    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("conexion exitosa con la base de datos")
        return engine
    
    except Exception as e:
        print(f"ERROR en la conexion{e}")

if __name__ == "__main__":
    verificar_conexion()