import requests
import datetime


def get_group_id(group_name:str): # Функция для получения ID группы, по которому будем искать расписание конкретной группы
    url = 'https://umu.sibadi.org/api/raspGrouplist?year=2024-2025'

    data = requests.get(url).json()
    groups_data = data['data']
    for group_data in groups_data:
        if group_data['name'] == group_name:
            return group_data['id']




current_date = datetime.date.today().isoformat()

def get_group_schedule(group_id): # Функция для получения расписания группы по ее ID
    url = f'https://umu.sibadi.org/api/Rasp?idGroup={group_id}&sdate={current_date}'
    data = requests.get(url).json()['data']['rasp']
    schedule = \
    {
        'Понедельник': [],
        'Вторник': [],
        'Среда': [],
        'Четверг': [],
        'Пятница': [],
        'Суббота': [],
    }
    for day in data:
        schedule[day['день_недели']].append(day)

    return schedule


def get_teacher_id(teacher_name:str): # Функция для получения ID препода, по которому будем искать расписание конкретного препода
    url = 'https://umu.sibadi.org/api/raspTeacherlist?year=2024-2025'

    data = requests.get(url).json()
    teachers_data = data['data']
    for teacher_data in teachers_data:
        if teacher_data['name'] == teacher_name:
            return teacher_data['id']


def get_teacher_schedule(teacher_id): # Функция для получения расписания препода по ее ID
    url = f'https://umu.sibadi.org/api/Rasp?idTeacher={teacher_id}&sdate={current_date}'
    data = requests.get(url).json()['data']['rasp']
    teacher_schedule = \
    {
        'Понедельник': [],
        'Вторник': [],
        'Среда': [],
        'Четверг': [],
        'Пятница': [],
        'Суббота': [],
    }
    for day in data:
        teacher_schedule[day['день_недели']].append(day)

    return teacher_schedule
