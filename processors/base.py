import time
from pathlib import Path
import pandas as pd

class BaseProcessor:
    """Clase base para procesadores de remuneraciones."""
    
    def validate_file(self, file_path: Path) -> None:
        """Realiza validaciones básicas del archivo."""
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        if file_path.suffix.lower() not in ('.xlsx', '.xls'):
            raise ValueError("Formato de archivo no válido")
        if file_path.stat().st_size == 0:
            raise ValueError("El archivo está vacío")
    
    def verify_file(self, file_path: Path):
        """Alias de validación de archivo."""
        self.validate_file(file_path)
    
    def safe_save(self, data: pd.DataFrame, output_path: Path) -> None:
        """Guarda el archivo con reintentos en caso de error de permisos."""
        for attempt in range(3):
            try:
                data.to_excel(str(output_path), index=False, engine='openpyxl')
                return
            except PermissionError:
                if attempt == 2:
                    raise
                time.sleep(1)
