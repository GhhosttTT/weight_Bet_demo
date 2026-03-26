#!/usr/bin/env python3
"""
查看数据库工具
"""
import sqlite3
import sys

def view_tables():
    """显示所有表"""
    conn = sqlite3.connect('weight_loss_betting.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n=== 数据库表 ===")
    for table in tables:
        print(f"  - {table[0]}")
    
    conn.close()

def view_users():
    """显示所有用户"""
    conn = sqlite3.connect('weight_loss_betting.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, email, nickname, gender, age, height, current_weight, target_weight, created_at
        FROM users
        ORDER BY created_at DESC
    """)
    users = cursor.fetchall()
    
    print("\n=== 用户列表 ===")
    if not users:
        print("  (无用户)")
    else:
        for user in users:
            print(f"\n用户ID: {user[0]}")
            print(f"  邮箱: {user[1]}")
            print(f"  昵称: {user[2]}")
            print(f"  性别: {user[3]}")
            print(f"  年龄: {user[4]}")
            print(f"  身高: {user[5]} cm")
            print(f"  当前体重: {user[6]} kg")
            print(f"  目标体重: {user[7]} kg" if user[7] else "  目标体重: 未设置")
            print(f"  注册时间: {user[8]}")
    
    conn.close()

def view_balances():
    """显示所有余额"""
    conn = sqlite3.connect('weight_loss_betting.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT b.user_id, u.nickname, b.available_balance, b.frozen_balance, b.updated_at
        FROM balances b
        LEFT JOIN users u ON b.user_id = u.id
        ORDER BY b.updated_at DESC
    """)
    balances = cursor.fetchall()
    
    print("\n=== 余额列表 ===")
    if not balances:
        print("  (无余额记录)")
    else:
        for balance in balances:
            print(f"\n用户: {balance[1]} ({balance[0][:8]}...)")
            print(f"  可用余额: ¥{balance[2]:.2f}")
            print(f"  冻结余额: ¥{balance[3]:.2f}")
            print(f"  总余额: ¥{(balance[2] + balance[3]):.2f}")
            print(f"  更新时间: {balance[4]}")
    
    conn.close()

def view_plans():
    """显示所有计划"""
    conn = sqlite3.connect('weight_loss_betting.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.id, u1.nickname as creator, u2.nickname as participant, 
               p.status, p.bet_amount, p.start_date, p.end_date, p.created_at
        FROM betting_plans p
        LEFT JOIN users u1 ON p.creator_id = u1.id
        LEFT JOIN users u2 ON p.participant_id = u2.id
        ORDER BY p.created_at DESC
    """)
    plans = cursor.fetchall()
    
    print("\n=== 对赌计划列表 ===")
    if not plans:
        print("  (无计划)")
    else:
        for plan in plans:
            print(f"\n计划ID: {plan[0][:8]}...")
            print(f"  创建者: {plan[1]}")
            print(f"  参与者: {plan[2] if plan[2] else '待接受'}")
            print(f"  状态: {plan[3]}")
            print(f"  赌金: ¥{plan[4]:.2f}")
            print(f"  开始日期: {plan[5]}")
            print(f"  结束日期: {plan[6]}")
            print(f"  创建时间: {plan[7]}")
    
    conn.close()

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'tables':
            view_tables()
        elif command == 'users':
            view_users()
        elif command == 'balances':
            view_balances()
        elif command == 'plans':
            view_plans()
        else:
            print(f"未知命令: {command}")
            print_usage()
    else:
        # 默认显示所有信息
        view_tables()
        view_users()
        view_balances()
        view_plans()

def print_usage():
    """打印使用说明"""
    print("\n使用方法:")
    print("  python view_db.py           # 显示所有信息")
    print("  python view_db.py tables    # 显示所有表")
    print("  python view_db.py users     # 显示用户列表")
    print("  python view_db.py balances  # 显示余额列表")
    print("  python view_db.py plans     # 显示计划列表")

if __name__ == '__main__':
    main()
