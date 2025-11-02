"""
Componentes de loading animados
Compatible con Windows y macOS
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QPen


class SpinnerWidget(QWidget):
    """Widget con spinner animado circular"""

    def __init__(self, parent=None, size=80, color="#00d4ff"):
        super().__init__(parent)
        self.angle = 0
        self.size = size
        self.color = QColor(color)
        self.setFixedSize(size, size)

        # Timer para animación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(30)  # 30ms = ~33fps

    def rotate(self):
        self.angle = (self.angle + 8) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Dibuja arco giratorio
        pen = QPen(self.color, 6, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)

        rect = self.rect().adjusted(10, 10, -10, -10)
        painter.drawArc(rect, self.angle * 16, 120 * 16)

    def stop(self):
        self.timer.stop()


class PulsingDot(QWidget):
    """Punto pulsante animado"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 1.0
        self.setFixedSize(15, 15)

        # Animación de opacidad
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(800)
        self.animation.setStartValue(0.3)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setLoopCount(-1)  # Infinito
        self.animation.start()

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, value):
        self._opacity = value
        self.update()

    opacity = pyqtProperty(float, get_opacity, set_opacity)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setOpacity(self._opacity)

        color = QColor("#00d4ff")
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, 11, 11)


class LoadingWidget(QWidget):
    """Widget de loading completo con spinner y texto"""

    def __init__(self, parent=None, text="Cargando..."):
        super().__init__(parent)
        self.setup_ui(text)

    def setup_ui(self, text):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Spinner
        self.spinner = SpinnerWidget(self, size=100, color="#00d4ff")
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

        # Texto
        self.label = QLabel(text)
        self.label.setObjectName("loadingText")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Dots pulsantes
        dots_layout = QVBoxLayout()
        dots_layout.setAlignment(Qt.AlignCenter)
        dots_layout.setSpacing(5)

        dot_container = QWidget()
        dot_layout = QVBoxLayout(dot_container)
        dot_layout.setContentsMargins(0, 0, 0, 0)
        dot_layout.setSpacing(8)
        dot_layout.setAlignment(Qt.AlignCenter)

        # Crear 3 dots con delays diferentes
        for i in range(3):
            dot = PulsingDot(self)
            dot.animation.setStartValue(0.3)
            dot.animation.setCurrentTime(i * 266)  # Delay escalonado
            dot_layout.addWidget(dot, alignment=Qt.AlignCenter)

        layout.addWidget(dot_container, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def set_text(self, text):
        """Actualiza el texto del loading"""
        self.label.setText(text)

    def stop(self):
        """Detiene la animación"""
        self.spinner.stop()


class ProgressLoadingWidget(QWidget):
    """Widget de loading con barra de progreso y mensaje"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        from PyQt5.QtWidgets import QProgressBar

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        # Spinner pequeño
        self.spinner = SpinnerWidget(self, size=60, color="#667eea")
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

        # Mensaje de estado
        self.status_label = QLabel("Iniciando...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #2c3e50;
            font-size: 16px;
            font-weight: 600;
        """)
        layout.addWidget(self.status_label)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedWidth(400)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def update_progress(self, value, message=""):
        """Actualiza progreso y mensaje"""
        self.progress_bar.setValue(value)
        if message:
            self.status_label.setText(message)

    def stop(self):
        """Detiene la animación"""
        self.spinner.stop()
