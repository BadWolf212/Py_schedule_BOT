import asyncio
import json
import os

from aiogram import Router, types
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message


from parsing import get_group_schedule, get_group_id

base_router = Router(name=__name__)


# Файл для хранения данных
USER_DATA_FILE = 'user_data.json'


# Загрузить существующие данные пользователя или создать пустой словарь
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}


# Сохранить данные о пользователе в файл
def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file, indent=2)


# Команда регистрации пользователя
@base_router.message(Command("register"))
async def register_user(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    user_data = load_user_data()

    if str(user_id) in user_data:
        await message.answer("Вы уже зарегестрированы.")
        return

    user_data[str(user_id)] = {
        "username": username,
        "registered_at": message.date.isoformat()
    }

    save_user_data(user_data)
    await message.answer("Регистрация успешна!")


# Проверка статуса регистрации
@base_router.message(Command("status"))
async def check_status(message: types.Message):
    user_id = message.from_user.id
    user_data = load_user_data()

    if str(user_id) in user_data:
        user_info = user_data[str(user_id)]
        await message.answer(
            f"Вы зарегестрированы.\nИмя пользователя: {user_info['username']}\nВремя регистрации: {user_info['registered_at']}")
    else:
        await message.answer("Вы не зарегестрированы. Используйте /register для регистрации.")


# Приветственное сообщение
def get_start_text():
    with open('start_message.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def create_text_schedule(schedule, day):
    txt = ''
    txt+=f'{day}\n'
    lessons = schedule[day]
    for lesson in lessons:
        txt += f'Дисциплина: {lesson["дисциплина"]}\n'
        txt += f'Аудитория: {lesson["аудитория"]}\n'
        txt += f'Номер занятия: {lesson["номерЗанятия"]}\n'
        txt += f'Преподаватель: {lesson["фиоПреподавателя"]}\n'
        txt += f'Время: {lesson["начало"][:5]} -- {lesson["конец"][:5]}\n'
        txt += '\n ***************************************\n\n'
    if txt == f'{day}\n':
        return f'В {day} пар нет, отдыхай!'

    return txt

@base_router.message(CommandStart())
async def command_current_handler(message: Message) -> None:
    await message.answer(f"{get_start_text()}")

# Команда current
@base_router.message(Command('current'))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    group_name = command.args
    if group_name is None:
        await message.answer('Введите название группы. \n/current БИ-22Э1 - (пример)')
        return

    group_id = get_group_id(group_name)

    if group_id is None:
        await message.answer('Такой группы не существует или вы ввели ее неправильно. \nУчитывайте регистр!!!')
        return

    schedule = get_group_schedule(group_id)
    days = ['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота']

    for day in days:
        await message.answer(f"{create_text_schedule(schedule, day)}")
        await asyncio.sleep(1) # Защита от блокировки от Телеграма


@base_router.message()
async def echo_handler(message: Message) -> None:

    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:

        await message.answer("Nice try!")
