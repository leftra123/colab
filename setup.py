import sys
from setuptools import setup, find_packages

VERSION = '2.1.1'
APP = ['main.py']
DATA_FILES = []

# Configuración base común
setup_config = {
    'name': 'RemuPro',
    'version': VERSION,
    'author': 'Eric Aguayo Quintriqueo',
    'author_email': 'leftra123@gmail.com',
    'url': 'https://github.com/leftra123/colab',
    'description': 'Sistema de Procesamiento de Remuneraciones SEP/PIE-NORMAL',
    'long_description': open('README.md').read() if 'README.md' in __import__('os').listdir('.') else '',
    'long_description_content_type': 'text/markdown',
    'packages': find_packages(),
    'classifiers': [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    'install_requires': [
        'pandas>=2.0.0',
        'numpy>=2.0.0',
        'openpyxl>=3.1.0',
        'PyQt5>=5.15.0',
    ],
    'python_requires': '>=3.8',
}

# Opciones específicas para macOS (py2app)
mac_options = {
    'argv_emulation': False,
    'iconfile': 'icon.ico',
    'packages': ['pandas', 'numpy', 'openpyxl', 'PyQt5'],
    'excludes': ['unittest', 'doctest', 'pydoc', 'test'],
    'includes': ['pandas', 'numpy', 'cmath'],
    'plist': {
        'CFBundleName': 'RemuPro',
        'CFBundleDisplayName': 'RemuPro',
        'CFBundleIdentifier': 'com.ericaguayo.remupro',
        'CFBundleVersion': VERSION,
        'CFBundleShortVersionString': VERSION,
        'NSHumanReadableCopyright': '© 2023-2025 Eric Aguayo Quintriqueo'
    }
}

# Opciones específicas para Windows (py2exe)
win_options = {
    'packages': ['pandas', 'numpy', 'openpyxl', 'PyQt5'],
    'excludes': ['unittest', 'doctest', 'pydoc', 'test'],
    'includes': ['pandas', 'numpy', 'cmath'],
    'bundle_files': 1,
    'compressed': True,
    'optimize': 2,
}

# Configuración específica para cada plataforma
if sys.platform == 'darwin':
    setup_config.update({
        'app': APP,
        'data_files': DATA_FILES,
        'options': {'py2app': mac_options},
        'setup_requires': ['py2app'],
    })
elif sys.platform == 'win32':
    setup_config.update({
        'windows': [{
            'script': 'main.py',
            'icon_resources': [(1, 'icon.ico')],
            'dest_base': 'RemuPro',
            'copyright': '© 2023-2025 Eric Aguayo Quintriqueo',
        }],
        'options': {'py2exe': win_options},
        'setup_requires': ['py2exe'],
    })
else:  # Linux u otros un passsss
    pass

setup(**setup_config)