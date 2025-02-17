import time
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from processors.base import BaseProcessor

class SEPProcessor(BaseProcessor):
    """Procesador para remuneraciones SEP."""
    
    def process_file(self, file_path: Path, output_path: Path, progress_callback):
        try:
            progress_callback(0, "Iniciando proceso SEP...")
            df_horas, df_total = self.load_data_with_retry(file_path)
            progress_callback(20, "Datos cargados, procesando...")
            processed_data = self.process_data(df_horas, df_total)
            progress_callback(70, "Guardando resultados...")
            self.safe_save(processed_data, output_path)
            progress_callback(100, "Proceso SEP completado!")
        except Exception as e:
            logging.error(f"Error en SEP process_file: {str(e)}", exc_info=True)
            raise

    def load_data_with_retry(self, file_path: Path, max_retries=3, delay=2):
        for attempt in range(max_retries):
            try:
                return self.load_data(file_path)
            except PermissionError:
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay)
                logging.warning(f"Reintento {attempt + 1} para abrir el archivo")
        return None

    def load_data(self, file_path: Path):
        self.verify_file(file_path)
        df_horas = pd.read_excel(str(file_path), sheet_name='HORAS', engine='openpyxl')
        df_total = pd.read_excel(str(file_path), sheet_name='TOTAL', engine='openpyxl')
        required_columns = {
            'HORAS': ['Rut', 'Nombre', 'SEP'],
            'TOTAL': ['Rut']
        }
        self.validate_columns(df_horas, required_columns['HORAS'], 'HORAS')
        self.validate_columns(df_total, required_columns['TOTAL'], 'TOTAL')
        return df_horas, df_total

    def validate_columns(self, df, required_columns, sheet_name):
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            error_msg = f"Hoja {sheet_name} falta(n) columna(s): {', '.join(missing)}"
            logging.error(error_msg)
            raise ValueError(error_msg)

    def process_data(self, df_horas, df_total):
        try:
            df_total = df_total.rename(columns={'rut': 'Rut'})
            df_horas['ID_Horas'] = df_horas.index
            df_total['ID_Total'] = df_total.index
            df_horas['TOTAL HORAS'] = df_horas['SEP']
            df_horas = df_horas[df_horas['TOTAL HORAS'] != 0]
            horas_agrupadas = df_horas.groupby(['Rut', 'Nombre'])['SEP'].sum().reset_index()
            horas_agrupadas['TOTAL HORAS'] = horas_agrupadas['SEP']
            df_horas = df_horas.merge(
                horas_agrupadas[['Rut', 'Nombre', 'TOTAL HORAS']],
                on=['Rut', 'Nombre'],
                how='left',
                suffixes=('', '_SUMA')
            )
            df_horas = df_horas.rename(columns={'TOTAL HORAS_SUMA': 'TOTAL HORAS POR DOCENTE'})
            df_horas = df_horas.drop('TOTAL HORAS', axis=1, errors='ignore')
            datos_combinados = pd.merge(df_total, df_horas, on=['Rut'], how='left')
            fill_values = {'SEP': 0, 'TOTAL HORAS POR DOCENTE': 0}
            datos_combinados = datos_combinados.fillna(fill_values)
            columnas_salarios = self.get_salary_columns(datos_combinados)
            datos_combinados = self.calculate_salaries(datos_combinados, columnas_salarios)
            self.validate_hours(datos_combinados)
            return datos_combinados
        except Exception as e:
            logging.error(f"Error en SEP process_data: {str(e)}")
            raise

    def get_salary_columns(self, df):
        predefined_columns = [
            'SUELDO BASE', 'RBMN (SUELDO BASE)', 'ASIGNACION EXPERIENCIA', 'Antic SEG.INV.SOB.',
            'SEG.CESANTIA EMP.', 'MUTUAL', 'ASIGNACION RESPONSABILIDAD', 'CONDICION DIFICIL',
            'COMPLEMENTO DE ZONA', '(BRP) Asig. Titulo y M', 'PROF. ENCARGADO LEY.',
            'HORAS EXTRAS RETROACT.', 'ASIGNACION ESPECIAL', 'ASIG.RESP. UTP', 'HORAS EXTRAS DEM',
            'RETRO.FAMILIAR', 'BONO VACACIONES', 'PAGO RETROACTIVO', 'LEY 19464/96',
            'BRP RETROAC/REEMPL.', 'BONIFICACION ESPECIAL', 'INCENTIVO (P.I.E)', 'EXCELENCIA ACADEMICA',
            'ASIG. TITULO ESPECIAL', 'DEVOLUCION DESCUENTO', 'RETROBONO INCENTIVO', 'ASIG. FAMILIAR CORR.',
            'BONO CUMPLIMIENTO METAS', 'ASIG.DIRECTOR.LEY 20501', 'RESP. INSPECTOR GENERAL',
            'COND.DIFICIL.ASIST.EDUCACIÓN', 'ASIGNACION LEY 20.501/2011 DIR', 'RETROACTIVO BIENIOS',
            'RETROACTIVO PROFESOR ENCARGADO', 'ASIG.RESPONS. 6HRS', 'RETROCT.ALS.PRIORIT.ASIST.EDUC',
            'ART.59 LEY 20.883BONO ASISTEDU', 'RETROACT.ASIGN.RESPOS.DIRECTIV', 'ALS PRIORIT.ASIST.EDUC.AÑO2022',
            'LEY 21.405 ART.44  ASISTE.EDUC', 'ASIGNACION INDUCCION CPEIP', 'AJUSTE BONO LEY 20.883ART59  A',
            'RESTITUCION LICEN.MEDICA', 'ART.42 LEY 21.526 ASIST.EDUC', 'ALUMNOS. PRIORITARIOS ASIS. DE',
            'ASIG.Por Tramo de Desarrollo P', 'Rec. Doc. Establ. Als Priorita', 'Planilla Suplementaria',
            'ART.5°TRANS. LEY20.903', '  TOTAL HABERES', '  IMPOSICIONES antic', '  SALUD',
            '  Imposicion Voluntaria', '  MONTO IMPONIBLE', '  MONTO IMP.DESAHUCIO', '  IMPUESTO UNICO',
            '  MONTO TRIBUTABLE', '  DIA NO TRABAJADO', '  RET. JUDICIAL', '  A.P.V',
            '  SEGURO DE CESANTIA', '  HDI CIA. DE SEGUROS', '  HDI CONDUCTORES',
            '  AGRUPACION CODOCENTE', '  TEMUCOOP (COOPERATIVA DE AHO', '  COOPAHOCRED.KUMEMOGEN LTDA',
            '  CRED. COOPEUCH BIENESTAR', '  PRESTAMO/ACCIONES- COOPEUCH', '  MUTUAL DE SEGUROS DE CHILE',
            '  1% PROFESORES DE RELIGION', '  CUOTA BIENESTAR 1%', '  CHILENA CONSOLIDADA - SEGURO',
            '  ATRASOS', '  VIDA SECURITY - SEGUROS DE V', '  BIENESTAR CUOTA INCORP. CUO', '  REINTEGRO',
            '  CAJA LOS ANDES - SEGUROS Y P', '  CAJA LOS ANDES - AHORRO', '  COLEGIO PROFESORES 1%',
            '  APORTE SEG. INV. SOB.', '  REINTEGRO BIENIO', '  1% ASOC.AGFAE', '  AHORRO AFP',
            '  RETENCION POR LICEN. MEDICA', '  BONO DOCENTE', '  SEGURO DE CESANTIA', '  SEGURO FALP',
            '  COLEGIO PROFESORES 1% HABER', '  Ajuste IMPOSICIONES'
        ]
        return [col for col in predefined_columns if col in df.columns]

    def calculate_salaries(self, df, columns):
        for col in columns:
            try:
                df[f'{col}_SEP'] = (df[col] / df['TOTAL HORAS POR DOCENTE']).replace(
                    [np.inf, -np.inf, np.nan], 0
                ) * df['SEP']
                df[f'{col}_SEP'] = df[f'{col}_SEP'].round().fillna(0).astype(int)
            except Exception as e:
                logging.warning(f"Error calculando columna {col}: {str(e)}")
        return df

    def validate_hours(self, df):
        try:
            df['HORAS_VALIDAS'] = df['TOTAL HORAS POR DOCENTE'] <= 44
            problematicos = df[~df['HORAS_VALIDAS']]
            if not problematicos.empty:
                logging.warning(f"{len(problematicos)} docentes exceden las 44 horas.")
                for _, row in problematicos.iterrows():
                    logging.warning(f"{row['Nombre']} (RUT: {row['Rut']}) - {row['TOTAL HORAS POR DOCENTE']} horas")
        except Exception as e:
            logging.error(f"Error en validate_hours: {str(e)}")
            raise

    def save_file(self, data, output_path: Path):
        for attempt in range(3):
            try:
                data.to_excel(str(output_path), index=False, engine='openpyxl')
                return
            except PermissionError:
                if attempt == 2:
                    raise
                time.sleep(1)
