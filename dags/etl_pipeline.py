#archivo DAG
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# ruta con los scripts
sys.path.insert(0, "/opt/airflow")

# configuracion del servicio
default_args = {
    "owner":            "ecommerce_etl",# usuario
    "retries":          2,                        # reintenta 2 veces si falla
    "retry_delay":      timedelta(minutes=5),     # espera 5 min entre reintentos
    "email_on_failure": False,
}

# funcion descripcion del DAG
dag = DAG(
    dag_id="ecommerce_etl_pipeline",
    description="Pipeline ETL completo del dataset Olist",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 6 * * *",  # todos los dias a las 6am
    catchup=False,                  # no ejecuta fechas pasadas
    tags=["ecommerce", "etl", "olist"],
)


#funcion lectura y extraccion
def tarea_extraer(**context):

    from src.extract import cargar_csvs
    datos = cargar_csvs()
    print(f"Extracción completa: {len(datos)} tablas cargadas")
    # Guardamos los nombres para verificar en el log
    for nombre, df in datos.items():
        print(f"  - {nombre}: {len(df):,} filas")
    return list(datos.keys())

#funcion transformacion
def tarea_transformar(**context):
   
    from src.extract import cargar_csvs
    from src.transform import transformar_todo
    datos  = cargar_csvs()
    tablas = transformar_todo(datos)
    print(f"Transformación completa: {len(tablas)} tablas procesadas")
    for nombre, df in tablas.items():
        print(f"  - {nombre}: {len(df):,} filas")

# funcion carga de datos limpios
def tarea_cargar(**context):

    from src.database import get_engine
    from src.load import cargar_todo
    engine = get_engine()
    cargar_todo(engine)
    print("Carga a PostgreSQL completa")


def tarea_verificar(**context):
    
    from src.database import get_engine
    from sqlalchemy import text
    engine = get_engine()

    tablas = [
        "dim_cliente", "dim_ubicacion", "dim_producto",
        "dim_pago", "dim_tiempo", "fact_sales"
    ]

    with engine.connect() as conn:
        print("\nVerificación final:")
        for tabla in tablas:
            resultado = conn.execute(
                text(f"SELECT COUNT(*) FROM {tabla}"))
            count = resultado.scalar()
            print(f" - {tabla}: {count:,} filas")

            # Si alguna tabla está vacía, el pipeline falló
            if count == 0:
                raise ValueError(
                    f"La tabla {tabla} está vacía — algo falló en la carga")

    print("\nPipeline verificado exitosamente")



t1_extraer = PythonOperator(
    task_id="extraer_csvs",
    python_callable=tarea_extraer,
    dag=dag,
)

t2_transformar = PythonOperator(
    task_id="transformar_datos",
    python_callable=tarea_transformar,
    dag=dag,
)

t3_cargar = PythonOperator(
    task_id="cargar_postgresql",
    python_callable=tarea_cargar,
    dag=dag,
)

t4_verificar = PythonOperator(
    task_id="verificar_carga",
    python_callable=tarea_verificar,
    dag=dag,
)

#orden de ejecucion
# extraer, transforma, carga los datos y los verfica
t1_extraer >> t2_transformar >> t3_cargar >> t4_verificar