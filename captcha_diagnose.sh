#!/bin/bash
# 验证码系统诊断脚本

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "         VideoSite 验证码系统诊断"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. 检查后端服务
echo "1️⃣  检查后端服务 (http://localhost:8000)..."
if curl -s http://localhost:8000/api/docs > /dev/null 2>&1; then
    echo "   ✅ 后端服务运行正常"
else
    echo "   ❌ 后端服务未运行或无法访问"
    echo "   💡 解决方法:"
    echo "      cd /home/eric/video/backend"
    echo "      source venv/bin/activate"
    echo "      uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  后端服务未运行，无法继续检查"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
fi
echo ""

# 2. 检查验证码API
echo "2️⃣  检查验证码API (GET /api/v1/captcha/)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/captcha/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ 验证码API正常 (HTTP $HTTP_CODE)"

    # 检查响应头
    CAPTCHA_ID=$(curl -s -I http://localhost:8000/api/v1/captcha/ | grep -i "x-captcha-id" | cut -d' ' -f2 | tr -d '\r')
    if [ -n "$CAPTCHA_ID" ]; then
        echo "   ✅ X-Captcha-ID 响应头正常: ${CAPTCHA_ID:0:36}"
    else
        echo "   ⚠️  警告: X-Captcha-ID 响应头缺失"
    fi
else
    echo "   ❌ 验证码API异常 (HTTP $HTTP_CODE)"
    echo "   💡 可能的原因:"
    echo "      - 路由未注册"
    echo "      - Redis 未运行"
    echo "      - 权限问题"
fi
echo ""

# 3. 检查Redis
echo "3️⃣  检查Redis连接..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "   ✅ Redis 连接正常 (PONG)"

        # 检查Redis中的验证码数量
        CAPTCHA_COUNT=$(redis-cli KEYS "captcha:*" 2>/dev/null | wc -l)
        echo "   📊 当前Redis中验证码数量: $CAPTCHA_COUNT"
    else
        echo "   ❌ Redis 未运行或无法连接"
        echo "   💡 解决方法:"
        echo "      sudo systemctl start redis"
        echo "      或"
        echo "      docker-compose -f docker-compose.dev.yml up -d redis"
    fi
else
    echo "   ⚠️  redis-cli 未安装，跳过检查"
fi
echo ""

# 4. 检查前端服务
echo "4️⃣  检查前端服务 (http://localhost:3001)..."
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo "   ✅ 前端服务运行正常"
else
    echo "   ❌ 前端服务未运行"
    echo "   💡 解决方法:"
    echo "      cd /home/eric/video/admin-frontend"
    echo "      pnpm run dev"
fi
echo ""

# 5. 测试验证码生成速度
echo "5️⃣  测试验证码生成性能..."
if [ "$HTTP_CODE" = "200" ]; then
    START_TIME=$(date +%s%N)
    curl -s -o /dev/null http://localhost:8000/api/v1/captcha/
    END_TIME=$(date +%s%N)
    DURATION=$(( (END_TIME - START_TIME) / 1000000 ))

    if [ $DURATION -lt 1000 ]; then
        echo "   ✅ 响应速度正常: ${DURATION}ms"
    elif [ $DURATION -lt 3000 ]; then
        echo "   ⚠️  响应偏慢: ${DURATION}ms"
    else
        echo "   ❌ 响应过慢: ${DURATION}ms"
        echo "   💡 可能需要检查Redis性能或服务器负载"
    fi
else
    echo "   ⏭️  跳过（API不可用）"
fi
echo ""

# 6. 检查CORS配置
echo "6️⃣  检查CORS配置..."
ORIGIN_HEADER=$(curl -s -I -H "Origin: http://localhost:3001" http://localhost:8000/api/v1/captcha/ | grep -i "access-control-allow-origin")
if [ -n "$ORIGIN_HEADER" ]; then
    echo "   ✅ CORS 配置正常"
    echo "      $ORIGIN_HEADER" | tr -d '\r'
else
    echo "   ⚠️  未检测到 CORS 头（可能使用了 Vite 代理）"
fi
echo ""

# 7. 检查Vite代理配置
echo "7️⃣  检查Vite代理配置..."
if [ -f "/home/eric/video/admin-frontend/vite.config.ts" ]; then
    if grep -q "'/api'" "/home/eric/video/admin-frontend/vite.config.ts"; then
        echo "   ✅ Vite 代理配置存在"
        grep -A 3 "'/api'" "/home/eric/video/admin-frontend/vite.config.ts" | sed 's/^/      /'
    else
        echo "   ❌ Vite 代理配置缺失"
    fi
else
    echo "   ⚠️  vite.config.ts 文件未找到"
fi
echo ""

# 总结
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "         诊断完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 验证码系统工作正常！"
    echo ""
    echo "📝 如果前端仍无法加载验证码，请："
    echo "   1. 打开浏览器开发者工具 (F12)"
    echo "   2. 切换到 Network 标签"
    echo "   3. 访问登录页面"
    echo "   4. 查看 /api/v1/captcha/ 请求的状态"
    echo "   5. 检查控制台 Console 是否有错误"
else
    echo "❌ 验证码系统存在问题"
    echo ""
    echo "🔧 建议修复步骤："
    echo "   1. 确保后端服务正在运行"
    echo "   2. 确保 Redis 正在运行"
    echo "   3. 检查后端日志是否有错误"
    echo "   4. 查看完整文档: CAPTCHA_TROUBLESHOOTING.md"
fi
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
