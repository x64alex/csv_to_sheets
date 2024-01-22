from setuptools import setup

APP = ['sheets.py']
DATA_FILES = [('resources', ['credentials.json'])]  # Add this line
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pandas', 'googleapiclient'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
