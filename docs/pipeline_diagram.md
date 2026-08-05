# ETL Pipeline Architecture

## 1. Block Diagram.

El siguiente diagrama ilustra el flujo de los datos desde que son extraídos de los sistemas origen, hasta que son cargados en la base de datos analítica.

```mermaid
flowchart LR
    %% Defining Styles
    classDef source fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef process fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b
    classDef output fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef query fill:#fff3e0,stroke:#f57c00,stroke-width:2px

    %% Data Sources
    subgraph Sources [1. Data Sources]
        direction TB
        S1[(Cali CSV)]:::source
        S2[(Bogotá JSON)]:::source
        S3[(Medellín XML)]:::source
        Ref[(Reference Tables)]:::source
    end

    %% Pipeline Processing
    subgraph ETL [2. ETL Pipeline Stages]
        direction LR
        E(EXTRACT):::process --> P(PROFILE):::process
        P --> C(CLEAN &<br>HARMONIZE):::process
        C --> T(TRANSFORM &<br>INTEGRATE):::process
        T --> V(VALIDATE):::process
        V --> L(LOAD):::process
    end

    %% Outputs
    subgraph Outputs [3. Analytical Outputs]
        direction TB
        CSV[integrated_sales.csv]:::output
        DB[(retail_analytics.db)]:::output
    end

    %% Queries
    Q(ANALYTICAL<br>QUERIES):::query

    %% Connections
    S1 & S2 & S3 & Ref --> E
    L --> CSV
    L --> DB
    DB -.-> Q
```

---

## 2. Pipeline Blocks Definition

Para mantener el sistema ordenado, cada bloque tiene una única responsabilidad y una salida específica.

| Block (Bloque) | Input (Entrada) | Processing Responsibility (Responsabilidad) | Output (Salida) | Possible Failure (Posible Fallo) |
| :--- | :--- | :--- | :--- | :--- |
| **Extract** | Archivos crudos (CSV, JSON, XML) | Leer y estandarizar datos de diferentes formatos hacia una estructura común (Pandas DataFrame) sin aplicar cálculos de negocio. | Pandas DataFrames Crudos | Archivo no encontrado, o error al leer (parsing error). |
| **Profile** | DataFrames Crudos | Analizar estadísticamente los datos extraídos para descubrir problemas de calidad (nulos, duplicados, datos inválidos). | Resumen de Perfilamiento | *No altera datos, usualmente no falla.* |
| **Clean & Harmonize** | DataFrames Crudos | Estandarizar formatos (IDs en mayúsculas), corregir datos inválidos, manejar valores nulos y eliminar duplicados. | DataFrames Limpios | Exceso de registros inválidos causando pérdida masiva de datos. |
| **Transform & Integrate** | DataFrames Limpios + Tablas Referencia | Cruzar ventas con las referencias (Productos, Tiendas, Promos) y calcular KPIs de negocio (`gross_sales`, `net_sales`, fechas). | DataFrame Integrado | IDs huérfanos (ej: se vendió un producto que no existe en el catálogo). |
| **Validate** | DataFrame Integrado | Comprobar reglas críticas antes de guardar: campos no nulos, IDs únicos, precios no negativos, que cruces de tablas cuadren. | DataFrame Validado | Violación de regla crítica (detiene el pipeline para no ensuciar la BD). |
| **Load** | DataFrame Validado | Guardar el dataset limpio en almacenamiento persistente (CSV) y en la base de datos analítica final (SQLite). | `integrated_sales.csv` y `retail_analytics.db` | Fallo de conexión a la base de datos o disco lleno. |
| **Query** | `retail_analytics.db` | Ejecutar consultas SQL (Analytical Queries) enfocadas en responder las preguntas de negocio. | Tablas de Resultados / Reportes | Error de sintaxis SQL o tablas no encontradas. |
