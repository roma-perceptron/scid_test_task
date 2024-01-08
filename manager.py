import utils
import mysql.connector
from config import Config
from typing import Union


class BaseManager:
    """
    Базовый класс менеджера БД с общим функционалом для управления БД
    """
    def __init__(self, db_config):
        self.config = db_config
        self.connection = None
        self.cursor = None
        self.table_names = None
        #
        self.connect()
        self.get_tables()

    def connect(self):
        """
        Подключение к базе данных
        """
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor()

            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                print(f"Успешное подключение к серверу MySQL ({db_info}): {self.connection.database}")

        except mysql.connector.Error as exp:
            print(f"Ошибка при подключении к базе данных: {exp}")

    def disconnect(self):
        """
        Закрытие соединения
        """
        bd_name = self.connection.database
        if self.connection.is_connected():
            self.connection.close()
            print(f"Соединение с базой данных {bd_name} закрыто")

    def get_tables(self, silent=False):
        """
        Получение списка всех таблиц в базе данных
        :param silent: Отключение уведомлений в консоли
        :return: Список имен таблиц
        """
        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()
        tables = [table[0] for table in tables]
        self.table_names = tables

        if not silent:
            if tables:
                print(f'В Базе Данных {self.connection.database} существуют следующие таблицы:')
                for table in tables:
                    print(' '*3, table)
            else:
                print(f'База Данных {self.connection.database} пуста, нет ни одной таблицы..')
        #
        return tables

    def _add_column(self, table_name: str, column_signature: str):
        """
        Формирование SQL-запроса для добавления столбца в таблицу
        :param table_name: имя таблицы
        :param column_signature: параметры добавляемого столбца (имя, тип, прочее)
        """
        if table_name in self.table_names:
            query = f"ALTER TABLE {table_name} ADD COLUMN {column_signature};"
            self.send_to_db(query)

    def _change_column(self, table: str, column_signature_test: str):
        """
        Формирование SQL-запроса для изменения существующего столбца
        :param table: имя таблицы
        :param column_signature_test: новые параметры для изменяемого столбца (имя, тип, прочее)
        """
        query = f'ALTER TABLE {table} MODIFY COLUMN {column_signature_test};'
        self.send_to_db(query)

    def _drop_column(self, table: str, column: str):
        """
        Формирование SQL-запроса для удаления столбца
        :param table: имя таблицы
        :param column: имя столбца
        """
        query = f'ALTER TABLE {table} DROP COLUMN {column};'
        self.send_to_db(query)

    def _drop_table(self, table_name):
        """
        Формирование SQL-запроса для удаления таблицы
        :param table_name: имя таблицы
        :return: Кортеж с флагом итога операции и выброшенным исключением (при возникновении)
        """
        try:
            query = f"DROP TABLE {table_name}"
            self.send_to_db(query)
            self.get_tables(silent=True)
            return True, None
        except Exception as exp:
            return False, exp

    def drop_tables(self):
        """
        Удаление всех таблиц - очистка БД
        """
        existing_tables = self.get_tables(silent=True)

        # удаляю в while цикле поочередно пробуя каждую таблицу (из-за связей и ограничений)
        # можно было просто в обратном порядке, но это не дает 100% гарантии
        while existing_tables:
            is_dropped, exp = self._drop_table(existing_tables[0])
            if is_dropped:
                existing_tables.pop(0)
            elif isinstance(exp, mysql.connector.errors.DatabaseError) and exp.errno == 3730:
                # это ошибка из-за неверной очереди удаления таблиц
                existing_tables.append(existing_tables.pop(0))
            else:
                # иная ошибка, пробрасываю наверх
                raise exp
            #
            self.connection.commit()

    def send_to_db(self, query: str, params: Union[None, list] = None):
        """
        Выполнение SQL запроса и закрепление результата
        :param query: Строка со SQL-запросом
        :param params: Параметры для массовой записи (опционально)
        """
        if params:
            self.cursor.executemany(query, params)
        else:
            self.cursor.execute(query)
        self.connection.commit()

    def make_initial_tables(self):
        """
        Наполнение БД первичными данными
        :return:
        """
        print('Создаю и наполняю демо-таблицы')
        for table, insert, data in zip(utils.get_initial_tables(),
                                       utils.get_sql_for_insert_rows(),
                                       utils.get_initial_data()):
            self.send_to_db(table)
            self.send_to_db(insert, data)
        self.get_tables()

    def get_structure(self):
        """
        Сбор данных о структуре БД
        :return: Словарь данными о таблицах и столбцах внутри
        """
        structure = {}
        for table_name in self.table_names:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            is_empty = not bool(self.cursor.fetchone()[0])

            query = f"""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM information_schema.COLUMNS
                WHERE TABLE_NAME = '{table_name}'
            """
            self.cursor.execute(query)
            columns_info = self.cursor.fetchall()
            columns_data = [column[0] for column in columns_info]
            structure[table_name] = {'is_empty': is_empty, 'columns': columns_data}
        #
        return structure


