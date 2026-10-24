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

# ТОКЕН
TOKEN = '8931356815:AAF9i-Z07DTm4K5P4bua4WM21CagMu0ZbQQ'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, брат! Я Манга-Ками ⛩️. Напиши, что нарисовать (лучше на английском).')

@bot.message_handler(content_types=['text'])
def generate_image(message):
    prompt = message.text
    magic_prompt = f"{prompt}, anime style, masterpiece"
    encoded_prompt = urllib.parse.quote(magic_prompt)
    
    bot.send_message(message.chat.id, 'Рисую... ⏳ Подожди около минуты...')

    seed = random.randint(1, 1000000)
    # Убрал model=flux-anime, чтобы сервер сам выбрал рабочую модель
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}"
    
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        # Увеличил таймаут до 180 секунд, так как сервера часто тупят
        response = requests.get(url, headers=headers, timeout=180)
        response.raise_for_status()
        bot.send_photo(message.chat.id, response.content, caption=f'Готово! 🎨')
    except Exception as e:
        # ТЕПЕРЬ БОТ ПОКАЖЕТ НАСТОЯЩУЮ ОШИБКУ
        bot.send_message(message.chat.id, f'Ошибка сервера: {str(e)}')

if __name__ == "__main__":
    keep_alive()
    print("Бот-художник запущен!")
    bot.infinity_polling()
