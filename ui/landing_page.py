"""
Landing Page - Pantalla principal de RemuPro
Compatible con Windows y macOS
"""

import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont
from ui.styles import LANDING_PAGE_STYLE


class LandingPage(QWidget):
    """Pantalla principal con opciones de procesamiento"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RemuPro - Sistema de Procesamiento de Remuneraciones")
        self.resize(900, 700)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setAlignment(Qt.AlignCenter)

        # Espaciador superior
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Título principal
        title = QLabel("RemuPro")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Sistema de Procesamiento de Remuneraciones")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Versión
        version = QLabel("Versión 2.1.1")
        version.setObjectName("version")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        # Espacio entre título y botones
        layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Botón 1: Procesar Separado
        self.btn_separated = QPushButton("Procesar Remuneraciones\nSeparadas")
        self.btn_separated.setObjectName("primaryButton")
        self.btn_separated.setCursor(Qt.PointingHandCursor)
        self.btn_separated.clicked.connect(self.open_separated_processor)
        self.add_shadow_effect(self.btn_separated)
        layout.addWidget(self.btn_separated, alignment=Qt.AlignCenter)

        # Descripción botón 1
        desc1 = QLabel("Procesar archivos en modo SEP o PIE-NORMAL de forma independiente")
        desc1.setObjectName("subtitle")
        desc1.setAlignment(Qt.AlignCenter)
        desc1.setStyleSheet("font-size: 14px; color: #c0c0c0;")
        layout.addWidget(desc1)

        # Espacio entre botones
        layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Botón 2: Procesar Consolidado (En desarrollo)
        self.btn_consolidated = QPushButton("Procesar Remuneraciones\nConsolidadas")
        self.btn_consolidated.setObjectName("secondaryButton")
        self.btn_consolidated.setCursor(Qt.PointingHandCursor)
        self.btn_consolidated.clicked.connect(self.open_consolidated_processor)
        self.add_shadow_effect(self.btn_consolidated)
        layout.addWidget(self.btn_consolidated, alignment=Qt.AlignCenter)

        # Descripción botón 2
        desc2 = QLabel("Procesamiento unificado e inteligente de todas las remuneraciones")
        desc2.setObjectName("subtitle")
        desc2.setAlignment(Qt.AlignCenter)
        desc2.setStyleSheet("font-size: 14px; color: #c0c0c0;")
        layout.addWidget(desc2)

        # Espaciador inferior
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Footer
        footer = QLabel("© 2024 RemuPro - Educación Chilena")
        footer.setObjectName("version")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        self.setLayout(layout)

        # Animaciones de entrada para los botones
        self.animate_button_entrance(self.btn_separated, delay=100)
        self.animate_button_entrance(self.btn_consolidated, delay=300)

    def add_shadow_effect(self, widget):
        """Añade efecto de sombra a un widget"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 8)
        widget.setGraphicsEffect(shadow)

    def animate_button_entrance(self, button, delay=0):
        """Anima la entrada de un botón con efecto de deslizamiento"""
        # Guardar posición original
        original_pos = button.pos()

        # Mover fuera de la pantalla inicialmente
        button.move(button.x(), button.y() + 100)
        button.setStyleSheet(button.styleSheet() + " QWidget { opacity: 0; }")

        # Animación de posición
        anim = QPropertyAnimation(button, b"pos")
        anim.setDuration(800)
        anim.setStartValue(QPoint(button.x(), button.y()))
        anim.setEndValue(QPoint(button.x(), button.y() - 100))
        anim.setEasingCurve(QEasingCurve.OutCubic)

        # Iniciar después del delay
        if delay > 0:
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(delay, anim.start)
        else:
            anim.start()

    def apply_styles(self):
        """Aplica estilos CSS a la ventana"""
        self.setStyleSheet(LANDING_PAGE_STYLE)

    def open_separated_processor(self):
        """Abre la ventana de procesamiento separado"""
        try:
            # Deshabilitar botones para evitar doble-click
            self.btn_separated.setEnabled(False)
            self.btn_consolidated.setEnabled(False)

            # Cambiar cursor a espera
            from PyQt5.QtCore import Qt
            self.setCursor(Qt.WaitCursor)

            # Importar y crear ventana
            from ui.processor_window import ProcessorWindow
            self.processor_window = ProcessorWindow()
            self.processor_window.show()

            # Restaurar cursor y cerrar
            self.setCursor(Qt.ArrowCursor)
            self.close()

        except ImportError as e:
            import logging
            from PyQt5.QtWidgets import QMessageBox
            logging.error(f"Error al importar ProcessorWindow: {e}")
            self.setCursor(Qt.ArrowCursor)
            self.btn_separated.setEnabled(True)
            self.btn_consolidated.setEnabled(True)
            QMessageBox.critical(
                self,
                "Error de Importación",
                f"No se pudo cargar la ventana de procesamiento.\n\nError técnico: {str(e)}\n\nPor favor, reinstale la aplicación."
            )
        except Exception as e:
            import logging
            from PyQt5.QtWidgets import QMessageBox
            logging.error(f"Error inesperado al abrir ProcessorWindow: {e}")
            self.setCursor(Qt.ArrowCursor)
            self.btn_separated.setEnabled(True)
            self.btn_consolidated.setEnabled(True)
            QMessageBox.critical(
                self,
                "Error Inesperado",
                f"Ocurrió un error al abrir la ventana de procesamiento.\n\nError: {str(e)}"
            )

    def open_consolidated_processor(self):
        """Abre la ventana de procesamiento consolidado (en desarrollo)"""
        try:
            # Deshabilitar botones para evitar doble-click
            self.btn_separated.setEnabled(False)
            self.btn_consolidated.setEnabled(False)

            # Cambiar cursor a espera
            from PyQt5.QtCore import Qt
            self.setCursor(Qt.WaitCursor)

            # Importar y crear ventana
            from ui.development_window import DevelopmentWindow
            self.dev_window = DevelopmentWindow()
            self.dev_window.show()

            # Restaurar cursor y cerrar
            self.setCursor(Qt.ArrowCursor)
            self.close()

        except ImportError as e:
            import logging
            from PyQt5.QtWidgets import QMessageBox
            logging.error(f"Error al importar DevelopmentWindow: {e}")
            self.setCursor(Qt.ArrowCursor)
            self.btn_separated.setEnabled(True)
            self.btn_consolidated.setEnabled(True)
            QMessageBox.critical(
                self,
                "Error de Importación",
                f"No se pudo cargar la ventana de desarrollo.\n\nError técnico: {str(e)}\n\nPor favor, reinstale la aplicación."
            )
        except Exception as e:
            import logging
            from PyQt5.QtWidgets import QMessageBox
            logging.error(f"Error inesperado al abrir DevelopmentWindow: {e}")
            self.setCursor(Qt.ArrowCursor)
            self.btn_separated.setEnabled(True)
            self.btn_consolidated.setEnabled(True)
            QMessageBox.critical(
                self,
                "Error Inesperado",
                f"Ocurrió un error al abrir la ventana de desarrollo.\n\nError: {str(e)}"
            )


def main():
    """Función principal para ejecutar la aplicación"""
    from PyQt5.QtWidgets import QApplication
    import logging

    # Configuración de DPI para Windows y macOS
    if sys.platform == 'win32':
        import ctypes
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception as e:
            logging.warning(f"No se pudo configurar DPI en Windows: {str(e)}")

    # En macOS, Qt maneja automáticamente el DPI

    app = QApplication(sys.argv)

    # Configurar fuente base según plataforma
    if sys.platform == 'darwin':  # macOS
        app.setFont(QFont("SF Pro Display", 11))
    else:  # Windows y otros
        app.setFont(QFont("Segoe UI", 10))

    window = LandingPage()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
