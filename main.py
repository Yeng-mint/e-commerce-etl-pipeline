from src.extract   import cargar_csvs
from src.transform import transformar_todo
from src.load      import cargar_todo
from src.database  import verificar_conexion

def main():

    print("PIPELINE ETL- ecommerce olist")
  

    # Funcionamiento de la pipeline:
    #1- verifacion de la conexion con la base de datos

    engine = verificar_conexion()

    # 2- Extraccion de los datos
    print("\n Fase de extraccion de los datos ")
    datos = cargar_csvs()

    # 3- Transformamos los datos
    print("\n Fase de transformacion de los datos ")
    transformar_todo(datos)

    # 4- Cargar
    print("\n Fase de carga a PostgreSQL...")
    cargar_todo(engine)

    print("\n")
    print("\n  Pipeline ETL completado exitosamente")
    print("Se ha realizo la extraccion, transformacion y carga de los datos a PostgreSQL")
  

if __name__ == "__main__":
    main()