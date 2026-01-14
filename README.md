# practicafinal_vsd
================================================================================
README - FAOSTAT Food Prices Data Analysis
================================================================================
Autor: Abdallah Tegguer
Proyecto: Análisis y Visualización de Datos de Precios Alimentarios
================================================================================

DESCRIPCIÓN
================================================================================
Script de Python que procesa datos de FAOSTAT Food Prices y genera archivos
CSV listos para visualización en Tableau.

REQUISITOS DEL SISTEMA
================================================================================
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

BIBLIOTECAS NECESARIAS
================================================================================
Instalar las siguientes bibliotecas antes de ejecutar el script:

pip install pandas numpy

ARCHIVOS DE ENTRADA REQUERIDOS
================================================================================
Coloca los siguientes archivos CSV en la misma carpeta que analizar.py:

1. Prices_E_All_Data.csv
2. Prices_E_AreaCodes.csv
3. Prices_E_ItemCodes.csv
4. Prices_E_Elements.csv
5. Prices_E_Flags.csv

Estos archivos se descargan desde: https://www.fao.org/faostat/en/#data/PP

CÓMO EJECUTAR
================================================================================

1. Abre una terminal o línea de comandos

2. Navega a la carpeta del proyecto:
   cd */practicafinal_vsd/visualizacion de datos

3. Ejecuta el script:
   python analizar.py

4. Espera a que termine el procesamiento (2-3 minutos aproximadamente)

ARCHIVOS DE SALIDA
================================================================================
El script genera una carpeta llamada 'output/' con los siguientes archivos:

1. 01_FAOSTAT_Prices_Clean_Long.csv - Dataset principal
2. 02_Country_Metrics.csv - Métricas por país
3. 03_Product_Metrics.csv - Métricas por producto
4. 04_Regional_Aggregates.csv - Agregados regionales
5. 05_Country_Category_Metrics.csv - Métricas país-categoría

Estos archivos están listos para utilizar en la visualizacion.

SOLUCIÓN DE PROBLEMAS
================================================================================

Error: "ModuleNotFoundError: No module named 'pandas'"
Solución: Instala pandas con: pip install pandas

Error: "FileNotFoundError: [Errno 2] No such file or directory"
Solución: Verifica que todos los archivos CSV estén en la misma carpeta

Error: "UnicodeDecodeError"
Solución: El script usa encoding='latin-1' automáticamente, no requiere acción

ESTRUCTURA DEL PROYECTO
================================================================================
proyecto/
├── analizar.py                      # Script principal
├── Prices_E_All_Data.csv           # Datos de entrada
├── Prices_E_AreaCodes.csv          # Códigos de países
├── Prices_E_ItemCodes.csv          # Códigos de productos
├── Prices_E_Elements.csv           # Tipos de medición
├── Prices_E_Flags.csv              # Banderas de calidad
├── output/                          # Carpeta de salida (se crea automáticamente)
│   ├── 01_FAOSTAT_Prices_Clean_Long.csv
│   ├── 02_Country_Metrics.csv
│   ├── 03_Product_Metrics.csv
│   ├── 04_Regional_Aggregates.csv
│   └── 05_Country_Category_Metrics.csv
└── README.txt                       # Este archivo

CONTACTO
================================================================================
Para preguntas o problemas, contactar a: Abdallah Tegguer
ategguer@uoc.edu
abdallahtegguer@hotmail.com

================================================================================
