'''
Description: 
'''
import asyncio
import os
import edge_tts
import sys
import hashlib
import pygame

# 定义输出目录
OUTPUT_DIR = r".\output_voice"

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def text_to_speech(text, voice, output, rate="-15%"):
    """
    将文本转换为语音并保存到指定的输出文件。
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    try:
        await communicate.save(output)
        # print(f"已保存语音到 {output}")
    except Exception as e:
        print(f"文本转语音过程中出错: {e}")
        raise


def play_audio(output):
    """
    使用 pygame 播放指定的音频文件。
    """
    if os.path.exists(output) and os.path.getsize(output) > 0:
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(output)
            pygame.mixer.music.play()
            # print(f"正在播放 {output}")
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # 每100毫秒检查一次播放状态
        except Exception as e:
            print(f"播放音频时出错: {e}")
    else:
        print(f"音频文件 {output} 不存在或为空。")


def generate_filename(text):
    """
    生成一个基于文本哈希值的唯一且较短的文件名。
    """
    # 使用 SHA-256 哈希文本
    hash_object = hashlib.sha256(text.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    return hex_dig


def main():
    """
    主函数，处理命令行输入并执行文本转语音和播放。
    """
    if len(sys.argv) != 3:
        # print("用法: python script.py \"要转换的文本\" \"文件名（不含扩展名，可选）\"")
        sys.exit(1)

    input_text = sys.argv[1]
    user_filename = sys.argv[2]

    # 如果用户提供的文件名过长，使用哈希值代替
    MAX_FILENAME_LENGTH = 50  # 根据需要调整最大长度
    if len(user_filename) > MAX_FILENAME_LENGTH:
        # print(f"提供的文件名过长，已自动生成简短文件名。")
        filename = generate_filename(input_text)
    else:
        # 确保文件名不包含非法字符
        filename = "".join(c for c in user_filename if c.isalnum() or c in (' ', '_', '-')).rstrip()

    # voice = "fr-FR-RemyMultilingualNeural"  # 选择语音
    voice = "fr-FR-HenriNeural"  # 选择语音
    output = os.path.join(OUTPUT_DIR, f"{filename}.mp3")

    try:
        # 判断是否存在同名文件
        if os.path.isfile(output):
            # print(f"文件 '{output}' 存在。")
            play_audio(output)
        else:
            # print(f"文件 '{output}' 不存在。正在生成音频...")
            # 执行文本转语音
            asyncio.run(text_to_speech(input_text, voice, output))
            # 播放生成的音频
            play_audio(output)
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    main()
