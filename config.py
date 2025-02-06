import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
if TOKEN is None:
    raise ValueError("BOT_TOKEN не найден в переменных окружения. Убедитесь, что файл .env существует и содержит BOT_TOKEN.")

API_BASE_URL = 'https://umu.sibadi.org/api'