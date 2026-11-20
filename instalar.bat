@echo off
cd /d "%~dp0"
py -3.13 -m venv .venv
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist ".env" copy ".env.example" ".env"
echo Instalacion terminada. Edita .env y ejecuta iniciar_dashboard.bat
pause
