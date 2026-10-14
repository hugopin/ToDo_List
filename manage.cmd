@echo off
setlocal
if "%~1"=="" goto help
if /I "%~1"=="help" goto help
if /I "%~1"=="install" goto prepare
if /I "%~1"=="run" goto prepare
if /I "%~1"=="test" goto prepare
if /I "%~1"=="check" goto prepare
echo Acao invalida. Use install, run, test ou check.
exit /b 2

:prepare
pushd "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Ambiente virtual ausente. Execute: py -m venv .venv
    popd
    exit /b 1
)
if /I "%~1"=="install" goto install
if /I "%~1"=="run" goto run
if /I "%~1"=="test" goto test
goto check

:install
".venv\Scripts\python.exe" -m pip install -r requirements.txt
goto finish
:run
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
goto finish
:test
".venv\Scripts\python.exe" -m pytest tests/test_tasks.py -v
goto finish
:check
".venv\Scripts\python.exe" -m pip check
goto finish

:finish
set "taskExitCode=%errorlevel%"
popd
exit /b %taskExitCode%

:help
echo Uso: manage.cmd install ^| run ^| test ^| check
echo Crie primeiro a .venv com: py -m venv .venv
exit /b 0
