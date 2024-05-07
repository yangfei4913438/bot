from custom_log import log
from oss import audio_del, audio_download, audio_exists
from telebot import TeleBot
import requests
import os
import asyncio


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
            "user_id": str(message.chat.id),
            "query": message.text
        }
        log.info("请求数据: %s", data)

        response = requests.post(url=url, json=data, timeout=100)

        if response.status_code == 200:
            log.info("返回数据: %o", response.json())
            data = response.json()
            if "msg" in data:
                bot_instance.reply_to(message, data["msg"].encode('utf-8'))
                asyncio.run(check_audio(message, 'audio', f"{data["id"]}.mp3"))
            else:
                bot_instance.reply_to(message, "对不起，我不知道怎么回复你")
        else:
            log.error("请求出错: %s, %s", response.status_code, response.text)
            bot_instance.reply_to(message, "对不起，我不知道怎么回复你")

    except requests.RequestException as err:
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
            log.debug("waiting")
            await asyncio.sleep(1)  # 使用asyncio.sleep(1)来等待1秒

try:
    # 启动服务
    log.info('启动服务')
    bot_instance.polling(logger_level=20)
except Exception as e:
    log.error("启动服务出错: %s", e)
    bot_instance.stop_polling()
