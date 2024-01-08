import uuid
from datetime import date, time
from random import randint, choice, sample


def get_next_char():
    """
    Генератор следующего символа для создания случайных имен
    Выдает гласную после согласной и наоборот в 80% случаев
    :return:
    """
    first = 'aeiou'
    second = 'bcdfghjklmnpqrstvwxyz'

    if choice([True, False]):
        first, second = second, first

    while True:
        yield choice(first)
        if choice([True, True, True, True, False]):
            first, second = second, first


# Создание генератора
next_char = get_next_char()


def get_random_name(min_chars=3, max_chars=9):
    """
    Генерация случайного человекоподобного имени из комбинации чередующихся гласных и согласных букв
    :param min_chars: минимальная длина имени
    :param max_chars: максимальная длина имени
    :return: строка с именеем с большой буквы
    """
    name = ''.join([
        next(next_char) for i in range(randint(min_chars, max_chars))
    ])
    return name.capitalize()


def get_initial_tables():
    """
    Генерация SQL запросов для создания демо-таблиц
    :return: кортеж из 4 строк-таблиц
    """
    festivals_table = """
        CREATE TABLE IF NOT EXISTS festivals (
            festival_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(32),
            place VARCHAR(32),
            date DATE
        )
    """

    # Создание таблицы для Band
    bands_table = """
        CREATE TABLE IF NOT EXISTS bands (
            band_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(32),
            genre VARCHAR(32),
            city VARCHAR(32)
        )
    """

    # Создание таблицы для Schedule
    schedule_table = """
        CREATE TABLE IF NOT EXISTS schedules (
            schedule_id INT AUTO_INCREMENT PRIMARY KEY,
            festival_id INT NOT NULL,
            band_id INT NOT NULL,
            time TIME NOT NULL,
            FOREIGN KEY (festival_id) REFERENCES festivals(festival_id),
            FOREIGN KEY (band_id) REFERENCES bands(band_id)
        )
    """

    manager_table = """
        CREATE TABLE IF NOT EXISTS managers (
            manager_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(32),
            last_name VARCHAR(32),
            email VARCHAR(64)
        )
    """
    #
    return festivals_table, bands_table, schedule_table, manager_table


def get_new_table():
    """ SQL запрос дополнительной таблицы для демо """
    return """
        CREATE TABLE IF NOT EXISTS new_table (
            some_id INT AUTO_INCREMENT PRIMARY KEY,
            some_name VARCHAR(32),
            some_date DATE,
            some_int INT
        )
    """


def get_sql_for_insert_rows():
    """
    Генерация SQL-запросов для массовой вставки данных в созданные таблицы
    :return: кортеж из 4 строк с запросами
    """
    festivals = "INSERT INTO festivals (festival_id, name, place, date) VALUES (%s, %s, %s, %s)"
    bands = "INSERT INTO bands (band_id, name, genre, city) VALUES (%s, %s, %s, %s)"
    schedule = "INSERT INTO schedules (festival_id, band_id, time) VALUES (%s, %s, %s)"
    managers = "INSERT INTO managers (first_name, last_name, email) VALUES (%s, %s, %s)"

    return festivals, bands, schedule, managers


def get_initial_data(as_tuples=True):
    """
    Генерация демо данных для наполнения таблиц
    :param as_tuples: флаг для возвращения результата в виде плоских кортежей, а не словарей
    :return: 4 словаря или кортежа с демо-данными
    """
    lim = 5

    # Генерация псевдо жанров музыки
    genres = [
        f"{choice(['Indi-', 'Hard-', ''])}{get_random_name(4,6)}{choice(['-Rock', '-Metal', ''])}" for i in range(10)
    ]

    # Генерация данных для таблицы с фестивалями
    festivals_data = [
        {
            'festival_id': i+1,
            'name': get_random_name(),
            'place': get_random_name(),
            'date': date(2024, randint(1, 12), randint(1, 28))
        }
        for i in range(randint(lim, lim))]

    # Генерация данных для таблицы музыкальных групп
    bands_data = [
        {
            'band_id': i+1,
            'name': get_random_name(),
            'genre': choice(genres),
            'city': get_random_name()
        }
        for i in range(randint(lim, lim))
    ]

    # Генерация данных для таблицы с расписаниями
    schedules_data = [
        {
            'festival_id': festival['festival_id'],
            'band_id': band['band_id'],
            'time': time(randint(12, 22), choice([0, 30]))  # могут быь совпадения, как и в жизни)
        }
        for festival in sample(festivals_data, lim) for band in sample(bands_data, lim)
    ]

    # Генерация данных для таблицы менеджеров
    managers_data = [
        {
            'first_name': first_name,
            'last_name': last_name,
            'email': f"({first_name}.{last_name}@{domain}-festivals.com"
        }
        for domain in [get_random_name()]
        for i in range(randint(lim, lim))
        for first_name in [get_random_name(3, 6)]
        for last_name in [get_random_name(5, 10)]
    ]

    # Превращение словарей в кортежи. Словари были удобны когда я думал делать через SQLAlchemy
    if as_tuples:
        festivals_data = [(f["festival_id"], f["name"], f["place"], f["date"]) for f in festivals_data]
        bands_data = [(f["band_id"], f["name"], f["genre"], f['city']) for f in bands_data]
        schedules_data = [(f["festival_id"], f["band_id"], f["time"]) for f in schedules_data]
        managers_data = [(f["first_name"], f["last_name"], f["email"]) for f in managers_data]
    #
    return festivals_data, bands_data, schedules_data, managers_data
