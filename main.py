from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
import config


# Инициализация бота и диспетчера
bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(content_types=types.ContentType.VOICE)
async def process_voice_message(message: types.Message, state: FSMContext):
    # Сохранение голосового сообщения в файл
    voice_file_id = message.voice.file_id
    voice_file = await bot.get_file(voice_file_id)
    voice_file_path = voice_file.file_path
    voice_file_data = await bot.download_file(voice_file_path)

    # Сохранение файла в формате mp3 на сервере
    mp3_file_path = 'E:/file_1.mp3'
    with open(mp3_file_path, 'wb') as mp3_file:
        mp3_file.write(voice_file_data.getvalue())

    # Отправка ответного сообщения
    await message.reply('Голосовое сообщение сохранено в формате MP3')


@dp.message_handler(Command('start'))
async def start_command(message: types.Message):
    await message.reply('Привет! Отправь мне голосовое сообщение, и я сохраню его в формате MP3.')


if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
