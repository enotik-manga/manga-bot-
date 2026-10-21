import os
import telebot
import requests
import urllib.parse
import random

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, брат! Я Манга-Ками ⛩️. Напиши, что нарисовать, и я создам эпичные картинки в стиле аниме!')

@bot.message_handler(content_types=['text'])
def generate_image(message):
    prompt = message.text
    
    # Секретный соус для крутой картинки
    magic_prompt = f"{prompt}, masterpiece, best quality, ultra-detailed, dynamic action pose, epic composition, cinematic lighting, vibrant colors, anime key visual, sharp focus"
    encoded_prompt = urllib.parse.quote(magic_prompt)
    
    bot.send_message(message.chat.id, 'Рисую экшн! ⏳ Генерирую 2 варианта (квадрат и вертикальный постер), подожди около минуты...')

    # Делаем 2 картинки: квадрат и вертикальную
    sizes = [("1024", "1024", "квадрат"), ("1024", "1536", "вертикальный постер")]
    
    for i, (w, h, desc) in enumerate(sizes):
        seed = random.randint(1, 1000000)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux-anime&width={w}&height={h}&nologo=true&seed={seed}"
        
        try:
            # Показываем статус "отправляет фото"
            bot.send_chat_action(message.chat.id, 'upload_photo')
            
            response = requests.get(url, timeout=300)
            response.raise_for_status()
            
            bot.send_photo(message.chat.id, response.content, caption=f'Вариант {i+1} ({desc}) готов! 🎨')
        except Exception as e:
            bot.send_message(message.chat.id, f'Ошибка на варианте {i+1}: не удалось нарисовать.')

print("Бот-художник запущен!")
bot.infinity_polling()
