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
        except Exception as e:
            self.error_signal.emit(str(e))
    
    def progress_callback(self, value, message):
        self.progress_signal.emit(value, message)
