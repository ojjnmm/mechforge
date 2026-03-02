# MechForge CalculiX Solver Container
# 基于 Ubuntu 22.04 + CalculiX 2.21 + FastAPI

FROM ubuntu:22.04

LABEL maintainer="MechForge AI"
LABEL description="CalculiX FEA Solver with REST API"

# 避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive

# 安装依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    libarpack2-dev \
    libblas-dev \
    liblapack-dev \
    libspooles-dev \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 编译安装 CalculiX 2.21
WORKDIR /opt
RUN wget -q https://www.dhondt.de/ccx_2.21.src.tar.bz2 && \
    tar xjf ccx_2.21.src.tar.bz2 && \
    cd CalculiX/ccx_2.21/src && \
    make -j$(nproc) && \
    cp ccx_2.21 /usr/local/bin/ccx && \
    cd /opt && rm -rf ccx_2.21.src.tar.bz2 CalculiX

# 创建 Python 虚拟环境
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 安装 Python 依赖
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    pydantic \
    numpy

# 创建工作目录
WORKDIR /solver
RUN mkdir -p /solver/jobs /solver/results

# 复制 API 服务
COPY solver_api.py /solver/solver_api.py

# 暴露端口
EXPOSE 8080

# 启动 API 服务
CMD ["uvicorn", "solver_api:app", "--host", "0.0.0.0", "--port", "8080"]