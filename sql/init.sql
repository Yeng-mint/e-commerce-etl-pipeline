
--Esquema de base de datos para el proyecto de ecommerce
--Creado por: Perez Ramirez Luis Alejandro


-- Eliminas tablas e hijos si existen.
DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_cliente CASCADE;
DROP TABLE IF EXISTS dim_ubicacion CASCADE;
DROP TABLE IF EXISTS dim_producto CASCADE;
DROP TABLE IF EXISTS dim_pago CASCADE;
DROP TABLE IF EXISTS dim_tiempo CASCADE;


-- creamos  las tabla dimension cliente
CREATE TABLE dim_cliente (
    id_cliente  SERIAL PRIMARY KEY, -- coloca de forma automatica el indice
    nombre      VARCHAR(100),
    ciudad      VARCHAR(50),
    estado      VARCHAR(50)
);

CREATE TABLE dim_ubicacion (
    id_ubicacion  SERIAL PRIMARY KEY,
    ciudad        VARCHAR(50),
    estado        VARCHAR(50),
    pais          VARCHAR(50)
);

CREATE TABLE dim_producto (
    id_producto  SERIAL PRIMARY KEY,
    categoria    VARCHAR(100),
    peso         DECIMAL(10,2)
);

CREATE TABLE dim_pago (
    id_pago    SERIAL PRIMARY KEY,
    tipo_pago  VARCHAR(30), --stirng
    cuotas     INTEGER -- cantidad de cuotas
);

CREATE TABLE dim_tiempo (
    id_tiempo   SERIAL PRIMARY KEY,
    fecha       TIMESTAMP, -- fecha completa
    año         INTEGER,
    mes         INTEGER, -- mes del año (1-12)
    dia         INTEGER,
    trimestre   INTEGER
);

--tabla de hechos central

CREATE TABLE fact_sales (
    id_venta            SERIAL PRIMARY KEY,
    total_venta         DECIMAL(10,2), --decimal o igual float
    cantidad_productos  INTEGER,
    costo_envio         DECIMAL(10,2), --decimal o igual float
    tiempo_entrega      TIMESTAMP,-- formato fecha
    id_cliente          INTEGER REFERENCES dim_cliente(id_cliente),-- referencia a la tabla cliente
    id_producto         INTEGER REFERENCES dim_producto(id_producto),
    id_tiempo           INTEGER REFERENCES dim_tiempo(id_tiempo),
    id_ubicacion        INTEGER REFERENCES dim_ubicacion(id_ubicacion),
    id_pago             INTEGER REFERENCES dim_pago(id_pago)
);

--creacion de los indices para optimizar consultas en la tabla de hechos

CREATE INDEX idx_fact_id_cliente   ON fact_sales(id_cliente);
CREATE INDEX idx_fact_id_producto  ON fact_sales(id_producto);
CREATE INDEX idx_fact_id_tiempo    ON fact_sales(id_tiempo);
CREATE INDEX idx_fact_id_ubicacion ON fact_sales(id_ubicacion);
CREATE INDEX idx_fact_id_pago      ON fact_sales(id_pago);