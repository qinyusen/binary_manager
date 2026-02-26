#!/usr/bin/env python3
"""
Calculator Module
提供基本的数学运算功能
"""


class Calculator:
    """简单的计算器类"""
    
    def __init__(self, precision=2):
        """
        初始化计算器
        
        Args:
            precision: 结果的小数位数，默认2位
        """
        self.precision = precision
    
    def _round_result(self, value):
        """四舍五入结果"""
        return round(value, self.precision)
    
    def add(self, a, b):
        """加法"""
        return self._round_result(a + b)
    
    def sub(self, a, b):
        """减法"""
        return self._round_result(a - b)
    
    def mul(self, a, b):
        """乘法"""
        return self._round_result(a * b)
    
    def div(self, a, b):
        """除法"""
        if b == 0:
            raise ZeroDivisionError("除数不能为零")
        return self._round_result(a / b)
    
    def power(self, a, b):
        """幂运算"""
        return self._round_result(a ** b)
    
    def mod(self, a, b):
        """取模"""
        if b == 0:
            raise ZeroDivisionError("除数不能为零")
        return self._round_result(a % b)


# 便捷函数
def add(a, b):
    """加法"""
    return Calculator().add(a, b)


def sub(a, b):
    """减法"""
    return Calculator().sub(a, b)


def mul(a, b):
    """乘法"""
    return Calculator().mul(a, b)


def div(a, b):
    """除法"""
    return Calculator().div(a, b)


if __name__ == "__main__":
    # 简单测试
    calc = Calculator()
    print("Calculator 测试:")
    print(f"  10 + 5 = {calc.add(10, 5)}")
    print(f"  10 - 5 = {calc.sub(10, 5)}")
    print(f"  10 * 5 = {calc.mul(10, 5)}")
    print(f"  10 / 5 = {calc.div(10, 5)}")
