'''
Description: 从Excel文件中读取法语单词或短语，并为每个单词生成TTS音频文件
'''
import asyncio
import os
import edge_tts
import hashlib
import pygame
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import re

# 定义全局配置
OUTPUT_DIR = r"./output"  # 输出目录
VOICE = "fr-FR-HenriNeural"  # 法语男声
# VOICE = "fr-FR-DeniseNeural"  # 法语女声
RATE = "-5%"  # 语速
MAX_FILENAME_LENGTH = 50  # 最大文件名长度

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def text_to_speech(text, output, voice=None, rate=None):
    """
    将文本转换为语音并保存到指定的输出文件。
    使用全局变量作为默认值。
    """
    # 如果未指定，使用全局变量
    if voice is None:
        voice = VOICE
    if rate is None:
        rate = RATE

    communicate = edge_tts.Communicate(text, voice, rate=rate)
    try:
        await communicate.save(output)
        print(f"已保存语音到 {output}")
    except Exception as e:
        print(f"文本转语音过程中出错: {e}")
        raise


def sanitize_filename(filename):
    """
    清理文件名，替换不合法的字符为下划线
    """
    # 确保输入是字符串
    filename = str(filename)
    # 移除非法字符，只保留字母、数字、空格、下划线和连字符
    sanitized = re.sub(r'[^\w\s-]', '_', filename)
    # 将连续的空格替换为单个下划线
    sanitized = re.sub(r'\s+', '_', sanitized)
    # 移除开头和结尾的下划线
    sanitized = sanitized.strip('_')
    return sanitized


async def process_excel_file(file_path):
    """
    处理Excel文件，为每个单词生成TTS音频
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)

        # 确保至少有一列
        if df.shape[1] < 1:
            print("Excel文件必须至少包含一列数据")
            return

        # 获取第一列数据（法语单词或短语）
        words = df.iloc[:, 0].tolist()

        # 处理每个单词
        for word in words:
            if pd.isna(word) or word == "":
                continue  # 跳过空值

            # 原始单词（用于TTS生成）
            original_word = str(word)

            # 清理文件名（所有不合法字符替换为下划线）
            filename = sanitize_filename(original_word)

            # 如果文件名过长，截断它
            if len(filename) > MAX_FILENAME_LENGTH:
                filename = filename[:MAX_FILENAME_LENGTH]

            # 确保文件名不为空
            if not filename:
                filename = "unnamed"

            # 生成输出文件路径
            output = os.path.join(OUTPUT_DIR, f"{filename}.mp3")

            # 检查文件是否已存在
            if os.path.isfile(output):
                print(f"文件 '{output}' 已存在，跳过生成。")
                continue

            # 生成TTS音频
            print(f"正在为 '{original_word}' 生成音频...")
            await text_to_speech(original_word, output)

        print("所有单词处理完成！")

    except Exception as e:
        print(f"处理Excel文件时出错: {e}")


def select_excel_file():
    """
    打开文件对话框选择Excel文件
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    file_path = filedialog.askopenfilename(
        title="选择Excel文件",
        filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
    )

    if file_path:
        print(f"已选择文件: {file_path}")
        return file_path
    else:
        print("未选择文件")
        return None


async def main():
    """
    主函数，打开文件对话框并处理选择的Excel文件
    """
    print("请选择一个Excel文件...")
    file_path = select_excel_file()

    if file_path:
        await process_excel_file(file_path)
    else:
        print("程序已取消")


if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())
