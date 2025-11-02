"""
Processor Window - Ventana de procesamiento de remuneraciones
Versión mejorada con estilos modernos
Compatible con Windows y macOS
"""

import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QProgressBar, QFileDialog, QMessageBox, QComboBox,
    QHBoxLayout, QFrame, QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont
from processors.sep import SEPProcessor
from processors.pie import PIEProcessor
from processors.duplicados import DuplicadosProcessor
from core.workers import ProcessorWorker, DuplicadosWorker
from ui.styles import PROCESSOR_WINDOW_STYLE


class ProcessorWindow(QWidget):
    """Ventana de procesamiento con interfaz moderna"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RemuPro - Procesamiento Separado")
        self.resize(900, 700)

        # Variables para SEP/PIE
        self.input_path = None
        self.output_path = None
        self.worker = None

        # Variables para Duplicados
        self.input_dup1 = None
        self.input_dup2 = None
        self.output_dup = None
        self.worker_dup = None

        self.setup_ui()
        self.apply_styles()
        self.fade_in()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)

        # Header con título y botón de volver
        header_layout = QHBoxLayout()

        # Botón de volver
        btn_back = QPushButton("← Volver")
        btn_back.setFixedWidth(120)
        btn_back.clicked.connect(self.go_back)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        header_layout.addWidget(btn_back)

        # Título
        header_label = QLabel("Procesamiento de Remuneraciones Separadas")
        header_label.setObjectName("headerLabel")
        header_layout.addWidget(header_label, alignment=Qt.AlignCenter)

        # Espaciador para centrar el título
        header_layout.addSpacerItem(QSpacerItem(120, 20, QSizePolicy.Fixed, QSizePolicy.Minimum))

        layout.addLayout(header_layout)

        # Línea separadora
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separator")
        layout.addWidget(line)

        # Sección de modo
        mode_container = self.create_card_container()
        mode_layout = QVBoxLayout(mode_container)

        mode_title = QLabel("Modo de Procesamiento")
        mode_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        mode_layout.addWidget(mode_title)

        mode_row = QHBoxLayout()
        lbl_modo = QLabel("Seleccione el modo:")
        self.combo_modo = QComboBox()
        self.combo_modo.addItems(["SEP", "PIE-NORMAL"])
        mode_row.addWidget(lbl_modo)
        mode_row.addWidget(self.combo_modo)
        mode_row.addStretch()
        mode_layout.addLayout(mode_row)

        layout.addWidget(mode_container)

        # Sección de archivos
        files_container = self.create_card_container()
        files_layout = QVBoxLayout(files_container)

        files_title = QLabel("Archivos de Entrada y Salida")
        files_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        files_layout.addWidget(files_title)

        # Archivo de entrada
        self.label_input = QLabel("📄 Archivo Excel de entrada: No seleccionado")
        files_layout.addWidget(self.label_input)

        self.btn_select_input = QPushButton("Seleccionar Archivo Excel")
        self.btn_select_input.setObjectName("selectButton")
        self.btn_select_input.clicked.connect(self.select_input_file)
        self.add_shadow_effect(self.btn_select_input)
        files_layout.addWidget(self.btn_select_input)

        files_layout.addSpacing(15)

        # Archivo de salida
        self.label_output = QLabel("💾 Guardar archivo en: No seleccionado")
        files_layout.addWidget(self.label_output)

        self.btn_select_output = QPushButton("Seleccionar Destino")
        self.btn_select_output.setObjectName("selectButton")
        self.btn_select_output.clicked.connect(self.select_output_file)
        self.add_shadow_effect(self.btn_select_output)
        files_layout.addWidget(self.btn_select_output)

        layout.addWidget(files_container)

        # Botón de inicio
        self.btn_start = QPushButton("🚀 Iniciar Procesamiento")
        self.btn_start.setObjectName("startButton")
        self.btn_start.clicked.connect(self.start_process)
        self.btn_start.setEnabled(False)
        self.add_shadow_effect(self.btn_start)
        layout.addWidget(self.btn_start)

        # Barra de progreso y estado
        progress_container = self.create_card_container()
        progress_layout = QVBoxLayout(progress_container)

        self.status_label = QLabel("⏳ Esperando acción...")
        self.status_label.setObjectName("statusLabel")
        progress_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)

        layout.addWidget(progress_container)

        # Separador
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setObjectName("separator")
        layout.addWidget(line2)

        # Sección de duplicados (colapsable)
        self.btn_toggle_dup = QPushButton("📊 Mostrar Opciones de Duplicados")
        self.btn_toggle_dup.setCheckable(True)
        self.btn_toggle_dup.toggled.connect(self.toggle_dup_options)
        self.btn_toggle_dup.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                text-align: left;
                padding-left: 20px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:checked {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(self.btn_toggle_dup)

        # Contenedor de duplicados (oculto inicialmente)
        self.dup_frame = self.create_card_container()
        dup_layout = QVBoxLayout(self.dup_frame)

        dup_title = QLabel("Procesamiento de Duplicados")
        dup_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        dup_layout.addWidget(dup_title)

        # Archivo 1
        self.label_input_dup1 = QLabel("📄 Archivo Duplicados 1: No seleccionado")
        dup_layout.addWidget(self.label_input_dup1)

        self.btn_select_input_dup1 = QPushButton("Seleccionar Archivo 1")
        self.btn_select_input_dup1.clicked.connect(self.select_input_dup1)
        dup_layout.addWidget(self.btn_select_input_dup1)

        # Archivo 2
        self.label_input_dup2 = QLabel("📄 Archivo Duplicados 2: No seleccionado")
        dup_layout.addWidget(self.label_input_dup2)

        self.btn_select_input_dup2 = QPushButton("Seleccionar Archivo 2")
        self.btn_select_input_dup2.clicked.connect(self.select_input_dup2)
        dup_layout.addWidget(self.btn_select_input_dup2)

        # Salida
        self.label_output_dup = QLabel("💾 Guardar resultado en: No seleccionado")
        dup_layout.addWidget(self.label_output_dup)

        self.btn_select_output_dup = QPushButton("Seleccionar Destino")
        self.btn_select_output_dup.clicked.connect(self.select_output_dup)
        dup_layout.addWidget(self.btn_select_output_dup)

        # Botón procesar duplicados
        self.btn_start_dup = QPushButton("🔄 Procesar Duplicados")
        self.btn_start_dup.setObjectName("startButton")
        self.btn_start_dup.clicked.connect(self.start_duplicados_process)
        self.btn_start_dup.setEnabled(False)
        dup_layout.addWidget(self.btn_start_dup)

        self.dup_frame.hide()
        layout.addWidget(self.dup_frame)

        # Espaciador
        layout.addStretch()

        self.setLayout(layout)

    def create_card_container(self):
        """Crea un contenedor con estilo de tarjeta"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(Qt.gray)
        shadow.setOffset(0, 3)
        container.setGraphicsEffect(shadow)
        return container

    def add_shadow_effect(self, widget):
        """Añade efecto de sombra a un widget"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 4)
        widget.setGraphicsEffect(shadow)

    def apply_styles(self):
        """Aplica estilos CSS a la ventana"""
        self.setStyleSheet(PROCESSOR_WINDOW_STYLE)

    def fade_in(self):
        """Anima la entrada de la ventana"""
        try:
            self.setWindowOpacity(0.0)
            # Guardar referencia de animación para evitar garbage collection
            self._fade_in_anim = QPropertyAnimation(self, b"windowOpacity")
            self._fade_in_anim.setDuration(500)
            self._fade_in_anim.setStartValue(0.0)
            self._fade_in_anim.setEndValue(1.0)
            self._fade_in_anim.setEasingCurve(QEasingCurve.InOutQuad)
            self._fade_in_anim.start()
        except Exception as e:
            logging.error(f"Error en animación fade-in: {e}")
            # Si falla la animación, simplemente mostrar la ventana
            self.setWindowOpacity(1.0)

    def toggle_dup_options(self, checked):
        """Muestra/oculta opciones de duplicados"""
        if checked:
            self.dup_frame.show()
            self.btn_toggle_dup.setText("📊 Ocultar Opciones de Duplicados")
        else:
            self.dup_frame.hide()
            self.btn_toggle_dup.setText("📊 Mostrar Opciones de Duplicados")

    # === Métodos de selección de archivos (SEP/PIE) ===

    def select_input_file(self):
        """Selecciona archivo de entrada"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo Excel", str(Path.home()),
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.input_path = Path(file_path)
            self.label_input.setText(f"📄 Archivo Excel de entrada: {self.input_path.name}")
            self.output_path = None
            self.label_output.setText("💾 Guardar archivo en: No seleccionado")
            self.check_enable_start()

    def select_output_file(self):
        """Selecciona archivo de salida"""
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
            self.label_output.setText(f"💾 Guardar archivo en: {self.output_path.name}")
            self.check_enable_start()

    def check_enable_start(self):
        """Habilita botón de inicio si hay archivos seleccionados"""
        self.btn_start.setEnabled(bool(self.input_path and self.output_path))

    def start_process(self):
        """Inicia el procesamiento"""
        if not self.input_path or not self.output_path:
            QMessageBox.warning(self, "Error", "Debe seleccionar archivo de entrada y destino.")
            return

        try:
            # Deshabilitar controles
            self.btn_start.setEnabled(False)
            self.btn_select_input.setEnabled(False)
            self.btn_select_output.setEnabled(False)
            self.combo_modo.setEnabled(False)
            self.progress_bar.setValue(0)
            self.status_label.setText("⚙️ Iniciando proceso...")

            # Cambiar cursor
            self.setCursor(Qt.WaitCursor)

            # Crear procesador según modo
            modo = self.combo_modo.currentText()
            if modo == "SEP":
                processor = SEPProcessor()
            elif modo == "PIE-NORMAL":
                processor = PIEProcessor()
            else:
                raise ValueError(f"Modo de procesamiento no reconocido: {modo}")

            # Crear y configurar worker
            self.worker = ProcessorWorker(processor, self.input_path, self.output_path)
            self.worker.progress_signal.connect(self.update_progress)
            self.worker.finished_signal.connect(self.process_finished)
            self.worker.error_signal.connect(self.process_error)

            # Iniciar procesamiento
            self.worker.start()

            # Restaurar cursor
            self.setCursor(Qt.ArrowCursor)

        except ImportError as e:
            logging.error(f"Error al importar procesador: {e}")
            self.setCursor(Qt.ArrowCursor)
            QMessageBox.critical(
                self,
                "❌ Error de Importación",
                f"No se pudo cargar el procesador {modo}.\n\nError técnico: {str(e)}\n\nPor favor, reinstale la aplicación."
            )
            self.reset_ui()

        except ValueError as e:
            logging.error(f"Error de validación: {e}")
            self.setCursor(Qt.ArrowCursor)
            QMessageBox.critical(
                self,
                "❌ Error de Validación",
                f"Error en la configuración del procesamiento.\n\nError: {str(e)}"
            )
            self.reset_ui()

        except Exception as e:
            logging.error(f"Error inesperado al iniciar proceso: {e}")
            self.setCursor(Qt.ArrowCursor)
            QMessageBox.critical(
                self,
                "❌ Error Inesperado",
                f"Ocurrió un error al iniciar el procesamiento.\n\nError: {str(e)}\n\nIntente nuevamente o contacte al soporte."
            )
            self.reset_ui()

    # === Métodos de duplicados ===

    def select_input_dup1(self):
        """Selecciona primer archivo de duplicados"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Archivo Duplicados 1", str(Path.home()),
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.input_dup1 = Path(file_path)
            self.label_input_dup1.setText(f"📄 Archivo Duplicados 1: {self.input_dup1.name}")
            self.check_enable_dup_start()

    def select_input_dup2(self):
        """Selecciona segundo archivo de duplicados"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Archivo Duplicados 2", str(Path.home()),
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.input_dup2 = Path(file_path)
            self.label_input_dup2.setText(f"📄 Archivo Duplicados 2: {self.input_dup2.name}")
            self.check_enable_dup_start()

    def select_output_dup(self):
        """Selecciona archivo de salida para duplicados"""
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
            self.label_output_dup.setText(f"💾 Guardar resultado en: {self.output_dup.name}")
            self.check_enable_dup_start()

    def check_enable_dup_start(self):
        """Habilita botón de duplicados si hay archivos"""
        self.btn_start_dup.setEnabled(bool(self.input_dup1 and self.input_dup2 and self.output_dup))

    def start_duplicados_process(self):
        """Inicia procesamiento de duplicados"""
        if not (self.input_dup1 and self.input_dup2 and self.output_dup):
            QMessageBox.warning(self, "Error", "Debe seleccionar ambos archivos de entrada y un destino.")
            return

        try:
            # Deshabilitar controles
            self.btn_start_dup.setEnabled(False)
            self.btn_select_input_dup1.setEnabled(False)
            self.btn_select_input_dup2.setEnabled(False)
            self.btn_select_output_dup.setEnabled(False)
            self.progress_bar.setValue(0)
            self.status_label.setText("⚙️ Iniciando proceso de duplicados...")

            # Cambiar cursor
            self.setCursor(Qt.WaitCursor)

            # Validar que los archivos existan
            if not self.input_dup1.exists():
                raise FileNotFoundError(f"El archivo no existe: {self.input_dup1}")
            if not self.input_dup2.exists():
                raise FileNotFoundError(f"El archivo no existe: {self.input_dup2}")

            # Crear procesador
            processor = DuplicadosProcessor()

            # Crear y configurar worker
            self.worker_dup = DuplicadosWorker(processor, self.input_dup1, self.input_dup2, self.output_dup)
            self.worker_dup.progress_signal.connect(self.update_progress)
            self.worker_dup.finished_signal.connect(self.process_finished_dup)
            self.worker_dup.error_signal.connect(self.process_error)

            # Iniciar procesamiento
            self.worker_dup.start()

            # Restaurar cursor
            self.setCursor(Qt.ArrowCursor)

        except FileNotFoundError as e:
            logging.error(f"Archivo no encontrado: {e}")
            self.setCursor(Qt.ArrowCursor)
            QMessageBox.critical(
                self,
                "❌ Archivo No Encontrado",
                f"No se pudo encontrar el archivo seleccionado.\n\nError: {str(e)}\n\nPor favor, seleccione un archivo válido."
            )
            self.reset_ui()

        except ImportError as e:
            logging.error(f"Error al importar DuplicadosProcessor: {e}")
            self.setCursor(Qt.ArrowCursor)
            QMessageBox.critical(
                self,
                "❌ Error de Importación",
                f"No se pudo cargar el procesador de duplicados.\n\nError técnico: {str(e)}\n\nPor favor, reinstale la aplicación."
            )
            self.reset_ui()

        except Exception as e:
            logging.error(f"Error inesperado al iniciar proceso de duplicados: {e}")
            self.setCursor(Qt.ArrowCursor)
            QMessageBox.critical(
                self,
                "❌ Error Inesperado",
                f"Ocurrió un error al iniciar el procesamiento de duplicados.\n\nError: {str(e)}\n\nIntente nuevamente o contacte al soporte."
            )
            self.reset_ui()

    # === Métodos de actualización y finalización ===

    def update_progress(self, value, message):
        """Actualiza barra de progreso"""
        self.progress_bar.setValue(value)
        self.status_label.setText(f"⚙️ {message}")

    def process_finished(self, output_path_str):
        """Maneja finalización exitosa"""
        reply = QMessageBox.question(
            self,
            "✅ Proceso completado",
            f"Proceso completado exitosamente.\n\nArchivo guardado en:\n{output_path_str}\n\n¿Desea procesar otro archivo?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.reset_ui()
        else:
            self.go_back()

    def process_finished_dup(self, output_path_str):
        """Maneja finalización de duplicados"""
        reply = QMessageBox.question(
            self,
            "✅ Proceso de Duplicados completado",
            f"Proceso completado exitosamente.\n\nArchivo guardado en:\n{output_path_str}\n\n¿Desea procesar otro archivo?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.reset_ui()
        else:
            self.go_back()

    def process_error(self, error_msg):
        """Maneja errores"""
        QMessageBox.critical(self, "❌ Error", f"Ocurrió un error:\n\n{error_msg}")
        self.reset_ui()

    def reset_ui(self):
        """Reinicia la interfaz"""
        try:
            # Reinicia SEP/PIE
            self.input_path = None
            self.output_path = None
            self.label_input.setText("📄 Archivo Excel de entrada: No seleccionado")
            self.label_output.setText("💾 Guardar archivo en: No seleccionado")
            self.btn_start.setEnabled(False)
            self.btn_select_input.setEnabled(True)
            self.btn_select_output.setEnabled(True)
            self.combo_modo.setEnabled(True)

            # Reinicia duplicados
            self.input_dup1 = None
            self.input_dup2 = None
            self.output_dup = None
            self.label_input_dup1.setText("📄 Archivo Duplicados 1: No seleccionado")
            self.label_input_dup2.setText("📄 Archivo Duplicados 2: No seleccionado")
            self.label_output_dup.setText("💾 Guardar resultado en: No seleccionado")
            self.btn_start_dup.setEnabled(False)
            self.btn_select_input_dup1.setEnabled(True)
            self.btn_select_input_dup2.setEnabled(True)
            self.btn_select_output_dup.setEnabled(True)

            self.status_label.setText("⏳ Esperando acción...")
            self.progress_bar.setValue(0)

            # Restaurar cursor si está en espera
            self.setCursor(Qt.ArrowCursor)

        except Exception as e:
            logging.error(f"Error al reiniciar UI: {e}")

    def go_back(self):
        """Vuelve a la landing page"""
        try:
            # Cambiar cursor
            self.setCursor(Qt.WaitCursor)

            # Importar y crear landing page
            from ui.landing_page import LandingPage
            self.landing = LandingPage()
            self.landing.show()

            # Restaurar cursor y cerrar
            self.setCursor(Qt.ArrowCursor)
            self.close()

        except ImportError as e:
            logging.error(f"Error al importar LandingPage: {e}")
            self.setCursor(Qt.ArrowCursor)
            QMessageBox.critical(
                self,
                "❌ Error de Importación",
                f"No se pudo cargar la pantalla principal.\n\nError técnico: {str(e)}\n\nLa aplicación se cerrará."
            )
            self.close()

        except Exception as e:
            logging.error(f"Error inesperado al volver: {e}")
            self.setCursor(Qt.ArrowCursor)
            QMessageBox.critical(
                self,
                "❌ Error Inesperado",
                f"Ocurrió un error al volver a la pantalla principal.\n\nError: {str(e)}\n\nLa aplicación se cerrará."
            )
            self.close()
