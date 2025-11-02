"""
Development Window - Pantalla de funcionalidad en desarrollo
Compatible con Windows y macOS
"""

import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont
from ui.styles import DEVELOPMENT_WINDOW_STYLE, LOADING_STYLE
from ui.components.loading import LoadingWidget


class DevelopmentWindow(QWidget):
    """Ventana que muestra que la funcionalidad está en desarrollo"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RemuPro - En Desarrollo")
        self.resize(800, 600)
        self._opacity = 0.0
        self.setup_ui()
        self.apply_styles()
        self.fade_in()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setAlignment(Qt.AlignCenter)

        # Espaciador superior
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Icono/Emoji de construcción
        icon_label = QLabel("🚧")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            font-size: 80px;
            background: transparent;
        """)
        layout.addWidget(icon_label)

        # Título principal
        title = QLabel("Funcionalidad en Desarrollo")
        title.setObjectName("mainTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Procesamiento Consolidado de Remuneraciones")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Espacio
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Widget de loading animado
        self.loading_widget = LoadingWidget(self, text="")
        self.loading_widget.set_text("")
        layout.addWidget(self.loading_widget, alignment=Qt.AlignCenter)

        # Espacio
        layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Mensaje sobre desarrolladores
        dev_title = QLabel("Equipo de Desarrollo:")
        dev_title.setObjectName("subtitle")
        dev_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(dev_title)

        # Nombres de desarrolladores
        developers = QLabel("Claude & Eric")
        developers.setObjectName("developers")
        developers.setAlignment(Qt.AlignCenter)
        layout.addWidget(developers)

        # Mensaje adicional
        message = QLabel("Trabajando arduamente para traerte la mejor experiencia")
        message.setObjectName("message")
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)

        # Espacio
        layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Mensaje de estado rotativo
        self.status_messages = [
            "Optimizando algoritmos de procesamiento...",
            "Mejorando la interfaz de usuario...",
            "Implementando validaciones avanzadas...",
            "Añadiendo nuevas funcionalidades...",
            "Realizando pruebas de rendimiento...",
            "Puliendo los últimos detalles..."
        ]
        self.current_message_index = 0

        self.status_label = QLabel(self.status_messages[0])
        self.status_label.setObjectName("message")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #ffcc00;
            font-size: 15px;
            font-weight: 500;
            background: transparent;
        """)
        layout.addWidget(self.status_label)

        # Timer para rotar mensajes
        self.message_timer = QTimer(self)
        self.message_timer.timeout.connect(self.rotate_message)
        self.message_timer.start(3000)  # Cambiar cada 3 segundos

        # Espacio
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Botón para volver
        self.btn_back = QPushButton("⬅  Volver al Menú Principal")
        self.btn_back.setObjectName("backButton")
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.clicked.connect(self.go_back)
        self.add_shadow_effect(self.btn_back)
        layout.addWidget(self.btn_back, alignment=Qt.AlignCenter)

        # Espaciador inferior
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.setLayout(layout)

    def rotate_message(self):
        """Rota entre diferentes mensajes de estado"""
        self.current_message_index = (self.current_message_index + 1) % len(self.status_messages)
        new_message = self.status_messages[self.current_message_index]

        # Animación de fade out/in del mensaje
        self.fade_message(new_message)

    def fade_message(self, new_text):
        """Anima el cambio de mensaje con fade"""
        # Nota: Para una animación más suave, podrías usar QGraphicsOpacityEffect
        # pero por simplicidad, solo cambiamos el texto
        self.status_label.setText(new_text)

    def add_shadow_effect(self, widget):
        """Añade efecto de sombra a un widget"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 6)
        widget.setGraphicsEffect(shadow)

    def apply_styles(self):
        """Aplica estilos CSS a la ventana"""
        self.setStyleSheet(DEVELOPMENT_WINDOW_STYLE + LOADING_STYLE)

    def fade_in(self):
        """Anima la entrada de la ventana con fade-in"""
        self.setWindowOpacity(0.0)

        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(600)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_animation.start()

    def go_back(self):
        """Vuelve al menú principal"""
        self.message_timer.stop()
        self.loading_widget.stop()

        # Animación de fade-out antes de cerrar
        fade_out = QPropertyAnimation(self, b"windowOpacity")
        fade_out.setDuration(400)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.InOutQuad)
        fade_out.finished.connect(self.open_landing_page)
        fade_out.start()

    def open_landing_page(self):
        """Abre la landing page"""
        from ui.landing_page import LandingPage
        self.landing = LandingPage()
        self.landing.show()
        self.close()

    def closeEvent(self, event):
        """Maneja el evento de cierre"""
        self.message_timer.stop()
        if hasattr(self, 'loading_widget'):
            self.loading_widget.stop()
        event.accept()


def main():
    """Función principal para ejecutar la ventana de desarrollo"""
    from PyQt5.QtWidgets import QApplication
    import logging

    # Configuración de DPI para Windows y macOS
    if sys.platform == 'win32':
        import ctypes
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception as e:
            logging.warning(f"No se pudo configurar DPI en Windows: {str(e)}")

    app = QApplication(sys.argv)

    # Configurar fuente base según plataforma
    if sys.platform == 'darwin':  # macOS
        app.setFont(QFont("SF Pro Display", 11))
    else:  # Windows y otros
        app.setFont(QFont("Segoe UI", 10))

    window = DevelopmentWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
