"""
Adapted from Agents4PLC:
https://github.com/Luoji-zju/Agents4PLC_release

Original file: src/compiler.py
"""

import os
import subprocess
import sys
from pathlib import Path

from plc_agent.src import config



def matiec_compiler(file_dir):
    """
    编译 ST 文件并返回结果和错误信息。

    Returns:
        tuple: (success: bool, errors: str | None)
            - success: True 表示编译成功
            - errors: 错误信息字符串，成功时为 None
    """
    MATIEC_PATH = getattr(config, 'MATIEC_PATH', None)

    if MATIEC_PATH is None:
        MATIEC_PATH = os.getenv('MATIEC_PATH')

    if MATIEC_PATH is None:
        raise ValueError("MATIEC_PATH is not set in config or as an environment variable.")

    # 转换为绝对路径
    abs_file_path = os.path.abspath(file_dir)

    try:
        output = subprocess.check_output(
            f'./iec2iec -f -p "{abs_file_path}" 2>&1',
            cwd=MATIEC_PATH,
            shell=True,
            text=True
        )

        # matiec 错误格式: "file.st:line-col: error: message" 或 "N error(s) found"
        if 'error:' in output or 'error(s) found' in output:
            return False, output
        return True, None
    except subprocess.CalledProcessError as e:
        # 命令执行失败（如文件不存在）
        error_msg = e.output if e.output else str(e)
        return False, error_msg