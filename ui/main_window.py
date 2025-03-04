import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QProgressBar, QFileDialog, QMessageBox, QComboBox, QHBoxLayout, QFrame
)
from processors.sep import SEPProcessor
from processors.pie import PIEProcessor
from processors.duplicados import DuplicadosProcessor
from core.workers import ProcessorWorker, DuplicadosWorker

# Configuración de logging
log_path = Path.home() / "AppData" / "Local" / "RemuPro" / "logs" if sys.platform == 'win32' else Path('.')
log_path.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path / 'proceso_remuneraciones.log'),
        logging.StreamHandler()
    ]
)

class ExcelProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RemuPro | v1.0")
        self.resize(700, 600)
        
        # Variables para SEP/PIE
        self.input_path = None
        self.output_path = None
        self.worker = None
        
        # Variables para Duplicados
        self.input_dup1 = None
        self.input_dup2 = None
        self.output_dup = None
        self.worker_dup = None
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # --- Sección de SEP/PIE  ---
        modo_layout = QHBoxLayout()
        lbl_modo = QLabel("Modo de procesamiento:")
        self.combo_modo = QComboBox()
        self.combo_modo.addItems(["SEP", "PIE-NORMAL"])
        modo_layout.addWidget(lbl_modo)
        modo_layout.addWidget(self.combo_modo)
        layout.addLayout(modo_layout)
        
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
        
        # --- Separador visual ---
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador)
        
        # --- Botón para mostrar/ocultar opciones de Duplicados ---
        self.btn_toggle_dup = QPushButton("Mostrar Opciones Duplicados")
        self.btn_toggle_dup.setCheckable(True)
        self.btn_toggle_dup.toggled.connect(self.toggle_dup_options)
        layout.addWidget(self.btn_toggle_dup)
        
        # --- Contenedor para opciones de Duplicados (inicialmente oculto) ---
        self.dup_frame = QFrame()
        dup_layout = QVBoxLayout()
        
        self.label_input_dup1 = QLabel("Archivo Duplicados 1: No seleccionado")
        self.btn_select_input_dup1 = QPushButton("Seleccionar Archivo Duplicados 1")
        self.btn_select_input_dup1.clicked.connect(self.select_input_dup1)
        
        self.label_input_dup2 = QLabel("Archivo Duplicados 2: No seleccionado")
        self.btn_select_input_dup2 = QPushButton("Seleccionar Archivo Duplicados 2")
        self.btn_select_input_dup2.clicked.connect(self.select_input_dup2)
        
        self.label_output_dup = QLabel("Guardar resultado duplicados en: No seleccionado")
        self.btn_select_output_dup = QPushButton("Seleccionar destino duplicados")
        self.btn_select_output_dup.clicked.connect(self.select_output_dup)
        
        self.btn_start_dup = QPushButton("Procesar Duplicados")
        self.btn_start_dup.clicked.connect(self.start_duplicados_process)
        self.btn_start_dup.setEnabled(False)
        
        # Agregar controles de Duplicados al layout del contenedor
        dup_layout.addWidget(self.label_input_dup1)
        dup_layout.addWidget(self.btn_select_input_dup1)
        dup_layout.addWidget(self.label_input_dup2)
        dup_layout.addWidget(self.btn_select_input_dup2)
        dup_layout.addWidget(self.label_output_dup)
        dup_layout.addWidget(self.btn_select_output_dup)
        dup_layout.addWidget(self.btn_start_dup)
        
        self.dup_frame.setLayout(dup_layout)
        self.dup_frame.hide()  # Ocultar por defecto
        layout.addWidget(self.dup_frame)
        
        self.setLayout(layout)
    
    def toggle_dup_options(self, checked):
        if checked:
            self.dup_frame.show()
            self.btn_toggle_dup.setText("Ocultar Opciones Duplicados")
        else:
            self.dup_frame.hide()
            self.btn_toggle_dup.setText("Mostrar Opciones Duplicados")
    
    # Métodos para SEP/PIE
    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo Excel", str(Path.home()),
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.input_path = Path(file_path)
            self.label_input.setText(f"Archivo Excel de entrada: {self.input_path}")
            self.output_path = None
            self.label_output.setText("Guardar archivo en: No seleccionado")
            self.check_enable_start()
    
    def select_output_file(self):
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
        self.btn_start.setEnabled(bool(self.input_path and self.output_path))
    
    def start_process(self):
        if not self.input_path or not self.output_path:
            QMessageBox.warning(self, "Error", "Debe seleccionar archivo de entrada y destino.")
            return
        
        self.btn_start.setEnabled(False)
        self.btn_select_input.setEnabled(False)
        self.btn_select_output.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Iniciando proceso...")
        
        modo = self.combo_modo.currentText()
        if modo == "SEP":
            processor = SEPProcessor()
        elif modo == "PIE-NORMAL":
            processor = PIEProcessor()
        else:
            QMessageBox.critical(self, "Error", "Modo de procesamiento no reconocido.")
            self.reset_ui()
            return
        
        self.worker = ProcessorWorker(processor, self.input_path, self.output_path)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(self.process_finished)
        self.worker.error_signal.connect(self.process_error)
        self.worker.start()
    
    # Métodos para Duplicados
    def select_input_dup1(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Archivo Duplicados 1", str(Path.home()),
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.input_dup1 = Path(file_path)
            self.label_input_dup1.setText(f"Archivo Duplicados 1: {self.input_dup1}")
            self.check_enable_dup_start()
    
    def select_input_dup2(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Archivo Duplicados 2", str(Path.home()),
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.input_dup2 = Path(file_path)
            self.label_input_dup2.setText(f"Archivo Duplicados 2: {self.input_dup2}")
            self.check_enable_dup_start()
    
    def select_output_dup(self):
        default_name = "resultado_duplicados.xlsx"
        if self.input_dup1:
            default_name = f"{self.input_dup1.stem}_duplicados.xlsx"
        default_dir = Path.home() / "Downloads"
        default_path = str(default_dir / default_name)
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar resultado duplicados", default_path,
            "Excel Files (*.xlsx)"
        )
        if file_path:
            self.output_dup = Path(file_path)
            self.label_output_dup.setText(f"Guardar resultado duplicados en: {self.output_dup}")
            self.check_enable_dup_start()
    
    def check_enable_dup_start(self):
        self.btn_start_dup.setEnabled(bool(self.input_dup1 and self.input_dup2 and self.output_dup))
    
    def start_duplicados_process(self):
        if not (self.input_dup1 and self.input_dup2 and self.output_dup):
            QMessageBox.warning(self, "Error", "Debe seleccionar ambos archivos de entrada y un destino.")
            return
        
        self.btn_start_dup.setEnabled(False)
        self.btn_select_input_dup1.setEnabled(False)
        self.btn_select_input_dup2.setEnabled(False)
        self.btn_select_output_dup.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Iniciando proceso de duplicados...")
        
        processor = DuplicadosProcessor()
        self.worker_dup = DuplicadosWorker(processor, self.input_dup1, self.input_dup2, self.output_dup)
        self.worker_dup.progress_signal.connect(self.update_progress)
        self.worker_dup.finished_signal.connect(self.process_finished_dup)
        self.worker_dup.error_signal.connect(self.process_error)
        self.worker_dup.start()
    
    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def process_finished(self, output_path_str):
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
    
    def process_finished_dup(self, output_path_str):
        reply = QMessageBox.question(
            self,
            "Proceso de Duplicados completado",
            f"Proceso completado. Archivo guardado en:\n{output_path_str}\n\n¿Desea procesar otro archivo?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.reset_ui()
        else:
            self.close()
    
    def process_error(self, error_msg):
        QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{error_msg}")
        self.reset_ui()
    
    def reset_ui(self):
        # Reinicia controles para SEP/PIE
        self.input_path = None
        self.output_path = None
        self.label_input.setText("Archivo Excel de entrada: No seleccionado")
        self.label_output.setText("Guardar archivo en: No seleccionado")
        self.btn_start.setEnabled(False)
        self.btn_select_input.setEnabled(True)
        self.btn_select_output.setEnabled(True)
        
        # Reinicia controles para Duplicados
        self.input_dup1 = None
        self.input_dup2 = None
        self.output_dup = None
        self.label_input_dup1.setText("Archivo Duplicados 1: No seleccionado")
        self.label_input_dup2.setText("Archivo Duplicados 2: No seleccionado")
        self.label_output_dup.setText("Guardar resultado duplicados en: No seleccionado")
        self.btn_start_dup.setEnabled(False)
        self.btn_select_input_dup1.setEnabled(True)
        self.btn_select_input_dup2.setEnabled(True)
        self.btn_select_output_dup.setEnabled(True)
        
        self.status_label.setText("Esperando acción...")
        self.progress_bar.setValue(0)

def main():
    # Configuración de DPI para Windows (evita problemas de escalado en pantallas de alta resolución)
    if sys.platform == 'win32':
        import ctypes
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception as e:
            logging.warning(f"No se pudo configurar DPI en Windows: {str(e)}")
    
    app = QApplication(sys.argv)
    window = ExcelProcessorApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
