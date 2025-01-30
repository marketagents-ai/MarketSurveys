@echo off
setlocal enabledelayedexpansion
rem Script to run market simulation with parallel orchestration, dashboard, and time tracking

rem Function to check if a port is in use
:check_port
set port=%1
netstat -ano | findstr :!port! >nul
if !errorlevel! equ 0 (
    exit /b 0 rem Port is in use
) else (
    exit /b 1 rem Port is free
)

rem File names for the Python scripts
set ORCHESTRATOR_SCRIPT=market_agents\orchestrators\meta_orchestrator.py
set DASHBOARD_SCRIPT=market_agents\agents\db\dashboard\dashboard.py
set GROUPCHAT_API_SCRIPT=market_agents\orchestrators\group_chat\groupchat_api.py
set DASHBOARD_PORT=8000
set GROUPCHAT_API_PORT=8001

rem Check if the Python scripts exist
for %%s in (%ORCHESTRATOR_SCRIPT% %DASHBOARD_SCRIPT% %GROUPCHAT_API_SCRIPT%) do (
    if not exist "%%s" (
        echo Error: %%s not found!
        exit /b 1
    )
)

rem Function to check API health
:check_api_health
set port=%1
set retries=3
set wait_time=2
for /L %%i in (1,1,!retries!) do (
    curl -s "http://localhost:!port!/health" >nul 2>&1
    if !errorlevel! equ 0 (
        exit /b 0 rem API is healthy
    )
    echo Attempt %%i: Waiting for API to become healthy...
    timeout /t !wait_time! >nul
)
exit /b 1 rem API failed health check


rem Check and start GroupChat API if needed
call :check_port %GROUPCHAT_API_PORT%
if !errorlevel! equ 0 (
    echo GroupChat API is already running at http://localhost:%GROUPCHAT_API_PORT%
    set GROUPCHAT_STARTED=false
) else (
    echo Starting GroupChat API...
    start /B python %GROUPCHAT_API_SCRIPT%
    for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo list /v ^| find /i "PID:"') do set GROUPCHAT_PID=%%i
    set GROUPCHAT_STARTED=true

    rem Check if API becomes healthy
    call :check_api_health %GROUPCHAT_API_PORT%
    if !errorlevel! neq 0  (
        echo Failed to start GroupChat API. Killing process...
        taskkill /PID %GROUPCHAT_PID%
        exit 1
    )
    echo GroupChat API is running at http://localhost:%GROUPCHAT_API_PORT%
)

rem Check and start dashboard if needed
call :check_port %DASHBOARD_PORT%
if !errorlevel! equ 0 (
    echo Dashboard is already running at http://localhost:%DASHBOARD_PORT%
    set DASHBOARD_STARTED=false
) else (
    echo Starting dashboard...
    start /B python %DASHBOARD_SCRIPT%
    for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo list /v ^| find /i "PID:"') do set DASHBOARD_PID=%%i
    set DASHBOARD_STARTED=true

    timeout /t 2
    echo Dashboard is running at http://localhost:%DASHBOARD_PORT%
)

rem Get the start time
for /f "tokens=1-4 delims=:." %%a in ("%time%") do (
    set /a start_time=(((%%a*60)+1%%b)*60+1%%c)*100+1%%d-5000
)
rem Run the orchestrator script
echo Starting market simulation with parallel orchestration...
python "%ORCHESTRATOR_SCRIPT%" > simulation_output.log 2>&1
set orchestrator_exit_code=%errorlevel%
type simulation_output.log

rem Get the end time and calculate duration
for /f "tokens=1-4 delims=:." %%a in ("%time%") do (
    set /a end_time=(((%%a*60)+1%%b)*60+1%%c)*100+1%%d-5000
)
set /a duration=%end_time% - %start_time%
set /a duration_seconds=%duration% / 100

rem Print results
echo ----------------------------------------
echo Simulation completed with exit code: %orchestrator_exit_code%
echo Total execution time: %duration_seconds% seconds
echo ----------------------------------------
echo Full output has been saved to simulation_output.log
echo ----------------------------------------

if %orchestrator_exit_code% neq 0 (
    echo Error: Orchestrator script failed with exit code %orchestrator_exit_code%
) else (
    echo Simulation completed successfully.
)

rem Cleanup services that we started
rem NOTE: Batch scripts don't support OR statements in if/else checks, so we need to check each separately. 

if "%DASHBOARD_STARTED%"=="true" (
    echo Press Enter to stop services and exit.
    pause > nul
    taskkill /PID %DASHBOARD_PID%
    echo Dashboard stopped.
) else (
    echo Services were already running and will continue running.
)

if "%GROUPCHAT_STARTED%"=="true" (
    echo Press Enter to stop services and exit.
    pause > nul
    taskkill /PID %GROUPCHAT_PID%
    echo GroupChat API stopped.
) else (
    echo Services were already running and will continue running.
)

exit %orchestrator_exit_code%