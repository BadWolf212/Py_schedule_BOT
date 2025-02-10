import asyncio
import json
import os
from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery

from constants import DAYS_OF_WEEK
from keyboard import get_main_keyboard, show_schedule, get_favorite_teachers_keyboard
from parsing import get_group_schedule, get_group_id, get_teacher_id, get_teacher_schedule
from utils import create_text_schedule

base_router = Router(name=__name__)


# Файл для хранения данных
USER_DATA_FILE = 'user_data.json'


@base_router.message(F.text == "Мое расписание")
async def show_my_schedule(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()

    if user_id not in user_data or not user_data[user_id].get("favorite_groups"):
        await message.answer("У вас нет избранных групп. Добавьте группу с помощью команды /addfavorite")
        return

    await show_schedule(message, user_data)

@base_router.message(F.text == "Преподаватели")
async def show_favorite_teachers(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()

    if user_id not in user_data or not user_data[user_id].get("favorite_teachers"):
        await message.answer("У вас нет избранных преподавателей. Добавьте преподавателя с помощью команды /addteacher")
        return

    favorite_teachers = user_data[user_id]["favorite_teachers"]
    keyboard = get_favorite_teachers_keyboard(favorite_teachers)
    await message.answer("Выберите преподавателя:", reply_markup=keyboard)


@base_router.callback_query(F.data.startswith("t_"))
async def show_teacher_schedule(callback_query: CallbackQuery):
    short_name = callback_query.data.split("_", 1)[1]

    # Найдите полное имя преподавателя
    user_data = load_user_data()
    user_id = str(callback_query.from_user.id)
    full_name = next((t for t in user_data[user_id]["favorite_teachers"] if t.startswith(short_name)), None)

    if not full_name:
        await callback_query.answer("Преподаватель не найден.")
        return

    teacher_id = get_teacher_id(full_name)

    if teacher_id is None:
        await callback_query.answer("Ошибка: преподаватель не найден.")
        return

    schedule = get_teacher_schedule(teacher_id)
    days = [DAYS_OF_WEEK]

    await callback_query.answer()
    for day in days:
        await callback_query.message.answer(f"{create_text_schedule(schedule, day)}")
        await asyncio.sleep(1)  # Защита от блокировки от Телеграма

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
        await message.answer("Вы уже зарегистрированы.", reply_markup=get_main_keyboard())
        return

    user_data[str(user_id)] = {
        "username": username,
        "registered_at": message.date.isoformat(),
        "favorite_groups": [],
        "favorite_teachers":[]
    }

    save_user_data(user_data)
    await message.answer("Регистрация успешна!", reply_markup=get_main_keyboard())

# Проверка статуса регистрации
@base_router.message(Command("status"))
async def check_status(message: types.Message):
    user_id = message.from_user.id
    user_data = load_user_data()

    if str(user_id) in user_data:
        user_info = user_data[str(user_id)]
        favorite_groups = ", ".join(user_info.get("favorite_groups", []))
        favorite_teachers = ", ".join(user_info.get("favorite_teachers", []))
        await message.answer(
            f"Вы зарегистрированы.\nИмя пользователя: {user_info['username']}\n"
            f"Время регистрации: {user_info['registered_at']}\n"
            f"Избранные группы: {favorite_groups or 'нет'}\n"
            f"Избранные преподаватели: {favorite_teachers or 'нет'}",
            reply_markup=get_main_keyboard())
    else:
        await message.answer("Вы не зарегистрированы. Используйте /register для регистрации.", reply_markup=get_main_keyboard())

# Команда добавления группы в избранное
@base_router.message(Command("addfavorite"))
async def add_favorite_group(message: Message, command: CommandObject):
    user_id = message.from_user.id
    group_name = command.args

    if group_name is None:
        await message.answer('Введите название группы. \n/addfavorite БИ-22Э1 - (пример)')
        return

    group_id = get_group_id(group_name)

    if group_id is None:
        await message.answer('Такой группы не существует или вы ввели ее неправильно. \nУчитывайте регистр!!!')
        return

    user_data = load_user_data()

    if str(user_id) not in user_data:
        await message.answer("Вы не зарегистрированы. Используйте /register для регистрации.")
        return

    if "favorite_groups" not in user_data[str(user_id)]:
        user_data[str(user_id)]["favorite_groups"] = []

    if group_name in user_data[str(user_id)]["favorite_groups"]:
        await message.answer(f"Группа {group_name} уже в избранном.")
    else:
        user_data[str(user_id)]["favorite_groups"].append(group_name)
        save_user_data(user_data)
        await message.answer(f"Группа {group_name} добавлена в избранное.")

@base_router.message(Command("addteacher"))
async def add_favorite_teacher(message: Message, command: CommandObject):
    user_id = message.from_user.id
    teacher_name = command.args

    if teacher_name is None:
        await message.answer('Введите имя преподавателя. \n/addteacher Иванов И.И. - (пример)')
        return

    teacher_id = get_teacher_id(teacher_name)

    if teacher_id is None:
        await message.answer('Такого преподавателя не существует или вы ввели его имя неправильно. \nУчитывайте регистр!!!')
        return

    user_data = load_user_data()

    if str(user_id) not in user_data:
        await message.answer("Вы не зарегистрированы. Используйте /register для регистрации.")
        return

    if "favorite_teachers" not in user_data[str(user_id)]:
        user_data[str(user_id)]["favorite_teachers"] = []

    if teacher_name in user_data[str(user_id)]["favorite_teachers"]:
        await message.answer(f"Преподаватель {teacher_name} уже в избранном.")
    else:
        user_data[str(user_id)]["favorite_teachers"].append(teacher_name)
        save_user_data(user_data)
        await message.answer(f"Преподаватель {teacher_name} добавлен в избранное.")

# Приветственное сообщение
def get_start_text():
    with open('start_message.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    return text


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

@base_router.message(Command('teacher'))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    teacher_name = command.args
    if teacher_name is None:
        await message.answer('Введите имя препода. \n/teacher Толкачева Елена Викторовна - (пример)')
        return

    teacher_id = get_teacher_id(teacher_name)

    if teacher_id is None:
        await message.answer('Не нашел такого преподавателя :(. \nПопробуйте написать фамилию, имя и отчество полностью')
        return

    schedule = get_teacher_schedule(teacher_id)
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
