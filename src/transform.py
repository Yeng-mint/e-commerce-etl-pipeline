import pandas as pd
from dotenv import load_dotenv
import os


load_dotenv()
PROCESSED_PATH = os.getenv("DATA_PROCESSED_PATH", "data/processed")


#dimension cliente:

def transformar_dim_cliente(customers):
    df = customers.copy()

    df = df.reset_index(drop=True)
    df["id_cliente"] = df.index + 1

    
    df["nombre"] = df["customer_unique_id"]
    df["ciudad"] = df["customer_city"].str.strip().str.title()
    df["estado"] = df["customer_state"].str.strip().str.upper()

    return df[["id_cliente", "nombre", "ciudad", "estado","customer_id"]]  

#dimension ubicacion:

def transformar_dim_ubicacion(geolocation):
 
    df = geolocation.copy()

 
    df = df.groupby("geolocation_zip_code_prefix").agg(
        geolocation_lat=("geolocation_lat", "mean"),
        geolocation_lng=("geolocation_lng", "mean"),
        ciudad=("geolocation_city", "first"),
        estado=("geolocation_state", "first")

    ).reset_index()

    df = df.reset_index(drop=True)
    df["id_ubicacion"] = df.index + 1

    df["ciudad"] = df["ciudad"].str.strip().str.title()
    df["estado"] = df["estado"].str.strip().str.upper()
    df["pais"]   = "Brasil" 
    return df[["id_ubicacion", "ciudad", "estado", "pais",
               "geolocation_zip_code_prefix"]]  


#dim producto:
def transformar_dim_producto(products, product_category):

    df = products.copy()


    df = df.merge(product_category, on="product_category_name", how="left")

    # Rellenamos nulos en categoria
    df["product_category_name"]         = df["product_category_name"].fillna("sin_categoria")
    df["product_category_name_english"] = df["product_category_name_english"].fillna("uncategorized")

    
    for col in ["product_weight_g", "product_length_cm",
                "product_height_cm", "product_width_cm"]:
        df[col] = df[col].fillna(df[col].median())

    df = df.reset_index(drop=True)
    df["id_producto"] = df.index + 1


    return df[["id_producto", "product_id",
               "product_category_name_english",
               "product_weight_g"]].rename(columns={
                   "product_category_name_english": "categoria",
                   "product_weight_g":              "peso"
               })


#dim pago:
def transformar_dim_pago(order_payments):
    """
    Fuente: order_payments
    Decisión: un pedido puede tener varios métodos de pago.
    Nos quedamos con el método principal (payment_sequential == 1)
    """
    df = order_payments.copy()

    df = df[df["payment_sequential"] == 1].copy()
    df = df.reset_index(drop=True)
    df["id_pago"] = df.index + 1

    return df[["id_pago", "order_id", "payment_type",
               "payment_installments"]].rename(columns={
                   "payment_type":         "tipo_pago",
                   "payment_installments": "cuotas"
               })


# dim tiempo:
def transformar_dim_tiempo(orders):
    """
    Fuente: orders (columna order_purchase_timestamp)
    Problema detectado: todas las fechas son string → convertir a datetime
    """
    df = orders[["order_purchase_timestamp"]].drop_duplicates().copy()

    # Convertimos el string a datetime real
    df["fecha"] = pd.to_datetime(df["order_purchase_timestamp"])

    df = df.reset_index(drop=True)
    df["id_tiempo"]  = df.index + 1
    df["año"]        = df["fecha"].dt.year
    df["mes"]        = df["fecha"].dt.month
    df["dia"]        = df["fecha"].dt.day
    df["trimestre"]  = df["fecha"].dt.quarter

    return df[["id_tiempo", "fecha", "año", "mes", "dia", "trimestre",
               "order_purchase_timestamp"]]  


