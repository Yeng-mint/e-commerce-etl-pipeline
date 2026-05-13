import sys
sys.path.append(".")

from src.extract import cargar_csvs
import pandas as pd

datos = cargar_csvs()#obtenemos los csvs 

def explorar(df, nombre):
    print(f"\n{'='*55}")
    print(f"  TABLA: {nombre.upper()}")

    print(f"{'='*55}")
    print(f"  Filas: {df.shape[0]:,}   Columnas: {df.shape[1]}")

    print(f"\n--- Primeras 3 filas ---")

    print(df.head(3).to_string())
    print(f"\n--- Tipos de datos ---")
    print(df.dtypes)

    print(f"\n--- Valores nulos por columna ---")
    nulos = df.isnull().sum()

    print(nulos[nulos > 0] if nulos.sum() > 0 else "  Sin valores nulos")
    print(f"\n--- Duplicados: {df.duplicated().sum()} ---")

for nombre, df in datos.items():
    explorar(df, nombre)



print("  Verificacion de las claves :)")
print("="*55)

ids_orders     = set(datos["orders"]["order_id"])
ids_items      = set(datos["order_items"]["order_id"])
ids_payments   = set(datos["order_payments"]["order_id"])
ids_sin_orden  = ids_items - ids_orders

print(f"\n order_items sin order_id en orders: {len(ids_sin_orden)}")
print(f"order_payments sin order_id en orders: {len(ids_payments - ids_orders)}")


ids_customers  = set(datos["customers"]["customer_id"])
ids_en_orders  = set(datos["orders"]["customer_id"])
print(f"orders sin customer_id en customers: {len(ids_en_orders - ids_customers)}")


ids_productos  = set(datos["products"]["product_id"])
ids_en_items   = set(datos["order_items"]["product_id"])
print(f"order_items sin product_id en products: {len(ids_en_items - ids_productos)}")

print("\nVerificación completa con exito")