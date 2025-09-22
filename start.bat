@echo off
echo 🃏 AI斗地主游戏启动器
echo ========================

echo 正在启动后端服务...
start "Backend Server" cmd /k "cd backend && python main.py"

echo 等待后端启动...
timeout /t 5 /nobreak >nul

echo 正在启动前端服务...
start "Frontend Server" cmd /k "cd frontend && npm start"

echo 等待前端启动...
timeout /t 10 /nobreak >nul

echo 正在打开浏览器...
start http://localhost:3000

echo.
echo ✅ 游戏启动完成！
echo 📱 前端地址: http://localhost:3000
echo ⚙️ 后端地址: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs
echo.
echo 按任意键关闭此窗口...
pause >nul