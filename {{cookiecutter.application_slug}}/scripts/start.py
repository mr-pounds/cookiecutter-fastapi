"""
Description  : 
Version      : 1.0.1
Author       : zzz
Date         : 2025-09-13 13:39:22
LastEditors  : zzz
LastEditTime : 2025-09-13 13:41:32
"""
import subprocess
import sys


def main():
    # 构建启动FastAPI开发服务器的命令
    command = [
        sys.executable,  # 使用当前Python解释器
        '-m', 'uvicorn',
        'app.main:app',  # FastAPI应用位置
        '--host', '127.0.0.1',  # 默认主机
        '--port', '8000',        # 默认端口
        '--env-file', '.env.prod', # 加载.env.dev文件
        '--worker', '4'
    ]
    
    print("启动FastAPI开发服务器 (使用环境文件: .env.prod)")
    print(f"命令: {' '.join(command)}")
    
    try:
        # 执行命令
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FastAPI服务器启动失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)


if __name__ == '__main__':
    main()