class TestManager(BaseManager):
    """
    Класс с функционалом для внесения изменений в тестовую БД:
    """
    def __init__(self, db_config):
        super().__init__(db_config)

    def add_column(self, table_name: str='bands', column_signature: str = 'country VARCHAR(32)'):
        """ Добавление столбца """
        self._add_column(table_name=table_name, column_signature=column_signature)

    def drop_column(self, table_name: str = 'bands', column_name: str = 'city'):
        """ Удаление столбца """
        self._drop_column(table=table_name, column=column_name)

    def change_column(self, table_name: str = 'festivals', column_signature: str = 'name VARCHAR(64)'):
        """ Изменение столбца """
        self._change_column(table_name, column_signature)

    def add_table(self):
        """ Добавление таблицы """
        self.send_to_db(utils.get_new_table())

    def remove_table(self, table_name: str = 'managers'):
        """ Удаление таблицы """
        if table_name in self.table_names:
            dropped, exp = self._drop_table(table_name=table_name)
            if not dropped:
                raise exp

    def make_changes(self):
        """ Применение всех вариантов изменений """
        self.add_column()
        self.change_column()
        self.drop_column()
        self.add_table()
        self.remove_table()


class ProdManager(BaseManager):
    """
    Класс с функционалом для управления боевой версией БД и внесение в нее изменений по образцу тестовой БД
    """
    def __init__(self, db_config):
        super().__init__(db_config)

    @staticmethod
    def get_column_signature(column: str, table: str, bd: Union[TestManager, BaseManager]):
        """
        Извлечение строки с параметрами отдельного столбца
        :param column: имя столбца
        :param table: имя таблицы
        :param bd: БД (экземпляр класса менеджера)
        :return: строка с параметрами столбца
        """
        source_cursor = bd.connection.cursor()
        query = f"SHOW CREATE TABLE {table}"
        source_cursor.execute(query)
        table_signature = source_cursor.fetchone()[1].split('\n')
        column_signature = [c.strip() for c in table_signature if c.strip().startswith(f'`{column}`')][0][:-1]
        #
        return column_signature

    def copy_table(self, table_name: str, source_db):
        """
        Копирование таблицы (только структуры, без данных) из внешней БД
        :param table_name: имя таблицы
        :param source_db: БД-донор, тестовая БД (экземпляр класса менеджера)
        """
        source_cursor = source_db.connection.cursor()
        target_cursor = self.connection.cursor()

        # Получение информации о структуре таблицы из исходной БД
        query = f"SHOW CREATE TABLE {table_name}"
        source_cursor.execute(query)
        table_structure = source_cursor.fetchone()[1]

        # Создание таблицы с аналогичной структурой в целевой БД
        target_cursor.execute(f"USE {self.connection.database}")
        target_cursor.execute(table_structure.replace(table_name, table_name))

        # Фиксация изменений
        self.connection.commit()

    def copy_column(self, column: str, table: str, source_bd: TestManager):
        """
        Копирование отдельного столбца (без данных)
        :param column: имя столбца
        :param table: имя таблицы
        :param source_bd: БД-донор, тестовая БД (экземпляр класса менеджера)
        """
        column_signature = self.get_column_signature(column=column, table=table, bd=source_bd)
        self._add_column(table_name=table, column_signature=column_signature)

    def compare_and_fit(self, test_db: TestManager):
        """
        Комплекс операций по сравнению текущей БД (боевой) с заданной тестовой и приведению к единому виду.
        :param test_db: БД-донор / тестовая БД (экземпляр класса менеджера)
        """
        print('\nНачинаем сравнивать и приводить боевую БД к виду тестовой')

        # сбор данных о структуре баз
        test_structure = test_db.get_structure()
        prod_structure = self.get_structure()

        print(f'Тестовая БД состоит из {len(test_structure)} таблиц: {sorted(test_structure.keys())}')
        print(f'Боевая БД состоит из {len(prod_structure)} таблиц: {sorted(prod_structure.keys())}')

        # В prod нет таблицы которая появилась в test - копируем
        added_tables = set(test_structure) - set(prod_structure)
        if added_tables:
            print(f'Добавленных таблиц в тестовую БД: [{len(added_tables)}]. Создаю их на боевой версии.')
            for table in added_tables:
                self.copy_table(table_name=table, source_db=test_db)
                print(' '*3, 'Создана:', table)

        # В prod есть таблица которой уже нет в test - удаляем
        dropped_tables = set(prod_structure) - set(test_structure)
        if dropped_tables:
            print(f'Удаленных таблиц в тестовой БД: [{len(dropped_tables)}]. Пробую удалить их с боевой.')
            for table in dropped_tables:
                is_dropped, _ = self._drop_table(table)
                if is_dropped:
                    print(' '*3, 'Удалил:', table)
                else:
                    print(' '*3, 'Не удалось удалить таблицу в автоматическом режиме:', table,
                          'вероятно наличие связанных данных и требуется внимание разработчика.')

        # Таблицы которые есть в обеих базах необходимо проверить на единообразие полей (столбцов)
        intersecting_tables = set(test_structure) & set(prod_structure)
        print(f'Общих таблиц в тестовой и боевой БД: [{len(intersecting_tables)}]. Проверяю столбцы.')
        for table in intersecting_tables:
            # На уровне столбцов та же история: новый / удаленный / измененный столбец
            print(' '*3, 'В таблице', table, ':')
            test_columns = test_structure[table]['columns']
            prod_columns = prod_structure[table]['columns']

            # Столбец который появился в test и отсутствует в prod - добавляем
            added_columns = set(test_columns) - set(prod_columns)
            for column in added_columns:
                self.copy_column(column=column, table=table, source_bd=test_db)
                print(' '*6, 'Скопировал столбец', column, 'в таблицу', table)

            # Столбец который был удален из test, но еще есть на prod - удаляем
            dropped_columns = set(prod_columns) - set(test_columns)
            for column in dropped_columns:
                self._drop_column(table, column)
                print(' '*6, 'Удалил столбец', column, 'таблицы', table)

            # Столбцы которые есть и там и там нужно проверить на одинаковость параметров и в случае различий
            # привести к виду test-столбца
            intersecting_columns = set(test_columns) & set(prod_columns)
            for column in intersecting_columns:
                column_signature_test = self.get_column_signature(column, table, test_db)
                column_signature_prod = self.get_column_signature(column, table, self)
                if column_signature_prod != column_signature_test:
                    print(' '*6, 'Нужно заменить столбец', column, 'таблицы', table)
                    print(' '*6, column_signature_prod, '-->', column_signature_test)
                    #
                    self._change_column(table, column_signature_test)
        #
        print('\n\nГотово! Теперь структура боевой БД приведена к виду тестовой!')


class MergeManager:
    """
    Верхнеуровневый класс для слияния двух версий БД
    """
    def __init__(self, db_test: TestManager = None, db_prod: ProdManager = None, configs_for_demo: Config = None):
        self.db_test = db_test
        self.db_prod = db_prod
        self.configs_for_demo = configs_for_demo

    def merge(self):
        """ Запуск процесса сверки и слияния структур БД"""
        self.db_prod.compare_and_fit(test_db=self.db_test)

    def show_demo(self):
        """
        Демо по слиянию двух версий БД: очистка, наполнение демо-данными, изменение и слияние структур
        """
        self.db_test = TestManager(self.configs_for_demo.database_test.to_dict())
        self.db_prod = ProdManager(self.configs_for_demo.database_prod.to_dict())
        #
        self.db_test.drop_tables()
        self.db_test.make_initial_tables()
        self.db_test.make_changes()
        #
        self.db_prod.drop_tables()
        self.db_prod.make_initial_tables()
        self.db_prod.compare_and_fit(test_db=self.db_test)
        #
        self.db_test.disconnect()
        self.db_prod.disconnect()
        self.db_test = None
        self.db_prod = None

