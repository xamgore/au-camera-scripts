#!/usr/bin/python
from __init__ import *
from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Btn
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler
from youtube import YoutubeClient
import requests
import config
import thumbnails.send as thumbnails
import channel.send_to_telegram as channel


def upload(video_id, num):
    print('download preview...', end='')
    file_path = f'{video_id}_maxres{num}.jpg'
    with open(file_path, 'wb') as f:
        f.write(requests.get(f'https://i.ytimg.com/vi/{video_id}/maxres{num}.jpg').content)
        print('ok')

    print('upload to youtube...', end='')
    youtube.upload_thumbnail(video_id, file_path)
    os.remove(file_path)
    print('ok')


def thumbnail_button(bot, cfg):
    req = cfg.callback_query
    video_id, num = req.data.split('||')

    if str(req.message.chat.id) != env['DEV_CHAT']:
        return

    upload(video_id, num)

    f = lambda s, i: " 🆗 " if str(i) == num else s

    return not bot.editMessageReplyMarkup(
        chat_id=req.message.chat.id,
        message_id=req.message.message_id,
        reply_markup=InlineKeyboardMarkup([[
            Btn(f(" 1️⃣  ", 1), callback_data=f"{video_id}||1"),
            Btn(f(" 2️⃣  ", 2), callback_data=f"{video_id}||2"),
            Btn(f(" 3️⃣  ", 3), callback_data=f"{video_id}||3"),
        ]]))


def send_thumbnails(bot, cfg):
    bot.sendMessage(env['DEV_CHAT'], thumbnails.send(), disable_notification=True)

def send_videos(bot, cfg):
    bot.sendMessage(env['DEV_CHAT'], channel.send(), disable_notification=True)


env = config.load('config.prod.yml')
scope = ['https://www.googleapis.com/auth/youtube']
youtube = YoutubeClient(scope)

bot = Updater(env['TM_TOKEN'])
bot.dispatcher.add_handler(CallbackQueryHandler(thumbnail_button))
bot.dispatcher.add_handler(CommandHandler('thumbnails', send_thumbnails))
bot.dispatcher.add_handler(CommandHandler('channel', send_videos))
bot.dispatcher.add_error_handler(print)
bot.start_polling()
bot.idle()