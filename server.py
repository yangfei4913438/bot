import asyncio
import os
import urllib.parse

import requests
from telebot import TeleBot
from dotenv import load_dotenv

from oss import audio_del, audio_download, audio_exists

# 加载环境变量
load_dotenv()

# 创建一个机器人实例
bot_instance = TeleBot(os.getenv("BOT_TOKEN"))


@bot_instance.message_handler(commands=['start'])
def send_welcome(message):
    # 直接回复
    bot_instance.send_message(message.chat.id, "你好! 我是周半仙，有什么可以帮助你的吗？")


@bot_instance.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        print("发送消息:", message.text)
        encode_text = urllib.parse.quote(message.text)
        response = requests.post(
            url=f'{os.getenv("AI_SERVER")}/chat?user_id={message.chat.id}&query={encode_text}',
            timeout=100
        )

        if response.status_code == 200:
            print("返回数据:", response.json())
            data = response.json()
            if "msg" in data:
                bot_instance.reply_to(message, data["msg"].encode('utf-8'))
                asyncio.run(check_audio(message, 'audio', f"{data["id"]}.mp3"))
            else:
                bot_instance.reply_to(message, "对不起，我不知道怎么回复你")

    except requests.RequestException as e:
        print("发送消息出错:", e)
        bot_instance.reply_to(message, "对不起，我不知道怎么回复你")


async def check_audio(message: any, target_dir:str, filename: str):
    """ 检查音频是否存在并发送 """
    while True:
        # 检查音频是否存在
        if audio_exists(target_dir, filename):
            # 获取音频
            file = audio_download(target_dir, filename)
            # 发送音频
            bot_instance.send_audio(message.chat.id, file)
            # 删除音频, 释放云端空间
            audio_del(target_dir, filename)
            break
        else:
            print("waiting")
            await asyncio.sleep(1)  # 使用asyncio.sleep(1)来等待1秒

try:
    # 启动服务
    bot_instance.polling(logger_level=20)
except Exception as e:
    print("启动服务出错:", e)
    bot_instance.stop_polling()
