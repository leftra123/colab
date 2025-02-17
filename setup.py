from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'packages': ['pandas', 'numpy', 'openpyxl', 'PyQt5'],
    'excludes': ['unittest', 'doctest', 'pydoc', 'test'],
    'includes': ['pandas', 'numpy', 'cmath'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
