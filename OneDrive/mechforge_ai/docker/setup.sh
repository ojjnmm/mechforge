#!/bin/bash
# MechForge CalculiX Solver Setup Script
# 在 WSL/Linux 中安装 Docker 和 CalculiX 求解器

set -e

echo "============================================"
echo "   MechForge CalculiX Solver Setup"
echo "============================================"
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在 WSL 中
if grep -qi microsoft /proc/version 2>/dev/null; then
    IN_WSL=true
    echo -e "${GREEN}[INFO]${NC} 检测到 WSL 环境"
else
    IN_WSL=false
    echo -e "${GREEN}[INFO]${NC} 原生 Linux 环境"
fi

# 1. 检查 Docker
echo
echo "[1/6] 检查 Docker..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} Docker 已安装: $(docker --version)"
else
    echo -e "${YELLOW}[INSTALL]${NC} 安装 Docker..."
    sudo apt-get update
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # 添加 Docker 官方源
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # 启动 Docker
    sudo service docker start || sudo systemctl start docker
    
    # 添加用户到 docker 组
    sudo usermod -aG docker $USER
    
    echo -e "${GREEN}[OK]${NC} Docker 安装完成"
fi

# 2. 检查 Docker Compose
echo
echo "[2/6] 检查 Docker Compose..."
if docker compose version &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} Docker Compose: $(docker compose version)"
elif command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} Docker Compose: $(docker-compose --version)"
else
    echo -e "${YELLOW}[INSTALL]${NC} 安装 Docker Compose..."
    sudo apt-get install -y docker-compose
    echo -e "${GREEN}[OK]${NC} Docker Compose 安装完成"
fi

# 3. 创建工作目录
echo
echo "[3/6] 创建工作目录..."
WORK_DIR="$HOME/mechforge-solver"
mkdir -p "$WORK_DIR"
mkdir -p "$WORK_DIR/calculix-solver"
echo -e "${GREEN}[OK]${NC} 工作目录: $WORK_DIR"

# 4. 检查文件
echo
echo "[4/6] 检查配置文件..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 复制文件
if [ -f "$SCRIPT_DIR/calculix-solver/Dockerfile" ]; then
    cp "$SCRIPT_DIR/calculix-solver/Dockerfile" "$WORK_DIR/calculix-solver/"
    cp "$SCRIPT_DIR/calculix-solver/solver_api.py" "$WORK_DIR/calculix-solver/"
    cp "$SCRIPT_DIR/docker-compose.yml" "$WORK_DIR/"
    cp "$SCRIPT_DIR/nginx.conf" "$WORK_DIR/"
    echo -e "${GREEN}[OK]${NC} 配置文件已复制"
else
    echo -e "${YELLOW}[WARN]${NC} 未找到源文件，将创建默认配置"
    
    # 创建默认 Dockerfile
    cat > "$WORK_DIR/calculix-solver/Dockerfile" << 'DOCKERFILE'
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential gfortran \
    libarpack2-dev libblas-dev liblapack-dev \
    python3 python3-pip curl wget \
    && rm -rf /var/lib/apt/lists/*

# 安装 CalculiX (预编译版本)
RUN apt-get update && apt-get install -y calculix-ccx && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir fastapi uvicorn python-multipart pydantic numpy

WORKDIR /solver
RUN mkdir -p /solver/jobs /solver/results

COPY solver_api.py /solver/solver_api.py

EXPOSE 8080
CMD ["uvicorn", "solver_api:app", "--host", "0.0.0.0", "--port", "8080"]
DOCKERFILE

    echo -e "${GREEN}[OK]${NC} 默认 Dockerfile 已创建"
fi

# 5. 构建镜像
echo
echo "[5/6] 构建 Docker 镜像..."
echo -e "${YELLOW}[INFO]${NC} 这可能需要几分钟..."
cd "$WORK_DIR"

if docker compose build 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} 镜像构建完成"
elif docker-compose build 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} 镜像构建完成"
else
    echo -e "${RED}[ERROR]${NC} 镜像构建失败"
    exit 1
fi

# 6. 启动容器
echo
echo "[6/6] 启动求解器容器..."
if docker compose up -d 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} 容器启动成功"
elif docker-compose up -d 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} 容器启动成功"
else
    echo -e "${RED}[ERROR]${NC} 容器启动失败"
    exit 1
fi

# 等待服务启动
echo
echo -e "${YELLOW}[WAIT]${NC} 等待服务启动..."
sleep 5

# 测试连接
echo
echo "============================================"
echo "   安装完成!"
echo "============================================"
echo
echo -e "${GREEN}求解器服务:${NC}"
echo "  Gateway:  http://localhost:8080"
echo "  Solver 1: http://localhost:8081"
echo "  Solver 2: http://localhost:8082"
echo
echo -e "${GREEN}测试命令:${NC}"
echo "  curl http://localhost:8080/status"
echo
echo -e "${GREEN}在 MechForge 中使用:${NC}"
echo "  /api http://localhost:8080"
echo "  /solve --api"
echo
echo -e "${GREEN}管理命令:${NC}"
echo "  停止: docker compose down"
echo "  日志: docker compose logs -f"
echo "  重启: docker compose restart"
echo