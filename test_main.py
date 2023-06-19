from unittest.mock import MagicMock, patch

import pytest
import requests
from aiogram import types
from requests_toolbelt.multipart.encoder import MultipartEncoder

import main


@pytest.fixture
def voice_message():
    return MagicMock(spec=types.Message, content_type=types.ContentType.VOICE)


@pytest.fixture
def mocked_bot():
    return MagicMock()


@pytest.fixture
def mocked_storage():
    return MagicMock()


@pytest.fixture
def mocked_dispatcher(mocked_bot, mocked_storage):
    return MagicMock(bot=mocked_bot, storage=mocked_storage)


@pytest.fixture
def mocked_file():
    file = MagicMock()
    file.file_path = "voice_file_path"
    return file


@pytest.fixture
def mocked_download_file(mocked_file):
    return MagicMock(return_value=mocked_file)


@pytest.fixture
def mocked_open():
    file = MagicMock()
    file.__enter__.return_value = file
    return MagicMock(return_value=file)


@pytest.fixture
def mocked_requests_post():
    return MagicMock(spec=requests.Response, status_code=200, json=lambda: {"detected_language": "en", "recognized_text": "Hello"})


def test_process_voice_message(voice_message, mocked_dispatcher, mocked_download_file, mocked_open, mocked_requests_post):
    voice_message.voice.file_id = "voice_file_id"
    voice_message.reply = MagicMock()

    mocked_bot = mocked_dispatcher.bot
    mocked_bot.get_file.return_value = MagicMock(file_path="voice_file_path")
    mocked_bot.download_file = mocked_download_file

    with patch("builtins.open", mocked_open), patch.object(requests, "post", mocked_requests_post):
        main.process_voice_message(voice_message, mocked_dispatcher)

    mocked_bot.get_file.assert_called_once_with("voice_file_id")
    mocked_bot.download_file.assert_called_once_with("voice_file_path")

    mocked_open.assert_called_once_with("config.PATH", "wb")
    mocked_open.return_value.write.assert_called_once_with(mocked_download_file().getvalue())

    voice_message.reply.assert_called_once_with("Голосовое сообщение сохранено")
    mocked_requests_post.assert_called_once_with(
        main.web_server_url,
        data=MultipartEncoder(fields={"file": ("mp3_file_path", mocked_open.return_value, "audio/mpeg")}),
        headers={"Content-Type": mocked_open.return_value.content_type},
    )

    voice_message.reply.assert_called_with("Detected Language: en\nRecognized Text: Hello")


def test_process_voice_message_error(voice_message, mocked_dispatcher, mocked_download_file, mocked_open):
    voice_message.voice.file_id = "voice_file_id"
    voice_message.reply = MagicMock()

    mocked_bot = mocked_dispatcher.bot
    mocked_bot.get_file.return_value = MagicMock(file_path="voice_file_path")
    mocked_bot.download_file = mocked_download_file

    mocked_requests_post = MagicMock(spec=requests.Response, status_code=500)
    mocked_requests_post.raise_for_status = MagicMock(side_effect=requests.HTTPError)

    with patch("builtins.open", mocked_open), patch.object(requests, "post", mocked_requests_post):
        main.process_voice_message(voice_message, mocked_dispatcher)

    mocked_bot.get_file.assert_called_once_with("voice_file_id")
    mocked_bot.download_file.assert_called_once_with("voice_file_path")

    mocked_open.assert_called_once_with("config.PATH", "wb")
    mocked_open.return_value.write.assert_called_once_with(mocked_download_file().getvalue())

    voice_message.reply.assert_called_once_with("Голосовое сообщение сохранено")
    mocked_requests_post.assert_called_once_with(
        main.web_server_url,
        data=MultipartEncoder(fields={"file": ("mp3_file_path", mocked_open.return_value, "audio/mpeg")}),
        headers={"Content-Type": mocked_open.return_value.content_type},
    )

    voice_message.reply.assert_called_with("Ошибка при отправке голосового сообщения на сервер")


def test_start_command(mocked_dispatcher):
    message = MagicMock(spec=types.Message)
    message.reply = MagicMock()

    main.start_command(message)

    message.reply.assert_called_once_with("Отправь мне голосовое сообщение, и я передам его на распознавание")
