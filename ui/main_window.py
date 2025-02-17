import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QProgressBar, QFileDialog, QMessageBox, QComboBox, QHBoxLayout
)
from processors.sep import SEPProcessor
from processors.pie import PIEProcessor
from core.workers import ProcessorWorker

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('proceso_remuneraciones.log'),
        logging.StreamHandler()
    ]
)

class ExcelProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RemuPro | v1.0")
        self.resize(650, 450)
        
        self.input_path: Path = None
        self.output_path: Path = None
        self.worker = None
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Selector de modo de procesamiento
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
        
        self.setLayout(layout)
    
    def select_input_file(self):
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
        
        # Deshabilitar controles durante el proceso
        self.btn_start.setEnabled(False)
        self.btn_select_input.setEnabled(False)
        self.btn_select_output.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Iniciando proceso...")
        
        # Seleccionar el procesador según el modo elegido
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
    
    def process_error(self, error_msg):
        QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{error_msg}")
        self.reset_ui()
    
    def reset_ui(self):
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
