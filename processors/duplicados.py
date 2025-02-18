import time
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from processors.base import BaseProcessor

class DuplicadosProcessor(BaseProcessor):
    """
    Procesador para consolidar registros duplicados.
    Este processor utiliza dos archivos de entrada (por ejemplo, uno principal y
    otro complementario, aunque en este ejemplo se procesa únicamente el primero).
    """
    def process_file(self, input_path1: Path, input_path2: Path, output_path: Path, progress_callback):
        try:
            progress_callback(0, "Iniciando proceso de duplicados...")
            # Cargar el primer archivo (por ejemplo, el consolidado principal)
            progress_callback(10, "Cargando primer archivo...")
            df = pd.read_excel(str(input_path1), sheet_name='Hoja1', engine='openpyxl')
            
            # Si se requiere utilizar el segundo archivo, se puede cargar y usar sus datos.
            progress_callback(20, "Cargando segundo archivo...")
            df_extra = pd.read_excel(str(input_path2), sheet_name='Hoja1', engine='openpyxl')
            # Aquí podrías, por ejemplo, usar información de df_extra para algún cruce
            # En este ejemplo simplemente se continua con el procesamiento en df
            
            progress_callback(30, "Detectando duplicados...")
            # Determinar las filas duplicadas basadas en la columna 'DUPLICADOS'
            duplicados = df.duplicated(subset=['DUPLICADOS'], keep=False)
            df_duplicados = df[duplicados]

            progress_callback(40, "Calculando suma de columnas para duplicados...")
            # Asumimos que las columnas de interés a sumar son desde la 17ª columna en adelante
            columnas_suma = df.columns[16:]
            df_suma = df_duplicados.groupby('DUPLICADOS')[columnas_suma].sum().reset_index()

            progress_callback(50, "Actualizando registros duplicados...")
            # Actualizar cada grupo de duplicados con la suma correspondiente
            for _, row in df_suma.iterrows():
                df.loc[df['DUPLICADOS'] == row['DUPLICADOS'], columnas_suma] = row[columnas_suma].values

            progress_callback(60, "Eliminando duplicados adicionales...")
            # Eliminar las filas duplicadas dejando solo la primera aparición
            df.drop_duplicates(subset=['DUPLICADOS'], keep='first', inplace=True)

            progress_callback(70, "Ordenando datos...")
            # Ordenar el DataFrame según la columna 'DUPLICADOS' (u otro criterio)
            df.sort_values(by='DUPLICADOS', inplace=True)

            progress_callback(80, "Guardando resultado final...")
            # Guardar el DataFrame final en el archivo de salida
            df.to_excel(str(output_path), index=False, engine='openpyxl')
            
            progress_callback(100, "Proceso de duplicados completado!")
        except Exception as e:
            logging.error(f"Error en DuplicadosProcessor: {str(e)}", exc_info=True)
            raise
