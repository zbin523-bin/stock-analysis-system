# 群晖快速部署脚本

echo "========================================="
echo "股票投资组合管理系统 - 群晖部署脚本"
echo "========================================="

# 检查是否为root用户
if [[ $EUID -ne 0 ]]; then
   echo "请使用root权限运行此脚本"
   echo "使用方法: sudo ./deploy.sh"
   exit 1
fi

# 设置变量
PROJECT_DIR="/volume1/docker/stock-portfolio"
BACKUP_DIR="/volume1/docker/backup"

echo "1. 创建备份目录..."
mkdir -p $BACKUP_DIR

echo "2. 备份现有配置（如果存在）..."
if [ -d "$PROJECT_DIR" ]; then
    echo "发现现有配置，正在备份..."
    cp -r $PROJECT_DIR $BACKUP_DIR/stock-portfolio-$(date +%Y%m%d-%H%M%S)
fi

echo "3. 创建项目目录..."
mkdir -p $PROJECT_DIR

echo "4. 进入项目目录..."
cd $PROJECT_DIR

echo "5. 停止现有服务..."
if [ -f "docker-compose.yml" ]; then
    docker-compose down
fi

echo "6. 清理旧镜像..."
docker system prune -f

echo "7. 构建并启动服务..."
docker-compose up -d --build

echo "8. 等待服务启动..."
sleep 30

echo "9. 检查服务状态..."
docker-compose ps

echo "10. 测试API连接..."
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ API服务正常运行"
else
    echo "❌ API服务启动失败，请检查日志"
fi

echo "========================================="
echo "部署完成！"
echo "前端地址: http://$(hostname -I | awk '{print $1}'):3000"
echo "API地址: http://$(hostname -I | awk '{print $1}'):5000"
echo "========================================="

echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
echo "重启服务: docker-compose restart"