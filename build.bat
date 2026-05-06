@echo off

echo ============================
echo GERANDO BUILD SMARTCHECK
echo ============================

call venv\Scripts\activate

pyinstaller --distpath . SmartCheck.spec

echo.
echo BUILD FINALIZADO
pause