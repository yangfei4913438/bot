from custom_log import log
from oss import audio_del, audio_download, audio_exists
from telebot import TeleBot
import requests
import os
import asyncio
import json


from dotenv import load_dotenv
# 加载环境变量
load_dotenv()


# 创建一个机器人实例
bot_instance = TeleBot(os.getenv("BOT_TOKEN"))


@bot_instance.message_handler(commands=['start'])
def send_welcome(message):
    """ 欢迎消息 """
    log.info("收到消息: %s", message.text)
    # 直接回复
    bot_instance.send_message(message.chat.id, "你好! 有什么可以帮助你的吗?")


@bot_instance.message_handler(func=lambda message: True)
def echo_all(message):
    """ 消息处理 """
    try:
        log.info("发送消息: %s", message.text)

        url = f'{os.getenv("AI_SERVER")}/chat'
        log.info("请求地址: %s", url)

        data = {
            "query": message.text
        }
        log.info("请求数据: %s", data)

        headers = {
            "Authorization": "Bearer demo",  # 这里不需要token，但是头部必须有这个 key value，否则会报错
            "Role": os.getenv("ADMIN_ROLE"),  # 这里是用户的特权，绕过 token 校验
            "UserId": str(message.chat.id),  # 这里是用户的id，用于记录用户的聊天记录
        }

        bot_instance.reply_to(message, "小友，请稍后片刻...")

        with requests.post(
                url=url, json=data, timeout=100, headers=headers, stream=True) as response:
            if response.status_code == 200:
                text = ''
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        log.info("返回数据: %s", decoded_line)
                        bot_instance.send_message(
                            message.chat.id, decoded_line)
                        text += decoded_line

                if text:
                    text_id = response.headers.get('id')
                    asyncio.run(check_audio(
                        message, 'audio', f"{text_id}.mp3"))
                else:
                    log.error("ai服务器返回的数据结构异常: %s", data)
                    bot_instance.reply_to(message, "对不起，我不知道怎么回复你")
            else:
                log.error("请求ai服务端出错: %s", response)
                bot_instance.reply_to(message, "对不起，我不知道怎么回复你")

    except Exception as err:
        log.error("发送消息出错: %s", err)
        bot_instance.reply_to(message, "对不起，我不知道怎么回复你")


async def check_audio(message: any, target_dir: str, filename: str):
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
            log.debug("等待 1 秒重试...")
            await asyncio.sleep(1)  # 使用asyncio.sleep(1)来等待1秒

try:
    # 启动服务
    log.info('启动服务')
    bot_instance.polling(logger_level=20)
except Exception as e:
    log.error("启动服务出错: %s", e)
    bot_instance.stop_polling()
