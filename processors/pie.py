import time
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from processors.base import BaseProcessor

class PIEProcessor(BaseProcessor):
    """Procesador para remuneraciones PIE (NORMAL)."""
    
    def process_file(self, file_path: Path, output_path: Path, progress_callback):
        try:
            progress_callback(0, "Iniciando proceso PIE...")
            progress_callback(5, "Cargando datos para PIE...")
            df_horas = pd.read_excel(
                str(file_path), sheet_name='HORAS',
                usecols=list(range(0, 5)) + list(range(6, 10)),
                engine='openpyxl'
            )
            df_total = pd.read_excel(str(file_path), sheet_name='TOTAL', engine='openpyxl')
            # Copias (si fuera necesario)
            df_horas_copia = df_horas.copy()
            df_total_copia = df_total.copy()
            df_total.rename(columns={'rut': 'Rut'}, inplace=True)
            df_horas['ID_Horas'] = df_horas.index
            df_total['ID_Total'] = df_total.index
            progress_callback(10, "Calculando horas PIE...")
            df_horas['TOTAL HORAS'] = df_horas['PIE'] + df_horas['SN']
            df_horas = df_horas[df_horas['TOTAL HORAS'] != 0]
            horas_agrupadas = df_horas.groupby(['Rut', 'Nombre'])[['PIE', 'SN']].sum().reset_index()
            horas_agrupadas['TOTAL HORAS'] = horas_agrupadas['PIE'] + horas_agrupadas['SN']
            df_horas = df_horas.merge(
                horas_agrupadas[['Rut', 'Nombre', 'TOTAL HORAS']],
                on=['Rut', 'Nombre'],
                how='left',
                suffixes=('', '_SUMA')
            )
            df_horas.rename(columns={'TOTAL HORAS_SUMA': 'TOTAL HORAS POR DOCENTE'}, inplace=True)
            df_horas.drop('TOTAL HORAS', axis=1, inplace=True)
            progress_callback(30, "Combinando datos PIE...")
            datos_combinados = pd.merge(df_total, df_horas, on=['Rut'], how='left')
            datos_combinados.fillna({'PIE': 0, 'SN': 0, 'TOTAL HORAS POR DOCENTE': 0}, inplace=True)
            for col in ['ID_Horas', 'ID_Total']:
                if col in datos_combinados.columns:
                    datos_combinados.drop(col, axis=1, inplace=True)
            progress_callback(50, "Calculando salarios y beneficios PIE...")
            columnas_especiales = [
                'SUELDO BASE', 'RBMN (SUELDO BASE)', 'ASIGNACION EXPERIENCIA',
                'Antic SEG.INV.SOB.', 'SEG.CESANTIA EMP.', 'MUTUAL'
            ]
            for columna in columnas_especiales:
                if columna in datos_combinados.columns:
                    valor_por_hora = datos_combinados[columna] / datos_combinados['TOTAL HORAS POR DOCENTE']
                    valor_por_hora.replace([np.inf, -np.inf, np.nan], 0, inplace=True)
                    datos_combinados[f'{columna} PIE'] = (valor_por_hora * datos_combinados['PIE']).round().fillna(0).astype(int)
                    datos_combinados[f'{columna} SN'] = (valor_por_hora * datos_combinados['SN']).round().fillna(0).astype(int)
            columnas_salarios_beneficios = [
                'ASIGNACION RESPONSABILIDAD', 'CONDICION DIFICIL',
                'COMPLEMENTO DE ZONA', '(BRP) Asig. Titulo y M', 'PROF. ENCARGADO LEY.',
                'HORAS EXTRAS RETROACT.', 'ASIGNACION ESPECIAL', 'ASIG.RESP. UTP',
                'HORAS EXTRAS DEM', 'RETRO.FAMILIAR', 'BONO VACACIONES', 'PAGO RETROACTIVO',
                'LEY 19464/96', 'BRP RETROAC/REEMPL.', 'BONIFICACION ESPECIAL',
                'INCENTIVO (P.I.E)', 'EXCELENCIA ACADEMICA', 'ASIG. TITULO ESPECIAL',
                'DEVOLUCION DESCUENTO', 'RETROBONO INCENTIVO', 'ASIG. FAMILIAR CORR.',
                'BONO CUMPLIMIENTO METAS', 'ASIG.DIRECTOR.LEY 20501', 'RESP. INSPECTOR GENERAL',
                'COND.DIFICIL.ASIST.EDUCACIÓN', 'ASIGNACION LEY 20.501/2011 DIR',
                'RETROACTIVO BIENIOS', 'RETROACTIVO PROFESOR ENCARGADO', 'ASIG.RESPONS. 6HRS',
                'RETROCT.ALS.PRIORIT.ASIST.EDUC', 'ART.59 LEY 20.883BONO ASISTEDU',
                'RETROACT.ASIGN.RESPOS.DIRECTIV', 'ALS PRIORIT.ASIST.EDUC.AÑO2022',
                'LEY 21.405 ART.44  ASISTE.EDUC', 'ASIGNACION INDUCCION CPEIP', 'AJUSTE BONO LEY 20.883ART59  A',
                'RESTITUCION LICEN.MEDICA', 'ART.42 LEY 21.526 ASIST.EDUC', 'ALUMNOS. PRIORITARIOS ASIS. DE',
                'ASIG.Por Tramo de Desarrollo P', 'Rec. Doc. Establ. Als Priorita',
                'Planilla Suplementaria', 'ART.5°TRANS. LEY20.903', '  TOTAL HABERES',
                '  IMPOSICIONES antic', '  SALUD', '  Imposicion Voluntaria', '  MONTO IMPONIBLE',
                '  MONTO IMP.DESAHUCIO', '  IMPUESTO UNICO', '  MONTO TRIBUTABLE',
                '  DIA NO TRABAJADO', '  RET. JUDICIAL', '  A.P.V', '  SEGURO DE CESANTIA',
                '  HDI CIA. DE SEGUROS', '  HDI CONDUCTORES', '  AGRUPACION CODOCENTE',
                '  TEMUCOOP (COOPERATIVA DE AHO', '  COOPAHOCRED.KUMEMOGEN LTDA',
                '  CRED. COOPEUCH BIENESTAR', '  PRESTAMO/ACCIONES- COOPEUCH',
                '  MUTUAL DE SEGUROS DE CHILE', '  1% PROFESORES DE RELIGION',
                '  CUOTA BIENESTAR 1%', '  CHILENA CONSOLIDADA - SEGURO', '  ATRASOS',
                '  VIDA SECURITY - SEGUROS DE V', '  BIENESTAR CUOTA INCORP. CUO',
                '  REINTEGRO', '  CAJA LOS ANDES - SEGUROS Y P', '  CAJA LOS ANDES - AHORRO',
                '  COLEGIO PROFESORES 1%', '  APORTE SEG. INV. SOB.', '  REINTEGRO BIENIO',
                '  1% ASOC.AGFAE', '  AHORRO AFP', '  RETENCION POR LICEN. MEDICA',
                '  BONO DOCENTE', '  SEGURO DE CESANTIA', '  SEGURO FALP',
                '  COLEGIO PROFESORES 1% HABER', '  Ajuste IMPOSICIONES'
            ]
            datos_combinados['SUMA POR FILA'] = datos_combinados['PIE'] + datos_combinados['SN']
            for columna in columnas_salarios_beneficios:
                if columna not in datos_combinados:
                    logging.warning(f"Aviso: La columna {columna} no está en los datos combinados.")
                    continue
                valor_por_hora = datos_combinados[columna] / datos_combinados['TOTAL HORAS POR DOCENTE']
                valor_por_hora.replace([np.inf, -np.inf, np.nan], 0, inplace=True)
                datos_combinados[f'{columna}_nuevo'] = (valor_por_hora * datos_combinados['SUMA POR FILA']).round().fillna(0).astype(int)
            progress_callback(70, "Ajustes finales PIE...")
            datos_combinados.fillna(0, inplace=True)
            datos_combinados.replace([np.inf, -np.inf], 0, inplace=True)
            datos_combinados.sort_values(['Rut', 'Nombre'], inplace=True)
            docentes_con_exceso = False
            for index, row in datos_combinados.iterrows():
                if row['TOTAL HORAS POR DOCENTE'] > 44:
                    logging.warning(f"Alerta: El docente {row['Nombre']} (RUT: {row['Rut']}) tiene {row['TOTAL HORAS POR DOCENTE']} horas, excede 44.")
                    docentes_con_exceso = True
            if not docentes_con_exceso:
                logging.info("No se encontró personal que supere las 44 horas totales")
            progress_callback(90, "Exportando datos PIE...")
            datos_combinados.to_excel(str(output_path), index=False, engine='openpyxl')
            progress_callback(100, "Proceso PIE completado!")
        except Exception as e:
            logging.error(f"Error en PIE process_file: {str(e)}", exc_info=True)
            raise
