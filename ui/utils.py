"""
UI工具函数模块
提供界面显示相关的工具函数
"""

import os
import sys
from typing import List, Dict, Any
from colorama import init, Fore, Back, Style

# 初始化colorama
init(autoreset=True)


class Colors:
    """颜色常量"""
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    BRIGHT = Style.BRIGHT
    RESET = Style.RESET_ALL


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_title(title: str):
    """打印标题"""
    title_len = len(title)
    border = "=" * (title_len + 4)

    print(f"\n{Colors.CYAN}{border}")
    print(f"  {title}")
    print(f"{border}{Colors.RESET}\n")


def print_separator(char: str = "-", length: int = 50):
    """打印分隔线"""
    print(f"{Colors.YELLOW}{char * length}{Colors.RESET}")


def print_error(message: str):
    """打印错误信息"""
    print(f"{Colors.RED}[错误] {message}{Colors.RESET}")


def print_success(message: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}[成功] {message}{Colors.RESET}")


def print_warning(message: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}[警告] {message}{Colors.RESET}")


def print_info(message: str):
    """打印信息"""
    print(f"{Colors.BLUE}[信息] {message}{Colors.RESET}")


def format_card_display(cards: List[any]) -> str:
    """格式化卡牌显示"""
    if not cards:
        return "无"

    card_strs = []
    for card in cards:
        card_str = str(card)
        # 根据花色添加颜色
        if hasattr(card, 'suit') and card.suit:
            if card.suit.value in ['♥', '♦']:  # 红色花色
                card_str = f"{Colors.RED}{card_str}{Colors.RESET}"
            else:  # 黑色花色
                card_str = f"{Colors.WHITE}{card_str}{Colors.RESET}"
        elif hasattr(card, 'value') and card.value in [16, 17]:  # 王牌
            card_str = f"{Colors.MAGENTA}{card_str}{Colors.RESET}"

        card_strs.append(card_str)

    return " ".join(card_strs)


def create_table(headers: List[str], rows: List[List[str]], title: str = None) -> str:
    """创建表格"""
    from tabulate import tabulate

    table = tabulate(rows, headers=headers, tablefmt="grid")

    if title:
        lines = table.split('\n')
        title_line = f"{Colors.CYAN}{title}{Colors.RESET}"
        return f"\n{title_line}\n{table}\n"

    return f"\n{table}\n"


def print_game_status(game_state: Dict[str, Any]):
    """打印游戏状态"""
    print_separator()
    print(f"{Colors.BRIGHT}游戏状态:{Colors.RESET}")
    print(f"阶段: {game_state.get('phase', '未知')}")
    print(f"回合: {game_state.get('round_count', 0)}")

    if game_state.get('landlord_idx') is not None:
        print(f"地主: 玩家{game_state['landlord_idx'] + 1}")

    print(f"当前玩家: 玩家{game_state.get('current_player_idx', 0) + 1}")
    print_separator()


def print_player_info(players: List[Any], current_idx: int = None):
    """打印玩家信息"""
    rows = []
    for i, player in enumerate(players):
        name = player.name
        role = "[地主]" if player.is_landlord else "[农民]"
        cards_count = f"{len(player.hand.cards)}张"
        current_marker = "<- 当前" if i == current_idx else ""

        rows.append([f"玩家{i+1}", name, role, cards_count, current_marker])

    headers = ["编号", "姓名", "角色", "手牌", "状态"]
    print(create_table(headers, rows, "玩家信息"))


def print_hand_cards(cards: List[Any], title: str = "你的手牌"):
    """打印手牌"""
    print(f"\n{Colors.BRIGHT}{title}:{Colors.RESET}")
    print(f"  {format_card_display(cards)}")
    print(f"  共 {len(cards)} 张\n")


def print_last_play(last_play_info: Dict[str, Any]):
    """打印上一手牌信息"""
    if not last_play_info or not last_play_info.get('cards'):
        print(f"{Colors.YELLOW}还没有人出牌{Colors.RESET}\n")
        return

    player_name = last_play_info.get('player_name', '未知玩家')
    card_type = last_play_info.get('card_type', '未知牌型')
    cards = last_play_info.get('cards', [])

    print(f"{Colors.BRIGHT}上一手牌:{Colors.RESET}")
    print(f"  {player_name} 出了 {card_type}")
    print(f"  {format_card_display(cards)}\n")


