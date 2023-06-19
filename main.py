import os

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from requests_toolbelt.multipart.encoder import MultipartEncoder

import config

# Инициализация бота и диспетчера
bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# URL веб-сервера
web_server_url = config.URL


@dp.message_handler(content_types=types.ContentType.VOICE)
async def process_voice_message(message: types.Message, state: FSMContext):
    # Сохранение голосового сообщения в файл
    voice_file_id = message.voice.file_id
    voice_file = await bot.get_file(voice_file_id)
    voice_file_path = voice_file.file_path
    voice_file_data = await bot.download_file(voice_file_path)

    # Сохранение файла в формате mp3 на сервере
    mp3_file_path = config.PATH
    with open(mp3_file_path, "wb") as mp3_file:
        mp3_file.write(voice_file_data.getvalue())

    # Отправка ответного сообщения
    await message.reply("Голосовое сообщение сохранено")

    # Отправка голосового сообщения на веб-сервер
    multipart_data = MultipartEncoder(fields={"file": (os.path.basename(mp3_file_path), open(mp3_file_path, "rb"), "audio/mpeg")})
    headers = {"Content-Type": multipart_data.content_type}

    response = requests.post(web_server_url, data=multipart_data, headers=headers)

    if response.status_code == 200:
        # Если запрос успешен, отправляем ответное сообщение от сервера в Telegram
        response_data = response.json()
        detected_language = response_data["detected_language"]
        recognized_text = response_data["recognized_text"]
        await message.reply(f"Detected Language: {detected_language}\nRecognized Text: {recognized_text}")
    else:
        await message.reply("Ошибка при отправке голосового сообщения на сервер")


@dp.message_handler(Command("start"))
async def start_command(message: types.Message):
    await message.reply("Отправь мне голосовое сообщение, и я передам его на распознавание")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
