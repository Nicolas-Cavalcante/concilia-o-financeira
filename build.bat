@echo off
setlocal

rem Sempre executa a partir da pasta onde este .bat esta salvo.
pushd "%~dp0"

set "PROJECT_DIR=%CD%"
set "SPEC_FILE=%PROJECT_DIR%\SmartCheck.spec"
set "PYTHON_EXE=%PROJECT_DIR%\venv\Scripts\python.exe"

echo ==========================================
echo GERANDO BUILD SMARTCHECK
echo Projeto: %PROJECT_DIR%
echo ==========================================
echo.

if not exist "%SPEC_FILE%" (
    echo [ERRO] Arquivo SmartCheck.spec nao encontrado.
    goto :erro
)

if not exist "%PYTHON_EXE%" (
    echo [ERRO] Ambiente virtual nao encontrado em:
    echo        %PYTHON_EXE%
    echo.
    echo Crie/atualize o venv antes do build.
    goto :erro
)

"%PYTHON_EXE%" -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] PyInstaller nao esta instalado neste venv.
    echo.
    echo Execute:
    echo   "%PYTHON_EXE%" -m pip install pyinstaller
    goto :erro
)

echo Limpando build anterior do projeto...
echo.

"%PYTHON_EXE%" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --distpath "%PROJECT_DIR%" ^
    --workpath "%PROJECT_DIR%\build" ^
    "%SPEC_FILE%"

if errorlevel 1 goto :erro

if not exist "%PROJECT_DIR%\SmartCheck.exe" (
    echo [ERRO] Build terminou, mas SmartCheck.exe nao foi encontrado.
    goto :erro
)

echo.
echo ==========================================
echo BUILD FINALIZADO COM SUCESSO
echo Executavel: %PROJECT_DIR%\SmartCheck.exe
echo ==========================================
echo.
pause
popd
endlocal
exit /b 0

:erro
echo.
echo ==========================================
echo BUILD NAO CONCLUIDO
echo ==========================================
echo.
pause
popd
endlocal
exit /b 1
