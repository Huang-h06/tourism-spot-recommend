#!/bin/bash
set -e

echo "=== 1. 安装 Git LFS ==="
apt-get update -qq && apt-get install -y git-lfs -qq

cd /opt/tourism-app

echo "=== 2. 初始化 LFS 并拉取真实视频文件 ==="
git lfs install
git lfs pull
git lfs checkout

echo "=== 3. 拉取最新代码（包含你的新改动） ==="
git pull origin main

echo "=== 4. 验证视频文件大小 ==="
ls -lh backend/static/videos/xiamen.mp4
ls -lh backend/static/videos/xihu.mp4

echo "=== 5. 停止旧容器，无缓存重建 ==="
docker stop tourism-app 2>/dev/null; docker rm tourism-app 2>/dev/null
docker build --no-cache -t tourism-app .

echo "=== 6. 验证镜像内视频和代码 ==="
echo "--- 视频大小 ---"
docker run --rm tourism-app:latest ls -lh /app/static/videos/xiamen.mp4

echo "--- serve_video 函数是否存在 ---"
docker run --rm tourism-app:latest grep -c "serve_video" /app/app.py

echo "=== 7. 启动容器 ==="
docker run -d \
  --name tourism-app \
  -p 8080:8080 \
  --restart=always \
  -e SUPABASE_URL="https://djuyihywdlqmawzbnzsf.supabase.co" \
  -e SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRqdXlpaHl3ZGxxbWF3emJuenNmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM5NDgyODIsImV4cCI6MjA5OTUyNDI4Mn0.O9DkuKdb2s1T9kzj7O1dE90-FPJoQkgJs7WC7XW8HCA" \
  -e PORT=8080 \
  tourism-app:latest

echo "=== 8. 测试视频接口 ==="
sleep 5
curl -s -I http://localhost:8080/static/videos/xiamen.mp4 | head -10

echo ""
echo "=== 外网访问地址 ==="
echo "http://8.217.15.166:8080"
echo "视频测试: http://8.217.15.166:8080/static/videos/xiamen.mp4"