# dim fact tables
def transformar_fact_sales(orders, order_items, dim_cliente, dim_producto, dim_tiempo, dim_ubicacion, dim_pago, customers):

    
    df = orders.merge(order_items, on="order_id", how="inner")

    # Convertimos fechas
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])

    # Nulos en fechas de entrega
    # pero calculamos tiempo_entrega solo cuando esta disponible
    df["order_delivered_customer_date"] = pd.to_datetime(
        df["order_delivered_customer_date"], errors="coerce")
    df["order_approved_at"] = pd.to_datetime(
        df["order_approved_at"], errors="coerce")

    df["tiempo_entrega"] = df["order_delivered_customer_date"]

    # Métricas de la venta
    df["total_venta"]          = df["price"] + df["freight_value"]
    df["cantidad_productos"]   = 1  # cada fila es 1 ítem
    df["costo_envio"]          = df["freight_value"]

    # union de llaves foraneas para dimensiones:

    # id_cliente
    df = df.merge(dim_cliente[["id_cliente", "customer_id"]],
                  on="customer_id", how="left")

    # id_producto
    df = df.merge(dim_producto[["id_producto", "product_id"]],
                  on="product_id", how="left")

   
    # id_tiempo a datetime
    dim_tiempo_merge = dim_tiempo[["id_tiempo", "order_purchase_timestamp"]].copy()
    dim_tiempo_merge["order_purchase_timestamp"] = pd.to_datetime(
    dim_tiempo_merge["order_purchase_timestamp"])

    df = df.merge(dim_tiempo_merge, on="order_purchase_timestamp", how="left")

    # id_ubicacion (via zip_code del cliente)
    clientes_zip = customers[["customer_id", "customer_zip_code_prefix"]]
    df = df.merge(clientes_zip, on="customer_id", how="left")
    df = df.merge(
        dim_ubicacion[["id_ubicacion", "geolocation_zip_code_prefix"]],
        left_on="customer_zip_code_prefix",
        right_on="geolocation_zip_code_prefix", how="left")

    # id_pago
    df = df.merge(dim_pago[["id_pago", "order_id"]],
                  on="order_id", how="left")

    # id_venta autoincremental
    df = df.reset_index(drop=True)
    df["id_venta"] = df.index + 1

    columnas_finales = [
        "id_venta", "total_venta", "cantidad_productos",
        "costo_envio", "tiempo_entrega",
        "id_cliente", "id_producto", "id_tiempo",
        "id_ubicacion", "id_pago"
    ]
    return df[columnas_finales]



def transformar_todo(datos):
    print("\nIniciando transformaciones...")

    dim_cliente   = transformar_dim_cliente(datos["customers"])
    print(f"  Dim_Cliente:    {len(dim_cliente):,} filas")

    dim_ubicacion = transformar_dim_ubicacion(datos["geolocation"])
    print(f" Dim_Ubicacion:  {len(dim_ubicacion):,} filas")

    dim_producto  = transformar_dim_producto(datos["products"], datos["product_category_name_translation"])
    print(f" Dim_Producto:   {len(dim_producto):,} filas")

    dim_pago      = transformar_dim_pago(datos["order_payments"])
    print(f"  Dim_Pago:       {len(dim_pago):,} filas")

    dim_tiempo    = transformar_dim_tiempo(datos["orders"])
    print(f" Dim_Tiempo:     {len(dim_tiempo):,} filas")

    fact_sales    = transformar_fact_sales(
        datos["orders"], datos["order_items"],
        dim_cliente, dim_producto, dim_tiempo,
        dim_ubicacion, dim_pago, datos["customers"]
    )
    print(f"  Fact_Sales:     {len(fact_sales):,} filas")

    tablas = {
        "dim_cliente":   dim_cliente.drop(columns=["customer_id"]),
        "dim_ubicacion": dim_ubicacion.drop(columns=["geolocation_zip_code_prefix"]),
        "dim_producto":  dim_producto.drop(columns=["product_id"]),
        "dim_pago":      dim_pago.drop(columns=["order_id"]),
        "dim_tiempo":    dim_tiempo.drop(columns=["order_purchase_timestamp"]),
        "fact_sales":    fact_sales
    }

    # Guardamos CSVs procesados
    os.makedirs(PROCESSED_PATH, exist_ok=True)
    for nombre, df in tablas.items():
        ruta = os.path.join(PROCESSED_PATH, f"{nombre}.csv")
        df.to_csv(ruta, index=False)
        print(f" Guardado: {ruta}")

    return tablas


if __name__ == "__main__":
    
    from extract import cargar_csvs
    
    datos   = cargar_csvs()
    tablas  = transformar_todo(datos)
    print("\nTransformacion completada.")