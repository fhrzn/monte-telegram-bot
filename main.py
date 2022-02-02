import os
from dotenv import load_dotenv
from bot import Bot

load_dotenv()

API_KEY = os.getenv('API_KEY')

if __name__ == '__main__':
    bot = Bot()
    bot.build()
    bot.start()