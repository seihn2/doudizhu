#!/usr/bin/env python3
"""
启动Web版斗地主游戏
自动启动后端和前端服务
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_requirements():
    """检查环境要求"""
    print("🔍 检查环境要求...")

    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ 需要Python 3.8+版本")
        return False

    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")

    # 检查Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js版本: {result.stdout.strip()}")
        else:
            print("❌ 未安装Node.js")
            return False
    except FileNotFoundError:
        print("❌ 未安装Node.js")
        return False

    # 检查npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm版本: {result.stdout.strip()}")
        else:
            print("❌ 未安装npm")
            return False
    except FileNotFoundError:
        print("❌ 未安装npm")
        return False

    return True

def install_backend_dependencies():
    """安装后端依赖"""
    print("\n📦 安装后端依赖...")

    backend_dir = Path(__file__).parent / "backend"
    requirements_file = backend_dir / "requirements.txt"

    if not requirements_file.exists():
        print("❌ 找不到requirements.txt文件")
        return False

    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ], cwd=backend_dir)

        if result.returncode == 0:
            print("✅ 后端依赖安装成功")
            return True
        else:
            print("❌ 后端依赖安装失败")
            return False
    except Exception as e:
        print(f"❌ 安装后端依赖时出错: {e}")
        return False

def install_frontend_dependencies():
    """安装前端依赖"""
    print("\n📦 安装前端依赖...")

    frontend_dir = Path(__file__).parent / "frontend"
    package_json = frontend_dir / "package.json"

    if not package_json.exists():
        print("❌ 找不到package.json文件")
        return False

    try:
        result = subprocess.run(['npm', 'install'], cwd=frontend_dir)

        if result.returncode == 0:
            print("✅ 前端依赖安装成功")
            return True
        else:
            print("❌ 前端依赖安装失败")
            return False
    except Exception as e:
        print(f"❌ 安装前端依赖时出错: {e}")
        return False

def start_backend():
    """启动后端服务"""
    print("\n🚀 启动后端服务...")

    backend_dir = Path(__file__).parent / "backend"
    main_py = backend_dir / "main.py"

    if not main_py.exists():
        print("❌ 找不到后端main.py文件")
        return None

    try:
        # 在新窗口启动后端
        if os.name == 'nt':  # Windows
            process = subprocess.Popen([
                sys.executable, str(main_py)
            ], cwd=backend_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Linux/Mac
            process = subprocess.Popen([
                'gnome-terminal', '--', sys.executable, str(main_py)
            ], cwd=backend_dir)

        print("✅ 后端服务启动中... (端口: 8000)")
        return process
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("\n🚀 启动前端服务...")

    frontend_dir = Path(__file__).parent / "frontend"

    try:
        # 在新窗口启动前端
        if os.name == 'nt':  # Windows
            process = subprocess.Popen([
                'npm', 'start'
            ], cwd=frontend_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Linux/Mac
            process = subprocess.Popen([
                'gnome-terminal', '--', 'npm', 'start'
            ], cwd=frontend_dir)

        print("✅ 前端服务启动中... (端口: 3000)")
        return process
    except Exception as e:
        print(f"❌ 启动前端服务失败: {e}")
        return None

def wait_for_services():
    """等待服务启动"""
    print("\n⏳ 等待服务启动...")

    import requests
    import time

    # 等待后端启动
    for i in range(30):  # 最多等待30秒
        try:
            response = requests.get('http://localhost:8000/health', timeout=1)
            if response.status_code == 200:
                print("✅ 后端服务已启动")
                break
        except:
            pass

        time.sleep(1)
        print(f"⏳ 等待后端启动... ({i+1}/30)")
    else:
        print("⚠️ 后端服务启动超时，但继续尝试访问前端")

    # 等待前端启动（简单等待）
    time.sleep(10)
    print("✅ 前端服务应该已启动")

def open_browser():
    """打开浏览器"""
    print("\n🌐 打开游戏页面...")

    try:
        webbrowser.open('http://localhost:3000')
        print("✅ 浏览器已打开，享受游戏！")
    except Exception as e:
        print(f"❌ 打开浏览器失败: {e}")
        print("请手动访问: http://localhost:3000")

def main():
    """主函数"""
    print("🃏 AI斗地主 Web版启动器")
    print("=" * 50)

    # 检查环境
    if not check_requirements():
        print("\n❌ 环境检查失败，请安装所需软件")
        input("按回车键退出...")
        return

    # 询问是否安装依赖
    install_deps = input("\n🤔 是否需要安装/更新依赖？(y/N): ").lower().strip()

    if install_deps in ['y', 'yes']:
        # 安装依赖
        if not install_backend_dependencies():
            print("\n❌ 后端依赖安装失败")
            input("按回车键退出...")
            return

        if not install_frontend_dependencies():
            print("\n❌ 前端依赖安装失败")
            input("按回车键退出...")
            return

    # 启动服务
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ 无法启动后端服务")
        input("按回车键退出...")
        return

    time.sleep(3)  # 等待后端启动

    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ 无法启动前端服务")
        input("按回车键退出...")
        return

    # 等待服务启动
    wait_for_services()

    # 打开浏览器
    open_browser()

    print("\n" + "=" * 50)
    print("🎮 游戏启动完成！")
    print("📱 前端地址: http://localhost:3000")
    print("⚙️ 后端地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("=" * 50)
    print("\n按Ctrl+C退出所有服务")

    try:
        # 等待用户中断
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 正在关闭服务...")

        try:
            if backend_process:
                backend_process.terminate()
            if frontend_process:
                frontend_process.terminate()
        except:
            pass

        print("✅ 服务已关闭，再见！")

if __name__ == "__main__":
    main()