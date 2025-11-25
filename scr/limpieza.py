import pandas as pd
import numpy as np
from pathlib import Path

def cargar_y_limpiar_datos(ruta_archivo):
    # --- PARTE 1: CARGA Y CONSOLIDACIÓN SELECTIVA ---
    print(f"Iniciando carga selectiva desde: {ruta_archivo}")

    # Columnas a seleccionar: F (índice 5) y GW-GZ (índices 202 a 205)
    # Nota: Los índices en pandas son base 0. F=5, GW=202, GX=203, GY=204, GZ=205
    columnas_a_usar = [5, 202, 203, 204, 205]
    nombres_nuevos = ['compañia', 'Capacitación', 'Bajo Supervisión', 'Sin Supervisión', 'Tope salarial']

    try:
        # Carga todas las hojas, pero solo las columnas especificadas
        diccionario_de_hojas = pd.read_excel(
            ruta_archivo, 
            sheet_name=None, 
            usecols=columnas_a_usar,
            header=None, # No hay encabezados en las filas de datos
            skiprows=2 # Omitir la fila de encabezado original
        )
    except ValueError as e:
        print(f"Error al leer las columnas: {e}")
        print("Es posible que las columnas especificadas (F, GW-GZ) no existan en todas las hojas del Excel.")
        return pd.DataFrame() # Devuelve un DataFrame vacío si hay error

    print(f"Se encontraron {len(diccionario_de_hojas)} hojas. Consolidando...")
    
    lista_dfs = []
    for nombre_hoja, df_hoja in diccionario_de_hojas.items():
        df_hoja.columns = nombres_nuevos
        df_hoja['fuente_encuesta'] = nombre_hoja
        lista_dfs.append(df_hoja)
        
    df = pd.concat(lista_dfs, ignore_index=True)
    
    print(f"Datos consolidados. {len(df)} filas cargadas con columnas seleccionadas.")
    print("Iniciando proceso de limpieza...")

    # --- PARTE 2: TRANSFORMACIÓN Y LIMPIEZA ---

    # Unificar las 4 columnas de salario en una sola: 'salario_diario'
    columnas_salario = ['compañia', 'Capacitación', 'Bajo Supervisión', 'Sin Supervisión', 'Tope salarial']
    
    df = df.melt(
        id_vars=['compañia', 'fuente_encuesta'], 
        value_vars=columnas_salario, 
        var_name='columna_origen_salario', 
        value_name='salario_diario'
    )
    
    # --- PASO 1: Corrección de Tipos y Manejo de Nulos ---
    print("\n--- PASO 1: Limpiando y filtrando datos de salario... ---")

    # Forzar 'salario_diario' a ser numérico. Si hay errores, se convierten en NaN.
    df['salario_diario'] = pd.to_numeric(df['salario_diario'], errors='coerce')
    
    # Eliminar filas donde el salario es nulo (incluyendo los que no eran numéricos)
    df.dropna(subset=['salario_diario'], inplace=True)
    
    # Ahora que es numérico, eliminar filas donde el salario es cero o menor
    df = df[df['salario_diario'] > 0]

    print(f"Columnas de salario unificadas y limpiadas. Total de registros con salario válido: {len(df)}")

    # Limpiar la columna 'compañia'
    df['compañia'] = df['compañia'].fillna('Desconocido').astype(str).str.strip()
    
    # Eliminar filas donde 'compañia' es 'nan' o vacía (después de convertir a string)
    df = df[df['compañia'] != 'nan']
    df = df[df['compañia'] != '']
    df = df[df['compañia'] != 'Desconocido']

    print(f"Filas con valores de compañia válidos: {len(df)}")

    # --- PASO 2: Manejo de Duplicados ---
    print("\n--- PASO 2: Buscando y eliminando duplicados... ---")
    duplicados = df.duplicated().sum()
    print(f"Se encontraron {duplicados} filas duplicadas.")
    
    if duplicados > 0:
        df.drop_duplicates(inplace=True)
        print("Filas duplicadas eliminadas.")

    # --- FINALIZACIÓN ---
    print("\n¡Proceso de limpieza completado!")
    print("\n--- Resumen de los datos limpios ---")
    print(df.info())
    print("\n--- Muestra de los datos finales ---")
    print(df.head())
    
    print("\n--- Compañías presentes en los datos limpios ---")
    print(f"Total de compañías únicas: {df['compañia'].nunique()}")
    print("\nDetalle por compañía:")
    print(df['compañia'].value_counts().sort_index())
    
    return df

if __name__ == "__main__":
    datos_dir = Path("datos")
    principal = datos_dir / "BASE HISTORICA.xlsx"

    if not principal.exists():
        raise FileNotFoundError(f"No se encontró el archivo '{principal.name}' en la carpeta '{datos_dir}'.")

    print(f"Usando archivo: {principal.name}")
    df_limpio = cargar_y_limpiar_datos(str(principal))

    if not df_limpio.empty:
        # Opcional: Guardar el resultado limpio en un nuevo archivo
        resultados_dir = Path("resultados")
        resultados_dir.mkdir(exist_ok=True)
        
        # Ordenar por compañía para facilitar la lectura
        df_limpio = df_limpio.sort_values(by=['compañia']).reset_index(drop=True)
        
        ruta_salida = resultados_dir / "datos_limpios.csv"
        df_limpio.to_csv(ruta_salida, index=False)
        print(f"\nDatos limpios guardados en: {ruta_salida}")