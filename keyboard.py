import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from parsing import get_group_id, get_group_schedule
from utils import create_text_schedule


def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Мое расписание"))
    builder.add(KeyboardButton(text="Преподаватели"))
    return builder.as_markup(resize_keyboard=True)

def get_favorite_teachers_keyboard(favorite_teachers):
    builder = InlineKeyboardBuilder()
    for teacher in favorite_teachers:
        # Ограничиваем длину имени преподавателя до 64 символов
        short_name = teacher[:64]
        # Используем сокращенное имя в callback_data
        builder.button(text=teacher, callback_data=f"t_{short_name}")
    # Устанавливаем ширину ряда в 1, чтобы каждая кнопка была на отдельной строке
    builder.adjust(1)
    return builder.as_markup()

async def show_schedule(message: types.Message, user_data):
    user_id = str(message.from_user.id)
    if user_id not in user_data or not user_data[user_id].get("favorite_groups"):
        await message.answer("У вас нет избранных групп. Добавьте группу с помощью команды /addfavorite")
        return

    group_name = user_data[user_id]["favorite_groups"][0]  # Берем первую избранную группу
    group_id = get_group_id(group_name)
    if group_id is None:
        await message.answer(f"Ошибка: группа {group_name} не найдена.")
        return

    schedule = get_group_schedule(group_id)
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']

    for day in days:
        await message.answer(f"{create_text_schedule(schedule, day)}")
        await asyncio.sleep(1)  # Защита от блокировки от Телеграма

