import pandas as pd
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

PROCESSED_PATH = os.getenv("DATA_PROCESSED_PATH", "data/processed")

#funcion para cargar las dimensiones 
def cargar_tabla(df, nombre_tabla, engine):
  
    try:
        df.to_sql(
            name=nombre_tabla,
            con=engine,
            if_exists="append",   
            index=False,          # no incluimos los indices.
            method="multi",       
            chunksize=1000        # de 1000 en 1000 filas
        )
        print(f" {nombre_tabla}: {len(df):,} filas cargadas")
    except Exception as e:
        print(f" Error cargando {nombre_tabla}: {e}")


#funcion limpiar tablas para evitar duplicados

def limpiar_tablas(engine):

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE fact_sales RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_cliente RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_ubicacion RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_producto RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_pago RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_tiempo RESTART IDENTITY CASCADE"))
    print("Tablas limpiadas correctamente")
def cargar_todo(engine):


    print("\nIniciando carga a PostgreSQL...")

    limpiar_tablas(engine)

    # 
    tablas = [
        "dim_cliente",
        "dim_ubicacion",
        "dim_producto",
        "dim_pago",
        "dim_tiempo",
        "fact_sales",
    ]

    for nombre in tablas:
        ruta = os.path.join(PROCESSED_PATH, f"{nombre}.csv")

        
        df = pd.read_csv(ruta)

       
        if nombre == "dim_tiempo":
            df["fecha"] = pd.to_datetime(df["fecha"])

        if nombre == "fact_sales":
            df["tiempo_entrega"] = pd.to_datetime(
                df["tiempo_entrega"], errors="coerce")

        cargar_tabla(df, nombre, engine)

    print("\n Carga completa a PostgreSQL")


if __name__ == "__main__":
    from src.database import get_engine
    engine = get_engine()
    cargar_todo(engine)