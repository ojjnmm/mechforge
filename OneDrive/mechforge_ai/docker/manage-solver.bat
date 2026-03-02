@echo off
REM MechForge Solver Container - Quick Start
REM 快速启动求解器容器

echo ============================================
echo    MechForge Solver - Quick Start
echo ============================================
echo.

REM 检查 WSL Docker
wsl docker ps >nul 2>&1
if errorlevel 1 (
    echo 启动 Docker 服务...
    wsl sudo service docker start
    timeout /t 3 >nul
)

REM 检查容器状态
echo 检查容器状态...
wsl docker ps -a --filter "name=mechforge" --format "{{.Names}}: {{.Status}}"

echo.
echo 选择操作:
echo   1. 启动求解器
echo   2. 停止求解器  
echo   3. 查看日志
echo   4. 重启求解器
echo   5. 测试连接
echo   6. 退出
echo.

set /p choice="请选择 (1-6): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto logs
if "%choice%"=="4" goto restart
if "%choice%"=="5" goto test
if "%choice%"=="6" goto end

:start
echo.
echo 启动求解器容器...
wsl cd ~/mechforge-solver && docker compose up -d
echo.
echo 等待服务启动...
timeout /t 5 >nul
goto status

:stop
echo.
echo 停止求解器容器...
wsl cd ~/mechforge-solver && docker compose down
goto end

:logs
echo.
echo 显示日志 (Ctrl+C 退出)...
wsl cd ~/mechforge-solver && docker compose logs -f
goto end

:restart
echo.
echo 重启求解器容器...
wsl cd ~/mechforge-solver && docker compose restart
timeout /t 5 >nul
goto status

:test
echo.
echo 测试连接...
echo.
echo Gateway:
curl -s http://localhost:8080/status 2>nul || echo "  未连接"
echo.
echo Solver 1:
curl -s http://localhost:8081/status 2>nul || echo "  未连接"
echo.
echo Solver 2:
curl -s http://localhost:8082/status 2>nul || echo "  未连接"
goto end

:status
echo.
echo 容器状态:
wsl docker ps --filter "name=mechforge" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
goto end

:end
echo.
pause