[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# RemuPro: Procesador de Remuneraciones  SEP - PIE - NORMAL

**RemuPro** es una aplicación gráfica diseñada para facilitar el procesamiento de archivos Excel con datos de remuneraciones SEP, PIE y NORMAL. Con RemuPro, el usuario puede seleccionar un archivo de entrada, procesarlo y guardar los resultados en un nuevo archivo Excel sin necesidad de interactuar con el código. La aplicación está pensada para ser intuitiva, escalable y modular, permitiendo agregar nuevas funcionalidades en el futuro (por ejemplo, el procesamiento de remuneraciones PIE, NOTRMAL).

## Características

- **Interfaz gráfica intuitiva:**  
  Utiliza PyQt5 para que el usuario seleccione fácilmente el archivo Excel de entrada y defina la ubicación de salida sin necesidad de conocimientos técnicos.

- **Procesamiento robusto de datos:**  
  Lee y valida datos de las hojas `HORAS` y `TOTAL`, realiza cálculos y gestiona reintentos en caso de errores, asegurando un procesamiento fiable.

- **Sugerencia automática de nombre de salida:**  
  Propone un nombre por defecto para el archivo de salida (usando la carpeta `Downloads` de macOS) basado en el nombre del archivo de entrada.

- **Escalabilidad y modularidad:**  
  La estructura del código permite incorporar fácilmente nuevas funcionalidades, como el módulo para remuneraciones PIE, que se encuentra en fase de planificación.


## Requisitos
- Python 3.8+
- Sistema operativo: macOS, Windows o Linux

## Instalación

1. Clonar repositorio:
```bash
git clone https://github.com/leftra123/tu-repositorio.git
cd tu-repositorio
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate    # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso
Ejecutar el script principal:
```bash
python main.py
```

## Características
- Interfaz gráfica amigable
- Validación de datos integrada
- Compatibilidad con Excel
- Sistema de logging para diagnóstico