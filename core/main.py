import telebot
import os
import logging
from telebot.types import InlineQueryResultArticle, InputTextMessageContent
from telebot import apihelper

from PIL import Image
from io import BytesIO
import requests

apihelper.ENABLE_MIDDLEWARE = True

from dotenv import load_dotenv

logger= telebot.logger
telebot.logger.setLevel(logging.INFO)

load_dotenv()
API_TOKEN = os.environ.get('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "<i>Please send me a photo in jpg, png or jpeg format.You can send your image either as a photo or document!</i>", parse_mode="HTML")

@bot.middleware_handler(update_types=['message'])
def filter_images(bot_instance, message):
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
    elif message.content_type == 'document':
        if message.document.mime_type.startswith('image/'):
            file_id = message.document.file_id
        else:
            bot.send_message(message.chat.id, "Unsupported image format!! please send me a photo with png, jpg or jpeg format.")
            return
    else:
        return

    file_info = bot.get_file(file_id)
    file_url = f'https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}'
    
    response = requests.get(file_url)

    image = Image.open(BytesIO(response.content))
    

    image_format = image.format.lower()
    if image_format in ['jpeg', 'jpg', 'png']:
        bot.send_message(message.chat.id, "<i>Image received successfully.</i>", parse_mode="HTML")
        bot.send_message(message.chat.id, "<i>Your image is processing...</i>", parse_mode="HTML")
        message.supported_image_format = True
        message.image= image
    else:
        bot.send_message(message.chat.id, "<i>Unsupported image format!! please send me a photo with png, jpg or jpeg format.</i>", parse_mode="HTML")
        message.supported_image_format = False

    

def compress_jpeg_image(image):
    compressed_image_io = BytesIO()
    image.save(compressed_image_io, format='JPEG', quality=50)
    compressed_image_io.seek(0)
    return compressed_image_io

def compress_png_image(image):
    compressed_image_io = BytesIO()
    image.save(compressed_image_io, format='PNG', optimize=True)
    compressed_image_io.seek(0)
    return compressed_image_io


@bot.message_handler(content_types=['photo','document'])
def compress_send_image(message):
    if message.supported_image_format: 
        image_format = message.image.format.lower()
        if image_format in ['jpeg', 'jpg']:
            compressed_image_io = compress_jpeg_image(message.image)
        elif image_format == 'png':
            compressed_image_io = compress_png_image(message.image)
        bot.send_photo(message.chat.id, compressed_image_io, caption="This is your compressed image file.")
                     


@bot.inline_handler(func= lambda query: True)
def query_handler(query):
    results=[]
    results.append(
        InlineQueryResultArticle(
            id='1',
            title='Join the Bot',
            input_message_content=InputTextMessageContent(message_text="Join the Bot"),
            url='https://t.me/mysecond001_bot',
        
        )
    )

    results.append(
        InlineQueryResultArticle(
            id='2',
            title='Visit our website.',
            input_message_content=InputTextMessageContent(message_text="https://smehdizadeh.ir"),
            url='https://smehdizadeh.ir',
        
        )
    )

    results.append(
        InlineQueryResultArticle(
            id='3',
            title='Robot Description',
            input_message_content=InputTextMessageContent(message_text="this bot is suitable tool for compressing images in jpg, png and jpeg formats."),
            description="click to see bot's description",
        
        )
    )

    
    bot.answer_inline_query(query.id, results, cache_time=0)




bot.infinity_polling()