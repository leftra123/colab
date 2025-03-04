import sys
from PyQt5.QtCore import QThread, pyqtSignal
from pathlib import Path

class ProcessorWorker(QThread):
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, processor, input_path: Path, output_path: Path):
        super().__init__()
        self.processor = processor
        self.input_path = input_path
        self.output_path = output_path
    
    def run(self):
        try:
            self.processor.process_file(self.input_path, self.output_path, self.progress_callback)
            self.finished_signal.emit(str(self.output_path))
        except PermissionError as e:
            # Mensaje específico para errores de permisos en Windows
            if sys.platform == 'win32':
                error_msg = f"Error de permisos: El archivo podría estar abierto en Excel.\n{str(e)}"
            else:
                error_msg = f"Error de permisos: {str(e)}"
            self.error_signal.emit(error_msg)
        except Exception as e:
            self.error_signal.emit(str(e))
    
    def progress_callback(self, value, message):
        self.progress_signal.emit(value, message)

class DuplicadosWorker(QThread):
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, processor, input_path1: Path, input_path2: Path, output_path: Path):
        super().__init__()
        self.processor = processor
        self.input_path1 = input_path1
        self.input_path2 = input_path2
        self.output_path = output_path
    
    def run(self):
        try:
            self.processor.process_file(self.input_path1, self.input_path2, self.output_path, self.progress_callback)
            self.finished_signal.emit(str(self.output_path))
        except PermissionError as e:
            # Mensaje específico para errores de permisos en Windows
            if sys.platform == 'win32':
                error_msg = f"Error de permisos: Uno de los archivos podría estar abierto en Excel.\n{str(e)}"
            else:
                error_msg = f"Error de permisos: {str(e)}"
            self.error_signal.emit(error_msg)
        except Exception as e:
            self.error_signal.emit(str(e))
    
    def progress_callback(self, value, message):
        self.progress_signal.emit(value, message)