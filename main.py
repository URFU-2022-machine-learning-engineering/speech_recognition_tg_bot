import requests
from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from requests_toolbelt.multipart.encoder import MultipartEncoder

import config

bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class UploadState(StatesGroup):
    WaitingForAudio = State()


@dp.message_handler(content_types=[types.ContentType.AUDIO, types.ContentType.VOICE], state="*")
async def handle_audio(message: types.Message):
    # Determine the media type
    media_type = 'Audio' if message.content_type == 'audio' else 'Voice'

    # Download the media file
    media_file = await bot.download_file_by_id(
        file_id=message.audio.file_id) if message.content_type == 'audio' else await bot.download_file_by_id(
        file_id=message.voice.file_id)

    await message.reply('Голосовое сообщение отправлено.')

    # Prepare the multipart/form-data request
    multipart_data = MultipartEncoder(
        fields={'file': (f'{media_type.lower()}.mp3', media_file.read(), 'audio/mpeg')}
    )
    headers = {'Content-Type': multipart_data.content_type}

    # Send the media file to the remote server
    response = requests.post(config.URL, data=multipart_data, headers=headers)

    # Handle the server response
    if response.status_code == 200:
        response_data = response.json()
        detected_language = response_data['detected_language']
        recognized_text = response_data['recognized_text']
        await message.reply(f'Detected Language: {detected_language}\nRecognized Text: {recognized_text}')
    else:
        await message.reply(f'Не удалось загрузить {media_type.lower()}.')

    # Clean up the downloaded media file
    media_file.close()


def main():
    dp.register_message_handler(handle_audio)
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
