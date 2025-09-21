"""
AI斗地主游戏主程序
本地单人版斗地主游戏，支持与AI对手对战
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.console_ui import ConsoleUI


def main():
    """主程序入口"""
    try:
        # 检查依赖
        try:
            import colorama
            import tabulate
        except ImportError as e:
            print("缺少依赖包，请运行: pip install -r requirements.txt")
            print(f"错误详情: {e}")
            return

        # 启动游戏界面
        ui = ConsoleUI()
        ui.start()

    except KeyboardInterrupt:
        print("\n\n游戏被用户中断")
    except Exception as e:
        print(f"\n游戏发生致命错误: {e}")
        print("请检查错误信息或联系开发者")


if __name__ == "__main__":
    main()