def get_user_input(prompt: str, valid_choices: List[str] = None) -> str:
    """获取用户输入"""
    while True:
        user_input = input(f"{Colors.BRIGHT}{prompt}{Colors.RESET}").strip()

        if valid_choices is None:
            return user_input

        if user_input.lower() in [choice.lower() for choice in valid_choices]:
            return user_input

        print_error(f"请输入有效选择: {', '.join(valid_choices)}")


def show_menu(title: str, options: List[str]) -> int:
    """显示菜单并获取用户选择"""
    print_title(title)

    for i, option in enumerate(options, 1):
        print(f"{Colors.BRIGHT}{i}.{Colors.RESET} {option}")

    print()

    while True:
        try:
            choice = int(input(f"{Colors.BRIGHT}请选择 (1-{len(options)}): {Colors.RESET}"))
            if 1 <= choice <= len(options):
                return choice - 1
            else:
                print_error(f"请输入 1 到 {len(options)} 之间的数字")
        except ValueError:
            print_error("请输入有效的数字")


def print_game_result(result: Dict[str, Any]):
    """打印游戏结果"""
    clear_screen()
    print_title("游戏结束")

    result_text = result.get('result', '未知结果')
    winner = result.get('winner', '未知')
    landlord = result.get('landlord', '未知')
    scores = result.get('scores', {})
    rounds = result.get('rounds', 0)

    print(f"{Colors.BRIGHT}游戏结果: {Colors.GREEN if '地主' in result_text else Colors.BLUE}{result_text}{Colors.RESET}")
    print(f"获胜者: {Colors.YELLOW}{winner}{Colors.RESET}")
    print(f"地主: {landlord}")
    print(f"游戏回合数: {rounds}")
    print()

    # 显示积分
    if scores:
        print_title("积分情况")
        score_rows = []
        for player_name, score in scores.items():
            score_color = Colors.GREEN if score > 0 else Colors.RED if score < 0 else Colors.WHITE
            score_rows.append([player_name, f"{score_color}{score:+d}{Colors.RESET}"])

        print(create_table(["玩家", "积分"], score_rows))


def wait_for_enter(message: str = "按回车键继续..."):
    """等待用户按回车"""
    input(f"{Colors.CYAN}{message}{Colors.RESET}")


def print_ascii_art():
    """打印ASCII艺术字"""
    art = f"""{Colors.CYAN}
    ========================================
    =              AI 斗地主               =
    =                                      =
    =        智能对战，精彩对局！          =
    ========================================
    {Colors.RESET}"""
    print(art)


def show_help():
    """显示帮助信息"""
    help_text = f"""
{Colors.BRIGHT}游戏帮助{Colors.RESET}

{Colors.YELLOW}基本玩法:{Colors.RESET}
- 三人游戏，一人当地主，其余两人为农民
- 地主先出牌，按逆时针方向轮流出牌
- 玩家可以选择跟牌或过牌
- 先出完手中所有牌的一方获胜

{Colors.YELLOW}牌型说明:{Colors.RESET}
- 单张：任意一张牌
- 对子：两张相同点数的牌
- 三张：三张相同点数的牌
- 三带一：三张相同点数的牌+一张单牌
- 三带对：三张相同点数的牌+一对牌
- 顺子：五张或更多连续的牌
- 连对：三对或更多连续的对子
- 飞机：连续的三张牌
- 炸弹：四张相同点数的牌
- 王炸：大王+小王

{Colors.YELLOW}输入格式:{Colors.RESET}
- 出牌时输入牌的点数，用空格分隔
- 例如：3 4 5（顺子）、7 7（对子）
- 输入'pass'或'过'跳过出牌

{Colors.YELLOW}特殊牌:{Colors.RESET}
- 数字3-10：直接输入数字
- J、Q、K、A、2：输入字母或数字
- 小王：输入'小王'或'joker'
- 大王：输入'大王'或'JOKER'
"""
    print(help_text)


if __name__ == "__main__":
    # 测试UI工具函数
    print_ascii_art()
    print_title("测试标题")
    print_success("成功消息")
    print_error("错误消息")
    print_warning("警告消息")
    print_info("信息消息")
    print_separator()

    # 测试菜单
    choice = show_menu("测试菜单", ["选项1", "选项2", "选项3"])
    print(f"你选择了: {choice}")

    # 测试帮助
    show_help()