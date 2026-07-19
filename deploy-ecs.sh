#!/bin/bash
set -e

# ==============================================
# 旅游景点推荐项目 - ECS 一键部署脚本
# 适用：Ubuntu 22.04/24.04 + Docker
# ==============================================

PROJECT_DIR="/opt/tourism-app"
GIT_REPO="https://github.com/Huang-h06/tourism-spot-recommend.git"
PORT=8080

echo "=== Step 1: 安装 Docker & Git LFS ==="
sudo apt-get update -y
sudo apt-get install -y docker.io git git-lfs curl
sudo systemctl enable docker --now

echo "=== Step 2: 拉取项目代码（含 Git LFS 视频文件） ==="
git lfs install
if [ -d "$PROJECT_DIR" ]; then
    echo "目录已存在，执行 git pull..."
    cd "$PROJECT_DIR"
    git pull origin main
    git lfs pull
else
    sudo git clone "$GIT_REPO" "$PROJECT_DIR"
    sudo chown -R $(whoami):$(whoami) "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    git lfs pull
fi

echo "=== Step 3: 检查 Supabase 环境变量 ==="
if [ ! -f ".env" ]; then
    echo "ERROR: 缺少 .env 文件！"
    echo "请创建 .env 并写入："
    echo "SUPABASE_URL=https://your-project.supabase.co"
    echo "SUPABASE_KEY=your-anon-key"
    exit 1
fi

if ! grep -q "SUPABASE_URL" .env; then
    echo "WARNING: .env 中未找到 SUPABASE_URL，请检查配置"
fi

echo "=== Step 4: 构建 Docker 镜像 ==="
sudo docker build --no-cache -t tourism-app:latest .

echo "=== Step 5: 停止旧容器并启动新容器 ==="
sudo docker stop tourism-app 2>/dev/null || true
sudo docker rm tourism-app 2>/dev/null || true
sudo docker run -d \
    --name tourism-app \
    -p $PORT:8080 \
    --restart=always \
    tourism-app:latest

echo "=== Step 6: 等待启动并验证 ==="
sleep 8
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT || echo "000")

if [ "$HEALTH" = "200" ] || [ "$HEALTH" = "302" ]; then
    echo "部署成功！HTTP 状态码: $HEALTH"
    echo "外网访问地址: http://8.217.15.166:$PORT"
else
    echo "验证返回 HTTP $HEALTH，查看日志排查:"
    echo "   sudo docker logs tourism-app"
fi

echo ""
echo "=== 常用运维命令 ==="
echo "查看日志:     sudo docker logs -f tourism-app"
echo "重启容器:     sudo docker restart tourism-app"
echo "停止容器:     sudo docker stop tourism-app"
echo "更新代码:     cd $PROJECT_DIR && git pull origin main && git lfs pull && sudo docker build --no-cache -t tourism-app . && sudo docker stop tourism-app && sudo docker rm tourism-app && sudo docker run -d --name tourism-app -p 8080:8080 --restart=always tourism-app:latest"
