#!/usr/bin/env python3
"""
个人微习惯追踪器 (Micro-Habit Tracker)

一个命令行习惯追踪应用，帮助用户记录和管理日常微习惯。
数据使用 JSON 文件本地存储。
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 数据文件路径
DATA_FILE = "habits.json"


def load_data() -> Dict:
    """
    加载习惯数据。如果文件不存在，创建初始数据结构。
    
    Returns:
        Dict: 包含习惯数据的字典
    """
    if not os.path.exists(DATA_FILE):
        return {"habits": {}}
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"警告：读取数据文件出错 ({e})，将创建新数据文件。")
        return {"habits": {}}


def save_data(data: Dict) -> None:
    """
    保存习惯数据到 JSON 文件。
    
    Args:
        data: 要保存的习惯数据字典
    """
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"错误：无法保存数据 ({e})")


def add_habit(data: Dict, habit_name: str) -> bool:
    """
    添加新习惯。
    
    Args:
        data: 习惯数据字典
        habit_name: 习惯名称
        
    Returns:
        bool: 添加成功返回 True，已存在返回 False
    """
    if habit_name in data["habits"]:
        return False
    
    data["habits"][habit_name] = {
        "created_at": datetime.now().isoformat(),
        "check_ins": []
    }
    return True


def check_in_habit(data: Dict, habit_name: str) -> tuple:
    """
    为习惯打卡。
    逻辑：同一天允许多次打卡（记录每次打卡时间），
    但连续天数计算基于是否有至少一次打卡。
    
    Args:
        data: 习惯数据字典
        habit_name: 习惯名称
        
    Returns:
        tuple: (是否成功, 消息)
    """
    if habit_name not in data["habits"]:
        return False, f"习惯 '{habit_name}' 不存在！"
    
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    # 检查今天是否已打卡
    check_ins = data["habits"][habit_name]["check_ins"]
    today_check_ins = [c for c in check_ins if c.startswith(today_str)]
    
    # 记录打卡时间
    data["habits"][habit_name]["check_ins"].append(now.isoformat())
    
    if today_check_ins:
        return True, f"已为 '{habit_name}' 再次打卡！今日已打卡 {len(today_check_ins) + 1} 次"
    else:
        return True, f"'{habit_name}' 打卡成功！"


def calculate_streak(check_ins: List[str]) -> int:
    """
    计算连续打卡天数。
    从昨天开始往前数，直到找到中断的那天。
    如果今天已打卡，连续天数包含今天。
    
    Args:
        check_ins: 打卡记录列表
        
    Returns:
        int: 连续打卡天数
    """
    if not check_ins:
        return 0
    
    # 提取所有打卡日期（去重）
    dates = set()
    for check_in in check_ins:
        try:
            date = datetime.fromisoformat(check_in).date()
            dates.add(date)
        except ValueError:
            continue
    
    if not dates:
        return 0
    
    dates = sorted(dates, reverse=True)
    today = datetime.now().date()
    
    streak = 0
    check_date = today
    
    # 如果今天没打卡，从昨天开始检查
    if check_date not in dates:
        check_date = today - timedelta(days=1)
    
    # 往前数连续的天数
    while check_date in dates:
        streak += 1
        check_date -= timedelta(days=1)
    
    return streak


def get_statistics(data: Dict) -> List[Dict]:
    """
    获取所有习惯的统计数据。
    
    Args:
        data: 习惯数据字典
        
    Returns:
        List[Dict]: 每个习惯的统计信息列表
    """
    stats = []
    for habit_name, habit_data in data["habits"].items():
        check_ins = habit_data.get("check_ins", [])
        total_check_ins = len(check_ins)
        
        # 安全地计算打卡天数
        unique_days = 0
        if check_ins:
            try:
                unique_days = len(set(
                    datetime.fromisoformat(c).date() 
                    for c in check_ins 
                    if c
                ))
            except (ValueError, TypeError):
                unique_days = 0
        
        streak = calculate_streak(check_ins)
        
        stats.append({
            "name": habit_name,
            "total_check_ins": total_check_ins,
            "unique_days": unique_days,
            "streak": streak,
            "created_at": habit_data.get("created_at", "未知")
        })
    
    return stats


def delete_habit(data: Dict, habit_name: str) -> bool:
    """
    删除习惯及其所有记录。
    
    Args:
        data: 习惯数据字典
        habit_name: 习惯名称
        
    Returns:
        bool: 删除成功返回 True，不存在返回 False
    """
    if habit_name not in data["habits"]:
        return False
    
    del data["habits"][habit_name]
    return True


def list_habits(data: Dict) -> List[str]:
    """
    获取所有习惯名称列表。
    
    Args:
        data: 习惯数据字典
        
    Returns:
        List[str]: 习惯名称列表
    """
    return list(data["habits"].keys())


def display_menu():
    """显示主菜单。"""
    print("\n" + "=" * 40)
    print("      📝 个人微习惯追踪器")
    print("=" * 40)
    print("  1. ➕ 添加新习惯")
    print("  2. ✅ 今日打卡")
    print("  3. 📊 查看统计")
    print("  4. 🗑️  删除习惯")
    print("  5. 📋 列出所有习惯")
    print("  0. 🚪 退出程序")
    print("=" * 40)


def handle_add_habit(data: Dict):
    """处理添加习惯。"""
    habit_name = input("请输入习惯名称：").strip()
    
    if not habit_name:
        print("❌ 习惯名称不能为空！")
        return
    
    if add_habit(data, habit_name):
        save_data(data)
        print(f"✅ 习惯 '{habit_name}' 添加成功！")
    else:
        print(f"⚠️ 习惯 '{habit_name}' 已存在！")


def handle_check_in(data: Dict):
    """处理打卡。"""
    habits = list_habits(data)
    
    if not habits:
        print("⚠️ 还没有任何习惯，请先添加习惯！")
        return
    
    print("\n可打卡的习惯：")
    for i, habit in enumerate(habits, 1):
        print(f"  {i}. {habit}")
    
    try:
        choice = input("\n请选择习惯编号（或输入名称）：").strip()
        
        # 尝试按编号选择
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(habits):
                habit_name = habits[idx]
            else:
                print("❌ 无效的编号！")
                return
        else:
            habit_name = choice
        
        success, message = check_in_habit(data, habit_name)
        if success:
            save_data(data)
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    except ValueError:
        print("❌ 请输入有效的数字！")


def handle_view_stats(data: Dict):
    """处理查看统计。"""
    stats = get_statistics(data)
    
    if not stats:
        print("⚠️ 还没有任何习惯数据！")
        return
    
    print("\n" + "-" * 60)
    print(f"{'习惯名称':<15} {'总打卡':<8} {'打卡天数':<8} {'连续天数':<8}")
    print("-" * 60)
    
    for stat in stats:
        print(f"{stat['name']:<15} {stat['total_check_ins']:<8} {stat['unique_days']:<8} {stat['streak']:<8}")
    
    print("-" * 60)


def handle_delete_habit(data: Dict):
    """处理删除习惯。"""
    habits = list_habits(data)
    
    if not habits:
        print("⚠️ 还没有任何习惯！")
        return
    
    print("\n现有习惯：")
    for i, habit in enumerate(habits, 1):
        print(f"  {i}. {habit}")
    
    choice = input("\n请选择要删除的习惯编号（或输入名称）：").strip()
    
    # 尝试按编号选择
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(habits):
            habit_name = habits[idx]
        else:
            print("❌ 无效的编号！")
            return
    else:
        habit_name = choice
    
    confirm = input(f"确定要删除习惯 '{habit_name}' 吗？此操作不可恢复！(yes/no)：").strip().lower()
    
    if confirm in ('yes', 'y', '是'):
        if delete_habit(data, habit_name):
            save_data(data)
            print(f"✅ 习惯 '{habit_name}' 已删除！")
        else:
            print(f"❌ 习惯 '{habit_name}' 不存在！")
    else:
        print("已取消删除操作。")


def handle_list_habits(data: Dict):
    """处理列出所有习惯。"""
    habits = list_habits(data)
    
    if not habits:
        print("⚠️ 还没有任何习惯！")
        return
    
    print("\n📋 所有习惯：")
    for i, habit in enumerate(habits, 1):
        habit_data = data["habits"][habit]
        check_ins_count = len(habit_data.get("check_ins", []))
        print(f"  {i}. {habit} (打卡次数: {check_ins_count})")


def main():
    """主程序入口。"""
    print("🚀 欢迎使用个人微习惯追踪器！")
    
    data = load_data()
    
    while True:
        display_menu()
        choice = input("请选择操作 (0-5)：").strip()
        
        if choice == '0':
            print("\n👋 感谢使用，再见！")
            sys.exit(0)
        elif choice == '1':
            handle_add_habit(data)
        elif choice == '2':
            handle_check_in(data)
        elif choice == '3':
            handle_view_stats(data)
        elif choice == '4':
            handle_delete_habit(data)
        elif choice == '5':
            handle_list_habits(data)
        else:
            print("❌ 无效的选择，请输入 0-5 之间的数字！")


if __name__ == "__main__":
    main()
