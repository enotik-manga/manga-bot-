import os
import telebot
import requests
import urllib.parse
import random
from flask import Flask
from threading import Thread

# --- ЗАГЛУШКА ДЛЯ СЕРВЕРА ---
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()
# ----------------------------

# ТОКЕН ВПИСАН СЮДА
TOKEN = '8931356815:AAEc1hni9GZ9_21-2L40XWKAxaDem85P5C0'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, брат! Я Манга-Ками ⛩️. Напиши, что нарисовать, и я создам эпичные картинки в стиле аниме!')

@bot.message_handler(content_types=['text'])
def generate_image(message):
    prompt = message.text
    magic_prompt = f"{prompt}, masterpiece, best quality, highly detailed, dynamic action pose, epic composition, cinematic lighting, vibrant colors, anime key visual, sharp focus"
    encoded_prompt = urllib.parse.quote(magic_prompt)
    
    bot.send_message(message.chat.id, 'Рисую экшн! ⏳ Генерирую 2 варианта (квадрат и вертикальный постер), подожди около минуты...')

    sizes = [("1024", "1024", "квадрат"), ("1024", "1536", "вертикальный постер")]
    
    for i, (w, h, desc) in enumerate(sizes):
        seed = random.randint(1, 1000000)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux-anime&width={w}&height={h}&nologo=true&seed={seed}"
        
        try:
            bot.send_chat_action(message.chat.id, 'upload_photo')
            response = requests.get(url, timeout=300)
            response.raise_for_status()
            bot.send_photo(message.chat.id, response.content, caption=f'Вариант {i+1} ({desc}) готов! 🎨')
        except Exception as e:
            bot.send_message(message.chat.id, f'Ошибка на варианте {i+1}: не удалось нарисовать.')

if __name__ == "__main__":
    keep_alive()
    print("Бот-художник запущен!")
    bot.infinity_polling()
