"""
批量修复 logger f-string 问题的脚本
将所有 logger.xxx(f"...") 转换为 logger.xxx("...", args)
"""
import re
import os
from pathlib import Path

def fix_logger_fstring(content):
    """
    修复文件中的 logger f-string 问题
    """
    # 匹配 logger.method(f"...{var}...") 模式
    # 这个正则表达式会匹配 logger 调用中的 f-string
    pattern = r'logger\.(debug|info|warning|error|critical)\(f"([^"]*)"'
    
    def replace_fstring(match):
        method = match.group(1)
        fstring_content = match.group(2)
        
        # 提取 f-string 中的变量
        # 将 {var} 替换为 {}
        new_string = re.sub(r'\{([^}]+)\}', '{}', fstring_content)
        
        # 提取所有变量名
        variables = re.findall(r'\{([^}]+)\}', fstring_content)
        
        if not variables:
            # 没有变量，直接去掉 f 前缀
            return f'logger.{method}("{fstring_content}"'
        
        # 构建新的调用
        var_args = ', '.join(variables)
        return f'logger.{method}("{new_string}", {var_args}'
    
    # 替换所有匹配项
    fixed_content = re.sub(pattern, replace_fstring, content)
    
    return fixed_content

def process_file(file_path):
    """处理单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含 logger f-string
        if 'logger.' in content and 'f"' in content:
            fixed_content = fix_logger_fstring(content)
            
            if fixed_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"✅ Fixed: {file_path}")
                return True
        
        return False
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("批量修复 logger f-string 问题")
    print("=" * 60)
    
    # 查找所有 Python 文件
    backend_dir = Path(__file__).parent
    python_files = list(backend_dir.rglob('*.py'))
    
    # 排除虚拟环境和测试文件
    python_files = [
        f for f in python_files 
        if 'venv' not in str(f) 
        and 'bet_app' not in str(f)
        and '__pycache__' not in str(f)
    ]
    
    print(f"\n找到 {len(python_files)} 个 Python 文件")
    print("\n开始处理...\n")
    
    fixed_count = 0
    for file_path in python_files:
        if process_file(file_path):
            fixed_count += 1
    
    print("\n" + "=" * 60)
    print(f"处理完成！共修复 {fixed_count} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
