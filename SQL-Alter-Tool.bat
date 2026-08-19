:: A simple .bat in order to run the python program. (double-click)
:: Make sure you created a Python Virtual Environment (venv). If not, follow ReadMe instructions.
@echo off
setlocal

:: Edit to match your folder
set "path=Write_your_path_here\SQL-Alter-Tool"

cd %path%
call "%path%\.venv\Scripts\activate.bat"
pip install -r requirements.txt
python src\main.py
::pause
