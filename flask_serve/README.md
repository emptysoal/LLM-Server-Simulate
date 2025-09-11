# **Docker Compose** 结合 **Nginx** 实现多容器负载均衡

## 1. 准备 Flask 应用 Docker 镜像

Flask 应用 Docker化，构建镜像（这里命名为 `flask-stream-app:1.0`）：

```bash
cd server_code
docker build -t flask-stream-app:1.0 .
```

## 2. 使用 Docker Compose 启动多个容器

使用相同镜像启动多个服务实例（这里启动 3 个）：

```bash
cd ..
docker-compose up -d
```