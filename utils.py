from aiogram.utils.markdown import bold, italic, code

def create_text_schedule(schedule, day):
    txt = f"{bold(day.upper())}\n\n"
    lessons = schedule[day]

    if not lessons:
        return f"{italic('В этот день пар нет, отдыхай! 🎉')}"
    for lesson in lessons:
        txt += f'{lesson["номерЗанятия"]}\n'
        txt += f'Дисциплина: {lesson["дисциплина"]}\n'
        txt += f'Аудитория: {lesson["аудитория"]}\n'
        txt += f'Преподаватель: {lesson["фиоПреподавателя"]}\n'
        txt += f'Время: {lesson["начало"][:5]} -- {lesson["конец"][:5]}\n'
        txt += "\n" + "—" * 20 + "\n\n"
    if txt == f'{day}\n':
        return f'В {day} пар нет, отдыхай!'

    return txt