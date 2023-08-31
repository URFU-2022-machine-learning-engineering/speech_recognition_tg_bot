import logging
import os
import tempfile

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from requests_toolbelt.multipart.encoder import MultipartEncoder

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


class FileManager:
    @staticmethod
    async def save_voice_message(voice_file_data):
        # Save voice message to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(voice_file_data.read())
            temp_file_path = temp_file.name
            logging.debug(f"Saved voice message to {temp_file_path}")
        return temp_file_path

    @staticmethod
    async def delete_temp_file(temp_file_path):
        if os.path.exists(temp_file_path):
            logging.debug(f"Deleted temporary file {temp_file_path}")
            os.remove(temp_file_path)


class VoiceBot:
    def __init__(self, token: str, url: str):
        self.token = token if token else os.getenv("TOKEN")
        self.url = url if url else os.getenv("URL")
        self.bot = Bot(token=self.token)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(bot=self.bot, storage=self.storage)
        self.file_manager = FileManager()
        logging.debug(f"Voice bot initiated to URL {self.url}")

    async def send_voice_message(self, message, temp_file_path):
        try:
            with open(temp_file_path, "rb") as file:
                multipart_data = MultipartEncoder(fields={"file": (os.path.basename(temp_file_path), file, "audio/mpeg")})
                headers = {"Content-Type": multipart_data.content_type}
                response = requests.post(self.url, data=multipart_data, headers=headers)
                logging.debug(f"Request sent to {self.url}, received response code {response.status_code} " f"and response text {response.text}")
                response_data = response.json()
                detected_language = response_data["detected_language"]
                recognized_text = response_data["recognized_text"]
                await self.send_response_with_buttons(
                    message=message,
                    detected_language=detected_language,
                    recognized_text=recognized_text,
                )
        except (requests.RequestException, FileNotFoundError) as e:
            logging.error(f"There was an error during request {e}")
            await self.send_error_response_with_buttons(message)

    @staticmethod
    async def send_response_with_buttons(message, detected_language, recognized_text):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        retry_button = types.InlineKeyboardButton("Retry", callback_data="retry")
        cancel_button = types.InlineKeyboardButton("Cancel", callback_data="cancel")
        keyboard.add(retry_button, cancel_button)

        await message.reply(
            f"Detected Language: {detected_language}\nRecognized Text: {recognized_text}",
            reply_markup=keyboard,
        )

    @staticmethod
    async def send_error_response_with_buttons(message):
        keyboard = types.InlineKeyboardMarkup()
        retry_button = types.InlineKeyboardButton("Retry", callback_data="retry")
        cancel_button = types.InlineKeyboardButton("Cancel", callback_data="cancel")
        keyboard.add(retry_button, cancel_button)

        await message.reply(
            "Ошибка при отправке голосового сообщения на сервер",
            reply_markup=keyboard,
        )

    def run(self):
        @self.dp.message_handler(content_types=[types.ContentType.AUDIO, types.ContentType.VOICE])
        async def process_voice_message(message: types.Message):
            # Download audio/voice message
            if message.audio:
                audio_file_id = message.audio.file_id
            else:
                audio_file_id = message.voice.file_id

            audio_file = await self.bot.get_file(audio_file_id)
            audio_file_path = audio_file.file_path
            audio_file_data = await self.bot.download_file(audio_file_path)

            # Save audio/voice message and send it for processing
            temp_file_path = await self.file_manager.save_voice_message(audio_file_data)
            await self.send_voice_message(message, temp_file_path)

        @self.dp.callback_query_handler(lambda c: c.data == "retry")
        async def process_retry_callback(callback_query: types.CallbackQuery):
            await self.bot.answer_callback_query(callback_query.id)
            await self.bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
            await self.send_voice_message(callback_query.message, callback_query.from_user.id)

        @self.dp.callback_query_handler(lambda c: c.data == "cancel")
        async def process_cancel_callback(callback_query: types.CallbackQuery):
            await self.bot.answer_callback_query(callback_query.id)
            await self.bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
            await self.file_manager.delete_temp_file(callback_query.from_user.id)

        @self.dp.message_handler(Command("start"))
        async def start_command(message: types.Message):
            logging.debug("User has launched the bot")
            await message.reply("Отправь мне голосовое сообщение, и я передам его на распознавание")

        executor.start_polling(self.dp, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.getLogger("__name__")

    voice_bot = VoiceBot(token=os.getenv("TOKEN"), url=os.getenv("URL"))
    voice_bot.run()
