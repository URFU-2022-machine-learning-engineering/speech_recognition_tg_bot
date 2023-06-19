# Telegram Bot for Speech Recognition

This is a Telegram bot implemented in Python that allows users to send audio and voice messages. The bot can upload the received audio/voice messages to a remote server for further processing. The server responds with the detected language and recognized text from the audio/voice message.

## Prerequisites

- Python 3.10 or higher
- Docker (if running in a Docker container)

## Installation

1. Clone the repository:
git clone git@github.com:URFU-2022-machine-learning-engineering/speech_recognition_tg_bot.git
cd speech_recognition_tg_bot


2. Install the required Python dependencies:

pip install -r requirements.txt


3. Set up the bot token and upload URL:

Replace `'YOUR_BOT_TOKEN'` with your actual Telegram bot token in the `main.py` file.

Replace `'https://example.com/upload'` with the URL of your remote server's `/upload` handler in the `main.py` file.

## Usage

1. Run the bot locally:


2. Start a conversation with the bot on Telegram.

3. Send an audio or voice message to the bot. The bot will upload the message to the remote server and respond with the detected language and recognized text.

## Docker

Alternatively, you can run the bot in a Docker container. Make sure you have Docker installed and running on your system.

1. Build the Docker image:

docker build -t telegram-bot .


2. Run the Docker container:

docker run -d --name telegram-bot-container telegram-bot


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
