import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from parsing import get_group_id, get_group_schedule

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Мое расписание"))
    return builder.as_markup(resize_keyboard=True)

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

def create_text_schedule(schedule, day):
    txt = f'{day}\n'
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