from setuptools import setup

VERSION = '2.1.1'

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.ico',
    'packages': ['pandas', 'numpy', 'openpyxl', 'PyQt5'],
    'excludes': ['unittest', 'doctest', 'pydoc', 'test'],
    'includes': ['pandas', 'numpy', 'cmath'],
}

setup(
    name='RemuPro',
    version=VERSION,
    author='Eric Aguayo Quintriqueo',
    author_email='leftra123@gmail.com',
    url='https://github.com/leftra123/colab',
    description='Sistema de Procesamiento de Remuneraciones SEP/PIE-NORMAL',
    long_description=open('README.md').read() if 'README.md' in __import__('os').listdir('.') else '',
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
