@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\streamlit.exe" (
  echo No se encontro el entorno virtual. Ejecuta primero instalar.bat
  pause
  exit /b 1
)
call ".venv\Scripts\activate.bat"
streamlit run dashboard.py
pause
