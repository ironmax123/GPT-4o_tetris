from setuptools import setup

import sys
if sys.platform == "win32":
    import _overlapped
    import _io._WindowsConsoleIO
APP = ['GPTs_Tetris.py']  # tkinterアプリのスクリプトファイル名を指定
OPTIONS = {
    'packages': ['tkinter'],  # tkinterのみをパッケージング
    'iconfile': 'file.icns',  
}

# high_scores.csvのパスを指定
DATA_FILES = [('',['high_scores.csv'])]

# セットアップ
setup(
    app=APP,
    name='GPT-TETRIS',# アプリケーションの名前
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
