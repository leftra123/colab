#!/usr/bin/env python3
"""
Procesador de Remuneraciones SEP

Esta aplicación gráfica permite seleccionar un archivo Excel con hojas 'HORAS' y 'TOTAL',
procesarlo y guardar los resultados en un nuevo archivo Excel. Además, sugiere automáticamente
un nombre para el archivo de salida y, al finalizar, pregunta si se desea procesar otro archivo.

Requiere: pandas, numpy, openpyxl, PyQt5
"""

import sys
import os
import time
import logging
from pathlib import Path

import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QProgressBar, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('proceso_remuneraciones.log'),
        logging.StreamHandler()
    ]
)


class ExcelProcessor:
    """Clase que procesa el archivo Excel con remuneraciones SEP."""

    def process_file(self, file_path: Path, output_path: Path, progress_callback):
        """Realiza el procesamiento completo del archivo."""
        try:
            progress_callback(0, "Iniciando proceso...")
            df_horas, df_total = self.load_data_with_retry(file_path)
            progress_callback(20, "Datos cargados, procesando...")
            processed_data = self.process_data(df_horas, df_total)
            progress_callback(70, "Guardando resultados...")
            self.save_file(processed_data, output_path)
            progress_callback(100, "Proceso completado!")
        except Exception as e:
            logging.error(f"Error en process_file: {str(e)}", exc_info=True)
            raise

    def load_data_with_retry(self, file_path: Path, max_retries=3, delay=2):
        """Intenta cargar el archivo Excel con varios reintentos ante errores de permiso."""
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
        """Carga y valida las hojas 'HORAS' y 'TOTAL' del archivo Excel."""
        self.verify_file(file_path)
        # Leer hojas específicas del Excel
        df_horas = pd.read_excel(str(file_path), sheet_name='HORAS', engine='openpyxl')
        df_total = pd.read_excel(str(file_path), sheet_name='TOTAL', engine='openpyxl')
        # Validar estructura básica
        required_columns = {
            'HORAS': ['Rut', 'Nombre', 'SEP'],
            'TOTAL': ['Rut']
        }
        self.validate_columns(df_horas, required_columns['HORAS'], 'HORAS')
        self.validate_columns(df_total, required_columns['TOTAL'], 'TOTAL')
        return df_horas, df_total

    def validate_columns(self, df, required_columns, sheet_name):
        """Verifica que el DataFrame contenga las columnas necesarias."""
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            error_msg = f"Hoja {sheet_name} falta(n) columna(s): {', '.join(missing)}"
            logging.error(error_msg)
            raise ValueError(error_msg)

    def verify_file(self, file_path: Path):
        """Verifica que el archivo exista, tenga un tamaño mayor a cero y el formato adecuado."""
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        if file_path.suffix.lower() not in ('.xlsx', '.xls'):
            raise ValueError("Formato de archivo no válido. Debe ser .xlsx o .xls")
        if file_path.stat().st_size == 0:
            raise ValueError("El archivo está vacío")

    def process_data(self, df_horas, df_total):
        """Realiza el procesamiento de datos combinando y calculando columnas."""
        try:
            # Ajuste de nombres y generación de IDs
            df_total = df_total.rename(columns={'rut': 'Rut'})
            df_horas['ID_Horas'] = df_horas.index
            df_total['ID_Total'] = df_total.index
            # Calcular total de horas y filtrar registros sin horas
            df_horas['TOTAL HORAS'] = df_horas['SEP']
            df_horas = df_horas[df_horas['TOTAL HORAS'] != 0]
            # Agrupación y suma de horas por docente
            horas_agrupadas = df_horas.groupby(['Rut', 'Nombre'])['SEP'].sum().reset_index()
            horas_agrupadas['TOTAL HORAS'] = horas_agrupadas['SEP']
            df_horas = df_horas.merge(
                horas_agrupadas[['Rut', 'Nombre', 'TOTAL HORAS']],
                on=['Rut', 'Nombre'],
                how='left',
                suffixes=('', '_SUMA')
            )
            # Renombrado y limpieza de columnas
            df_horas = df_horas.rename(columns={'TOTAL HORAS_SUMA': 'TOTAL HORAS POR DOCENTE'})
            df_horas = df_horas.drop('TOTAL HORAS', axis=1, errors='ignore')
            # Combinación de datos de ambas hojas
            datos_combinados = pd.merge(
                df_total,
                df_horas,
                on=['Rut'],
                how='left'
            )
            # Manejo de valores nulos
            fill_values = {'SEP': 0, 'TOTAL HORAS POR DOCENTE': 0}
            datos_combinados = datos_combinados.fillna(fill_values)
            # Cálculos de salarios
            columnas_salarios = self.get_salary_columns(datos_combinados)
            datos_combinados = self.calculate_salaries(datos_combinados, columnas_salarios)
            # Validación final de horas
            self.validate_hours(datos_combinados)
            return datos_combinados
        except Exception as e:
            logging.error(f"Error en process_data: {str(e)}")
            raise

    def get_salary_columns(self, df):
        """Retorna la lista de columnas salariales presentes en el DataFrame."""
        predefined_columns = [
            'SUELDO BASE', 'RBMN (SUELDO BASE)', 'ASIGNACION EXPERIENCIA', 'Antic SEG.INV.SOB.', 'SEG.CESANTIA EMP.', 'MUTUAL',
            'ASIGNACION RESPONSABILIDAD', 'CONDICION DIFICIL', 'COMPLEMENTO DE ZONA', '(BRP) Asig. Titulo y M',
            'PROF. ENCARGADO LEY.', 'HORAS EXTRAS RETROACT.', 'ASIGNACION ESPECIAL', 'ASIG.RESP. UTP', 'HORAS EXTRAS DEM',
            'RETRO.FAMILIAR', 'BONO VACACIONES', 'PAGO RETROACTIVO', 'LEY 19464/96', 'BRP RETROAC/REEMPL.',
            'BONIFICACION ESPECIAL', 'INCENTIVO (P.I.E)', 'EXCELENCIA ACADEMICA', 'ASIG. TITULO ESPECIAL',
            'DEVOLUCION DESCUENTO', 'RETROBONO INCENTIVO', 'ASIG. FAMILIAR CORR.', 'BONO CUMPLIMIENTO METAS',
            'ASIG.DIRECTOR.LEY 20501', 'RESP. INSPECTOR GENERAL', 'COND.DIFICIL.ASIST.EDUCACIÓN', 'ASIGNACION LEY 20.501/2011 DIR',
            'RETROACTIVO BIENIOS', 'RETROACTIVO PROFESOR ENCARGADO', 'ASIG.RESPONS. 6HRS', 'RETROCT.ALS.PRIORIT.ASIST.EDUC',
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
        """Calcula las columnas salariales en función de la proporción de horas."""
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
        """Valida que las horas de cada docente no excedan el límite permitido (44 horas)."""
        try:
            df['HORAS_VALIDAS'] = df['TOTAL HORAS POR DOCENTE'] <= 44
            problematicos = df[~df['HORAS_VALIDAS']]
            if not problematicos.empty:
                msg = f"{len(problematicos)} docentes exceden las 44 horas. Verifique el log para detalles."
                logging.warning(msg)
                for _, row in problematicos.iterrows():
                    logging.warning(f"{row['Nombre']} (RUT: {row['Rut']}) - {row['TOTAL HORAS POR DOCENTE']} horas")
        except Exception as e:
            logging.error(f"Error en validate_hours: {str(e)}")
            raise

    def save_file(self, data, output_path: Path):
        """Guarda el DataFrame procesado en un archivo Excel, con reintentos ante errores de permiso."""
        for attempt in range(3):
            try:
                data.to_excel(str(output_path), index=False, engine='openpyxl')
                return
            except PermissionError:
                if attempt == 2:
                    raise
                time.sleep(1)


class Worker(QThread):
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, input_path: Path, output_path: Path):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.processor = ExcelProcessor()
    
    def run(self):
        try:
            self.processor.process_file(self.input_path, self.output_path, self.progress_callback)
            self.finished_signal.emit(str(self.output_path))
        except Exception as e:
            self.error_signal.emit(str(e))
    
    def progress_callback(self, value, message):
        self.progress_signal.emit(value, message)


class ExcelProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procesador de Remuneraciones SEP")
        self.resize(600, 400)
        
        self.input_path: Path = None
        self.output_path: Path = None
        self.worker = None
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.label_input = QLabel("Archivo Excel de entrada: No seleccionado")
        self.btn_select_input = QPushButton("Seleccionar Archivo Excel")
        self.btn_select_input.clicked.connect(self.select_input_file)
        
        self.label_output = QLabel("Guardar archivo en: No seleccionado")
        self.btn_select_output = QPushButton("Seleccionar destino")
        self.btn_select_output.clicked.connect(self.select_output_file)
        
        self.btn_start = QPushButton("Iniciar Proceso")
        self.btn_start.clicked.connect(self.start_process)
        self.btn_start.setEnabled(False)
        
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Esperando acción...")
        
        layout.addWidget(self.label_input)
        layout.addWidget(self.btn_select_input)
        layout.addWidget(self.label_output)
        layout.addWidget(self.btn_select_output)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def select_input_file(self):
        """Permite al usuario seleccionar el archivo Excel de entrada."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo Excel", str(Path.home()),
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.input_path = Path(file_path)
            self.label_input.setText(f"Archivo Excel de entrada: {self.input_path}")
            # Al cambiar el archivo de entrada se limpia la ruta de salida
            self.output_path = None
            self.label_output.setText("Guardar archivo en: No seleccionado")
            self.check_enable_start()
    
    def select_output_file(self):
        """Permite al usuario seleccionar o sugerir un destino para el archivo procesado."""
        # Sugerir un nombre basado en el archivo de entrada y usando la carpeta Descargas
        default_name = "procesado.xlsx"
        if self.input_path:
            default_name = f"{self.input_path.stem}_procesado.xlsx"
        default_dir = Path.home() / "Downloads"
        default_path = str(default_dir / default_name)
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo procesado", default_path,
            "Excel Files (*.xlsx)"
        )
        if file_path:
            self.output_path = Path(file_path)
            self.label_output.setText(f"Guardar archivo en: {self.output_path}")
            self.check_enable_start()
    
    def check_enable_start(self):
        """Habilita el botón de inicio si se han seleccionado archivo de entrada y salida."""
        if self.input_path and self.output_path:
            self.btn_start.setEnabled(True)
        else:
            self.btn_start.setEnabled(False)
    
    def start_process(self):
        """Inicia el proceso de procesamiento en un hilo separado."""
        if not self.input_path or not self.output_path:
            QMessageBox.warning(self, "Error", "Debe seleccionar archivo de entrada y destino.")
            return
        
        self.btn_start.setEnabled(False)
        self.btn_select_input.setEnabled(False)
        self.btn_select_output.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Iniciando proceso...")
        
        self.worker = Worker(self.input_path, self.output_path)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(self.process_finished)
        self.worker.error_signal.connect(self.process_error)
        self.worker.start()
    
    def update_progress(self, value, message):
        """Actualiza la barra de progreso y el estado en la interfaz."""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def process_finished(self, output_path_str):
        """Al finalizar el proceso, pregunta si se desea procesar otro archivo."""
        reply = QMessageBox.question(
            self,
            "Proceso completado",
            f"Proceso completado. Archivo guardado en:\n{output_path_str}\n\n¿Desea procesar otro archivo?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.reset_ui()
        else:
            self.close()
    
    def process_error(self, error_msg):
        """Muestra un mensaje de error en caso de que ocurra algún fallo durante el procesamiento."""
        QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{error_msg}")
        self.reset_ui()
    
    def reset_ui(self):
        """Reinicia la interfaz para procesar otro archivo."""
        self.input_path = None
        self.output_path = None
        self.label_input.setText("Archivo Excel de entrada: No seleccionado")
        self.label_output.setText("Guardar archivo en: No seleccionado")
        self.btn_start.setEnabled(False)
        self.btn_select_input.setEnabled(True)
        self.btn_select_output.setEnabled(True)
        self.status_label.setText("Esperando acción...")
        self.progress_bar.setValue(0)


def main():
    app = QApplication(sys.argv)
    window = ExcelProcessorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
