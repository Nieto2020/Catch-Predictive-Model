import pandas as pd
import numpy as np
from pathlib import Path

def cargar_y_limpiar_datos(ruta_archivo):
   
    
    # --- PARTE 1: CARGA Y CONSOLIDACIÓN ---
    print(f"Iniciando carga desde: {ruta_archivo}")
    
    # Carga todas las hojas en un diccionario {nombre_hoja: DataFrame}
    diccionario_de_hojas = pd.read_excel(ruta_archivo, sheet_name=None)
    
    print(f"Se encontraron {len(diccionario_de_hojas)} hojas. Consolidando...")
    
    # Lista para guardar los DataFrames individuales
    lista_dfs = []

    # Bucle para recorrer cada hoja en el diccionario
    for nombre_hoja, df_hoja in diccionario_de_hojas.items():
        
        df_hoja['fuente_encuesta'] = nombre_hoja
        lista_dfs.append(df_hoja)
        
    # Concatena todos los DataFrames de la lista en uno solo
    df = pd.concat(lista_dfs, ignore_index=True)
    
    print(f"Datos consolidados. {len(df)} filas cargadas.")
    print("Iniciando proceso de limpieza estándar...")

    # --- PARTE 2: PROCESO DE LIMPIEZA ESTÁNDAR ---

    print("\n--- Estado INICIAL de los datos (tipos y nulos) ---")
    df.info()

    # --- PASO 1: Manejo de Valores Nulos (NaN) ---
    print("\n--- PASO 1: Manejando valores nulos... ---")
    
    # Primero, calculamos la mediana de la columna 'salario'
    if 'salario' in df.columns:
        mediana_salario = df['salario'].median()
        # Rellenamos los NaN (nulos) en 'salario' con el valor de la mediana
        df['salario'] = df['salario'].fillna(mediana_salario)
        print(f"Valores nulos de 'salario' rellenados con la mediana: {mediana_salario}")
    
    # Estrategia para 'pregunta_abierta_1': Es texto libre.
    if 'pregunta_abierta_1' in df.columns:
        df['pregunta_abierta_1'] = df['pregunta_abierta_1'].fillna('')
        print("Valores nulos de 'pregunta_abierta_1' rellenados con '' (texto vacío).")

    # Estrategia para 'sector_empresa': Es categórico.
    # Rellenamos con una categoría específica "Desconocido".
    if 'sector_empresa' in df.columns:
        df['sector_empresa'] = df['sector_empresa'].fillna('Desconocido')
        print("Valores nulos de 'sector_empresa' rellenados con 'Desconocido'.")
    
    
    
    # --- PASO 2: Corrección de Tipos de Datos ---
    print("\n--- PASO 2: Corrigiendo tipos de datos... ---")

    
    if 'salario' in df.columns:
        # Forzamos 'salario' a ser un número. 
        df['salario'] = pd.to_numeric(df['salario'], errors='coerce')
        # Como 'coerce' pudo crear NUEVOS NaN, volvemos a rellenarlos por si acaso.
        mediana_salario = df['salario'].median()
        df['salario'] = df['salario'].fillna(mediana_salario)
        print("Tipo de dato de 'salario' asegurado como numérico.")
    
    # Las columnas categóricas (como 'sector' o 'region') se optimizan
    # usando el tipo 'category'. Esto ahorra memoria y acelera los cálculos.
    if 'sector_empresa' in df.columns:
        df['sector_empresa'] = df['sector_empresa'].astype('category')
        print("Tipo de dato de 'sector_empresa' optimizado a 'category'.")

    # --- PASO 3: Manejo de Duplicados ---
    print("\n--- PASO 3: Buscando y eliminando duplicados... ---")

    # Primero, contamos cuántas filas están completamente duplicadas
    duplicados = df.duplicated().sum()
    print(f"Se encontraron {duplicados} filas duplicadas.")
    
    if duplicados > 0:
        df.drop_duplicates(inplace=True)
        print("Filas duplicadas eliminadas.")

    # --- PASO 4: Normalización de Texto  ---
    print("\n--- PASO 4: Normalizando texto... ---")
    
    # --Lo pasamos todo a minúsculas.
    
    if 'sector_empresa' in df.columns:
        df['sector_empresa'] = df['sector_empresa'].str.lower()
        print("Texto de 'sector_empresa' convertido a minúsculas.")
    
    # --- FINALIZACIÓN ---
    print("\n¡Proceso de limpieza estándar completado!")
    
    # Imprime un resumen de los datos DESPUÉS de limpiar
    print("\n--- Estado FINAL de los datos (tipos y nulos) ---")
    df.info()
    
    # La función devuelve el DataFrame limpio y listo para usarse
    return df

if __name__ == "__main__":
    datos_dir = Path("datos")

    # Archivo principal que preferimos leer, en caso de no encontrarlo, buscamos cualquier otro Excel en la carpeta
    principal = datos_dir / "BASE HISTORICA.xlsx"

    if principal.exists():
        ruta = principal
        print(f"Usando archivo principal: {ruta.name}")
    else:
        print(f"Archivo principal no encontrado: {principal.name}")

        # Si existe la carpeta, buscar cualquier archivo excel como fallback
        if datos_dir.exists():
            excels = [p for p in datos_dir.iterdir() if p.suffix.lower() in ('.xls', '.xlsx', '.xlsm', '.xlsb')]
            if excels:
                # Tomamos el primero encontrado; se informa al usuario que es fallback
                ruta = excels[0]
                print(f"Usando archivo fallback encontrado en 'datos/': {ruta.name}")
            else:
                # No hay archivos excel en la carpeta
                print("Archivos disponibles en 'datos/':")
                for p in datos_dir.iterdir():
                    print(f" - {p.name}")
                raise FileNotFoundError(
                    "No se encontró 'BASE HISTORICA.xlsx' ni ningún archivo .xls/.xlsx en la carpeta 'datos/'."
                )
        else:
            raise FileNotFoundError("La carpeta 'datos' no existe en el directorio actual.")

    # Ejecuta la función con la ruta determinada (principal o fallback)
    df = cargar_y_limpiar_datos(str(ruta))