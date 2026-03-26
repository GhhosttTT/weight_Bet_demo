"""
整理 design.md 文件，移除零宽空格
"""

def main():
    # 读取文件
    with open('design.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 清理零宽空格
    content = content.replace('\u2000', '')
    
    # 保存文件
    with open('design.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ 文件整理完成！已移除所有零宽空格")

if __name__ == '__main__':
    main()
