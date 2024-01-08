**Задача 1  php или python, mysql, ООП**

_Есть боевая и тестовая версия проекта. В ходе разработки в тестовую версию проекта внесены изменения и надо эти изменения перенести на боевую версию._  

_Задача: 
Написать класс для коррекции второй бaзы данных по примеру первой. Первая БД - образец, вторая БД - которую надо скорректировать по первой БД.  Вторая БД уже существует и имеет данные, которые нельзя повредить._

**Дополнение к описанию задачи из переписки:**
>Роман: Задача перенести только данные, структура БД идентична и не меняется?

>Святослав: А разве в можно тестовые данные выкатывать на бой?

>Роман: Однако именно это указано в задании: "_в тестовую версию проекта внесены изменения и надо эти изменения перенести на боевую версию_". Но я спрашивал про структуру БД: появлялись ли, например, новые таблицы которые так же необходимо будет создать и наполнить.

>Святослав: Речь идёт о перенесении структуры базы данных

---
Хочу сделать ремарку. Мой вопрос о переносе данных возник от того, что я не был готов к постановке задачи о ручных миграциях. Некоторое время я сильно переживал, т.к. что угодно что я могу предложить будет сложным, избыточным и ненадежным, по сравнению с обновлением models.py, связанного кода и команд makemigrations + migrate.  Надеюсь, никто не ожидал в качестве тестового задания альтернативу для alembic или migrations. В конце концов, это ведь демонстрационная работа и цели у нее немного иные. 
Я решил не использовать SQLAlchemy для управления БД, сделал все на чистом SQL через mysql-connector. В качестве БД используются реальные MySQL-сервера от clever-cloud.com

Ниже показан текстовый вывод который будет показан в консоли после запуск проекта. Структура БД боевой базы модифицируется до вида тестовой БД, данные не затрагиваются.

---
```
Успешное подключение к серверу MySQL (8.0.22-13): bacj9m2tfvt2e18ya12y
База Данных bacj9m2tfvt2e18ya12y пуста, нет ни одной таблицы..

Успешное подключение к серверу MySQL (8.0.22-13): bwugiti66amancy1cxma
База Данных bwugiti66amancy1cxma пуста, нет ни одной таблицы..

Создаю и наполняю демо-таблицы
В Базе Данных bacj9m2tfvt2e18ya12y существуют следующие таблицы:
    bands
    festivals
    managers
    schedules
    
Создаю и наполняю демо-таблицы
В Базе Данных bwugiti66amancy1cxma существуют следующие таблицы:
    bands
    festivals
    managers
    schedules

В тестовую БД внесены изменения: 
- добавление, удаление, изменение типа столбцов; 
- добавление и удаление таблиц

Начинаем сравнивать и приводить боевую БД к виду тестовой
Тестовая БД состоит из 4 таблиц: ['bands', 'festivals', 'new_table', 'schedules']
Боевая БД состоит из 4 таблиц: ['bands', 'festivals', 'managers', 'schedules']

Добавленных таблиц в тестовую БД: [1]. Создаю их на боевой версии.
    Создана: new_table
Удаленных таблиц в тестовой БД: [1]. Пробую удалить их с боевой.
    Удалил: managers
Общих таблиц в тестовой и боевой БД: [3]. Проверяю столбцы.
    В таблице bands :
       Скопировал столбец country в таблицу bands
       Удалил столбец city таблицы bands
    В таблице festivals :
       Нужно заменить столбец name таблицы festivals
       `name` varchar(32) DEFAULT NULL --> `name` varchar(64) DEFAULT NULL
    В таблице schedules :


Готово! Теперь структура боевой БД приведена к виду тестовой!
Соединение с базой данных bacj9m2tfvt2e18ya12y закрыто
Соединение с базой данных bwugiti66amancy1cxma закрыто
```
