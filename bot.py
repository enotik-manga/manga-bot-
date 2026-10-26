import os
import telebot
import requests
import urllib.parse
import random
from flask import Flask
from threading import Thread
from PIL import Image
import io

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

TOKEN = '8931356815:AAF9i-Z07DTm4K5P4bua4WM21CagMu0ZbQQ'
bot = telebot.TeleBot(TOKEN)

# Цитаты для одиночных картинок
quotes = [
    "Иногда самые громкие слова — это тишина.",
    "Дождь смывает всё, кроме воспоминаний.",
    "Я отпустил тебя, но моя тень осталась с тобой.",
    "Сердце разбивается не сразу, а по кусочкам каждый день.",
    "Ты ушла, и мир потерял свои краски.",
    "Не все истории заканчиваются счастливо...",
    "Скажи мне, что это сон, и я поверю."
]

def get_image(prompt, width, height):
    # ЖЕСТКИЙ 2D СТИЛЬ
    style = "2D manhwa style, webtoon, flat color, comic book line art, masterpiece, best quality, no 3d, no realism, no cgi, "
    full_prompt = f"{style} {prompt}"
    encoded_prompt = urllib.parse.quote(full_prompt)
    seed = random.randint(1, 1000000)
    
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux-anime&width={width}&height={height}&nologo=true&seed={seed}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=180)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Я рисую 2D манхву.\n\nПросто напиши сцену на английском — я сделаю одну картинку с цитатой.\n\nА если хочешь комикс, добавь в конце слово "comic" или "комикс", и я склею 3 кадра!')

@bot.message_handler(content_types=['text'])
def handle_message(message):
    user_prompt = message.text.lower()
    
    # ПРОВЕРЯЕМ, ХОЧЕТ ЛИ ПОЛЬЗОВАТЕЛЬ КОМИКС
    is_comic = "comic" in user_prompt or "комикс" in user_prompt or "3 panels" in user_prompt

    if is_comic:
        # Убираем слова-триггеры из промпта, чтобы они не мешали рисовать
        clean_prompt = message.text.replace("comic", "").replace("комикс", "").replace("3 panels", "").strip()
        bot.send_message(message.chat.id, 'Рисую комикс из 3 кадров... ⏳ Это займет около 2 минут.')
        
        prompts = [
            f"wide shot, {clean_prompt}",
            f"dynamic action, {clean_prompt}",
            f"close up, dramatic, {clean_prompt}"
        ]
        
        images = []
        for p in prompts:
            bot.send_chat_action(message.chat.id, 'upload_photo')
            img = get_image(p, 1024, 1024)
            if img:
                images.append(img)
                
        if len(images) == 3:
            total_height = images[0].height * 3
            comic_page = Image.new('RGB', (images[0].width, total_height), color='white')
            comic_page.paste(images[0], (0, 0))
            comic_page.paste(images[1], (0, images[0].height))
            comic_page.paste(images[2], (0, images[0].height * 2))
            
            bio = io.BytesIO()
            bio.name = 'comic.jpg'
            comic_page.save(bio, 'JPEG')
            bio.seek(0)
            
            bot.send_photo(message.chat.id, bio, caption='Твой комикс готов! 🎨')
        else:
            bot.send_message(message.chat.id, 'Ошибка: нейросеть перегружена. Попробуй еще раз.')
            
    else:
        # РИСУЕМ ОДНУ КАРТИНКУ С ЦИТАТОЙ
        bot.send_message(message.chat.id, 'Рисую сцену... ⏳ Подожди минуту...')
        bot.send_chat_action(message.chat.id, 'upload_photo')
        
        img = get_image(message.text, 1024, 1536) # Вертикальный формат как страница манги
        
        if img:
            bio = io.BytesIO()
            bio.name = 'manhwa.jpg'
            img.save(bio, 'JPEG')
            bio.seek(0)
            
            selected_quote = random.choice(quotes)
            bot.send_photo(message.chat.id, bio, caption=f'💬 *{selected_quote}*', parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, 'Ошибка: нейросеть перегружена. Попробуй еще раз.')

if __name__ == "__main__":
    keep_alive()
    print("Бот-художник запущен!")
    bot.infinity_polling()
