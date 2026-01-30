#!/usr/bin/env python3
"""
Main application entry point
"""


def greet(name: str) -> str:
    return f"Hello, {name}!"


if __name__ == '__main__':
    print(greet("World"))
