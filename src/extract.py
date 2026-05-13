import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

RAW_PATH = os.getenv("DATA_RAW_PATH", "data/raw")

def cargar_csvs():
    
    archivos = {
        "customers":            "olist_customers_dataset.csv",
        "geolocation":          "olist_geolocation_dataset.csv",
        "order_items":          "olist_order_items_dataset.csv",
        "order_payments":       "olist_order_payments_dataset.csv",
        "order_reviews":        "olist_order_reviews_dataset.csv",
        "orders":               "olist_orders_dataset.csv",
        "products":             "olist_products_dataset.csv",
        "sellers":              "olist_sellers_dataset.csv",    
        "product_category_name_translation": "product_category_name_translation.csv" 
        
        
    }

    datos = {}
    for nombre, archivo in archivos.items():
        ruta = os.path.join(RAW_PATH, archivo)
        datos[nombre] = pd.read_csv(ruta)
        print(f"{nombre}: {datos[nombre].shape[0]} filas, {datos[nombre].shape[1]} columnas]")
    return datos

if __name__ == "__main__":
    datos = cargar_csvs()