@echo off
REM MechForge Solver Container Setup Script
REM 在 WSL Ubuntu 中安装 Docker 和 CalculiX 求解器容器

echo ============================================
echo    MechForge CalculiX Solver Setup
echo ============================================
echo.

REM 检查 WSL
echo [1/5] 检查 WSL...
wsl --list --verbose 2>nul
if errorlevel 1 (
    echo WSL 未安装，正在安装 Ubuntu...
    wsl --install -d Ubuntu
    echo 请重启电脑后重新运行此脚本
    pause
    exit /b 1
)

echo [OK] WSL 已安装
echo.

REM 检查 Docker
echo [2/5] 检查 Docker...
wsl docker --version 2>nul
if errorlevel 1 (
    echo Docker 未安装，正在安装...
    wsl sudo apt-get update
    wsl sudo apt-get install -y docker.io docker-compose
    wsl sudo service docker start
    wsl sudo usermod -aG docker $USER
)

echo [OK] Docker 已就绪
echo.

REM 创建工作目录
echo [3/5] 准备文件...
wsl mkdir -p ~/mechforge-solver
wsl mkdir -p ~/mechforge-solver/calculix-solver

REM 复制文件到 WSL
copy /Y "%~dp0calculix-solver\Dockerfile" "\\wsl$\Ubuntu\home\%USERNAME%\mechforge-solver\calculix-solver\"
copy /Y "%~dp0calculix-solver\solver_api.py" "\\wsl$\Ubuntu\home\%USERNAME%\mechforge-solver\calculix-solver\"
copy /Y "%~dp0docker-compose.yml" "\\wsl$\Ubuntu\home\%USERNAME%\mechforge-solver\"
copy /Y "%~dp0nginx.conf" "\\wsl$\Ubuntu\home\%USERNAME%\mechforge-solver\"

echo [OK] 文件已准备
echo.

REM 构建镜像
echo [4/5] 构建 Docker 镜像 (这需要几分钟)...
wsl cd ~/mechforge-solver && sudo docker-compose build
if errorlevel 1 (
    echo 构建失败，请检查网络连接
    pause
    exit /b 1
)

echo [OK] 镜像构建完成
echo.

REM 启动容器
echo [5/5] 启动求解器容器...
wsl cd ~/mechforge-solver && sudo docker-compose up -d

echo.
echo ============================================
echo    安装完成!
echo ============================================
echo.
echo 求解器服务:
echo   - Gateway: http://localhost:8080
echo   - Solver 1: http://localhost:8081
echo   - Solver 2: http://localhost:8082
echo.
echo 测试命令:
echo   curl http://localhost:8080/status
echo.
echo 在 MechForge 中使用:
echo   /api http://localhost:8080
echo   /solve --api
echo.
pause