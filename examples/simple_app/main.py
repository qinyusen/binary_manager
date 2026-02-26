#!/usr/bin/env python3
"""
Simple Calculator Application
一个简单的计算器应用，演示Binary Manager的使用
"""
import sys
import json
from pathlib import Path
from calculator import Calculator


def load_config():
    """加载配置文件"""
    config_file = Path(__file__).parent / "config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    return {"precision": 2}


def print_usage():
    """打印使用说明"""
    print("""
Simple Calculator - 使用方法:
  python3 main.py <operation> <num1> <num2>
  
操作:
  add    - 加法: num1 + num2
  sub    - 减法: num1 - num2
  mul    - 乘法: num1 * num2
  div    - 除法: num1 / num2
  
示例:
  python3 main.py add 10 5
  python3 main.py div 20 4
  python3 main.py mul 3.5 2
    """)


def main():
    """主函数"""
    if len(sys.argv) < 4:
        print_usage()
        sys.exit(1)
    
    operation = sys.argv[1].lower()
    try:
        num1 = float(sys.argv[2])
        num2 = float(sys.argv[3])
    except ValueError:
        print("错误: 参数必须是数字")
        sys.exit(1)
    
    config = load_config()
    calc = Calculator(precision=config.get("precision", 2))
    
    operations = {
        'add': ('加法', calc.add),
        'sub': ('减法', calc.sub),
        'mul': ('乘法', calc.mul),
        'div': ('除法', calc.div),
    }
    
    if operation not in operations:
        print(f"错误: 未知的操作 '{operation}'")
        print_usage()
        sys.exit(1)
    
    op_name, op_func = operations[operation]
    
    try:
        result = op_func(num1, num2)
        print(f"\n{op_name}结果:")
        print(f"  {num1} {operation} {num2} = {result}")
    except ZeroDivisionError:
        print("错误: 除零错误")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
