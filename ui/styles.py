"""
Estilos modernos para RemuPro
Diseñado para funcionar en Windows y macOS
"""

# Estilos para la Landing Page
LANDING_PAGE_STYLE = """
QWidget {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #1e3c72, stop:1 #2a5298);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

QLabel#title {
    color: #ffffff;
    font-size: 42px;
    font-weight: bold;
    padding: 20px;
    background: transparent;
}

QLabel#subtitle {
    color: #e0e0e0;
    font-size: 18px;
    padding: 10px;
    background: transparent;
}

QLabel#version {
    color: #b0b0b0;
    font-size: 14px;
    padding: 5px;
    background: transparent;
}

QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #667eea, stop:1 #764ba2);
    color: white;
    border: none;
    border-radius: 15px;
    padding: 30px 40px;
    font-size: 20px;
    font-weight: bold;
    min-width: 400px;
    min-height: 80px;
}

QPushButton#primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #764ba2, stop:1 #667eea);
    transform: scale(1.05);
}

QPushButton#primaryButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #5a3a82, stop:1 #5568ca);
    padding: 32px 40px 28px 40px;
}

QPushButton#primaryButton:disabled {
    background: #555555;
    color: #999999;
}

QPushButton#secondaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #f093fb, stop:1 #f5576c);
    color: white;
    border: none;
    border-radius: 15px;
    padding: 30px 40px;
    font-size: 20px;
    font-weight: bold;
    min-width: 400px;
    min-height: 80px;
}

QPushButton#secondaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #f5576c, stop:1 #f093fb);
}

QPushButton#secondaryButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #d04858, stop:1 #d078db);
    padding: 32px 40px 28px 40px;
}
"""

# Estilos para ventanas de procesamiento
PROCESSOR_WINDOW_STYLE = """
QWidget {
    background-color: #f5f7fa;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

QLabel {
    color: #2c3e50;
    font-size: 14px;
    padding: 5px;
}

QLabel#headerLabel {
    color: #1e3c72;
    font-size: 24px;
    font-weight: bold;
    padding: 15px;
}

QLabel#statusLabel {
    color: #34495e;
    font-size: 13px;
    padding: 8px;
    background-color: #ecf0f1;
    border-radius: 5px;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
    min-height: 40px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #21618c;
}

QPushButton:disabled {
    background-color: #95a5a6;
    color: #bdc3c7;
}

QPushButton#startButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #11998e, stop:1 #38ef7d);
    font-size: 16px;
    padding: 15px 30px;
    min-height: 50px;
}

QPushButton#startButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #0e8074, stop:1 #2dd163);
}

QPushButton#selectButton {
    background-color: #8e44ad;
}

QPushButton#selectButton:hover {
    background-color: #7d3c98;
}

QComboBox {
    background-color: white;
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 14px;
    min-height: 35px;
}

QComboBox:hover {
    border: 2px solid #3498db;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 8px solid #34495e;
    margin-right: 10px;
}

QProgressBar {
    background-color: #ecf0f1;
    border: none;
    border-radius: 10px;
    text-align: center;
    height: 25px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #667eea, stop:1 #764ba2);
    border-radius: 10px;
}

QFrame#separator {
    background-color: #bdc3c7;
    max-height: 2px;
}
"""

# Estilos para ventana de desarrollo
DEVELOPMENT_WINDOW_STYLE = """
QWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #232526, stop:1 #414345);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

QLabel#mainTitle {
    color: #ffffff;
    font-size: 36px;
    font-weight: bold;
    padding: 20px;
    background: transparent;
}

QLabel#subtitle {
    color: #e0e0e0;
    font-size: 18px;
    padding: 15px;
    background: transparent;
}

QLabel#developers {
    color: #00d4ff;
    font-size: 24px;
    font-weight: 600;
    padding: 10px;
    background: transparent;
}

QLabel#message {
    color: #a0a0a0;
    font-size: 16px;
    padding: 10px;
    background: transparent;
    font-style: italic;
}

QPushButton#backButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #434343, stop:1 #000000);
    color: white;
    border: 2px solid #00d4ff;
    border-radius: 10px;
    padding: 15px 30px;
    font-size: 16px;
    font-weight: bold;
    min-width: 200px;
}

QPushButton#backButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #00d4ff, stop:1 #00a8cc);
    border: 2px solid #ffffff;
}

QPushButton#backButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #0099bb, stop:1 #007799);
}
"""

# Estilos para componentes de loading
LOADING_STYLE = """
QLabel#loadingText {
    color: #00d4ff;
    font-size: 18px;
    font-weight: 600;
    background: transparent;
}
"""
