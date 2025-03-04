import sys
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
            
            # Verificar archivos de entrada
            self.verify_file(input_path1)
            self.verify_file(input_path2)
            
            # Intentar cargar los archivos con manejo de errores
            try:
                df = pd.read_excel(str(input_path1), sheet_name='Hoja1', engine='openpyxl')
            except PermissionError:
                if sys.platform == 'win32':
                    raise PermissionError("El primer archivo está siendo utilizado por otro programa. Ciérrelo e intente nuevamente.")
                else:
                    raise PermissionError("Error de permisos al acceder al primer archivo.")
            except Exception as e:
                raise ValueError(f"Error al leer el primer archivo: {str(e)}")
            
            # Si se requiere utilizar el segundo archivo, se puede cargar y usar sus datos.
            progress_callback(20, "Cargando segundo archivo...")
            try:
                df_extra = pd.read_excel(str(input_path2), sheet_name='Hoja1', engine='openpyxl')
            except PermissionError:
                if sys.platform == 'win32':
                    raise PermissionError("El segundo archivo está siendo utilizado por otro programa. Ciérrelo e intente nuevamente.")
                else:
                    raise PermissionError("Error de permisos al acceder al segundo archivo.")
            except Exception as e:
                raise ValueError(f"Error al leer el segundo archivo: {str(e)}")
            
            # Aquí podrías, por ejemplo, usar información de df_extra para algún cruce
            # En este ejemplo simplemente se continua con el procesamiento en df
            
            progress_callback(30, "Detectando duplicados...")
            
            # Verificar que exista la columna 'DUPLICADOS'
            if 'DUPLICADOS' not in df.columns:
                raise ValueError("La columna 'DUPLICADOS' no existe en el archivo. Verifique la estructura del archivo.")
            
            # Determinar las filas duplicadas basadas en la columna 'DUPLICADOS'
            duplicados = df.duplicated(subset=['DUPLICADOS'], keep=False)
            df_duplicados = df[duplicados]
            
            # Verificar si hay duplicados
            if df_duplicados.empty:
                logging.info("No se encontraron registros duplicados")
                progress_callback(40, "No se encontraron duplicados, preparando archivo...")
            else:
                num_duplicados = len(df_duplicados)
                logging.info(f"Se encontraron {num_duplicados} registros duplicados")
                progress_callback(40, f"Calculando suma de columnas para {num_duplicados} duplicados...")
                
                # Asumimos que las columnas de interés a sumar son desde la 17ª columna en adelante
                # Verificar que haya suficientes columnas
                if len(df.columns) < 17:
                    logging.warning("El archivo tiene menos de 17 columnas, se usarán todas las columnas numéricas")
                    columnas_suma = df.select_dtypes(include=['number']).columns.tolist()
                    if 'DUPLICADOS' in columnas_suma:
                        columnas_suma.remove('DUPLICADOS')
                else:
                    columnas_suma = df.columns[16:]
                
                # Agrupar y sumar
                try:
                    df_suma = df_duplicados.groupby('DUPLICADOS')[columnas_suma].sum().reset_index()
                except Exception as e:
                    logging.error(f"Error al agrupar duplicados: {str(e)}")
                    raise ValueError(f"Error al procesar duplicados: {str(e)}")

                progress_callback(50, "Actualizando registros duplicados...")
                # Actualizar cada grupo de duplicados con la suma correspondiente
                for _, row in df_suma.iterrows():
                    df.loc[df['DUPLICADOS'] == row['DUPLICADOS'], columnas_suma] = row[columnas_suma].values

                progress_callback(60, "Eliminando duplicados adicionales...")
                # Eliminar las filas duplicadas dejando solo la primera aparición
                num_antes = len(df)
                df.drop_duplicates(subset=['DUPLICADOS'], keep='first', inplace=True)
                num_despues = len(df)
                logging.info(f"Se eliminaron {num_antes - num_despues} filas duplicadas")

            progress_callback(70, "Ordenando datos...")
            # Ordenar el DataFrame según la columna 'DUPLICADOS' (u otro criterio)
            df.sort_values(by='DUPLICADOS', inplace=True)

            progress_callback(80, "Guardando resultado final...")
            # Usar el método safe_save en lugar de to_excel directamente
            self.safe_save(df, output_path)
            
            progress_callback(100, f"Proceso de duplicados completado! Archivo guardado en {output_path}")
            return True
        except Exception as e:
            logging.error(f"Error en DuplicadosProcessor: {str(e)}", exc_info=True)
            raise