"""
Description  :
Version      : 1.0.1
Author       : zzz
Date         : 2025-09-17 10:43:13
LastEditors  : zzz
LastEditTime : 2025-09-17 10:44:11
"""

import subprocess
import sys


def run_command(cmd):
    """执行命令并在执行前打印命令，模拟set -x的功能"""
    print(f"+ {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"命令执行失败: {cmd}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    run_command("uv export --format requirements.txt -o requirements.txt")
    run_command("git add requirements.txt")
