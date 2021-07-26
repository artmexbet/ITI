Это код сайта для провидения ИТИ в гимназии «Универс».  

## Введение
Данный сайт создан после ИТИ 2020, вызвавших у меня большие вопросы, описанные [в документе](https://docs.google.com/document/d/1EVA8DLRzNT_RM08moMkHQI5ec5AY2vNwJUmSYoydi4M/edit?usp=sharing).  
Сайт разрабатывается при поддержке организаторов ИТИ 2020 (Савокина Е.В. и Проходский А.Н.), а также
учителя информатики Инженерной школы (Вахитова Е.Ю.).

## Поддерживаемый функционал
| Функция | Необходимая роль | Место реализации | Дата |
| ------- | ----- | ----- | ---- |
| Вход (выход) на сайт | — | users.py | 23.04.21 |
| Изменение настроек | Любая | users.py | 23.04.21 |
| Регистрация, редактирование и удаление новых пользователей | admin | users.py | 23.04.21 |
| Регистрация, редактирование и удаление участников ИТИ | Любая | students.py | 27.04.21 |
| &nbsp; | | | |
| Загрузка файлов | admin | files_edit.py | 23.04.21 |
| Редактирование годовых файлов | admin | files_edit.py | 25.04.21 |
| Редактирование глобальных файлов | full | files_edit.py | 25.04.21 |
| &nbsp; | | | |
| Работа с новыми ИТИ и предметами | full | full.py, auto_generator.py, file_creator.py | 25.04.21 |
| Связь ИТИ и предметов, генерация страниц | admin | full.py, auto_generator.py, file_creator.py | 25.04.21 |
| Генерация кодов для участников, таблица со всеми кодами | admin | students.py, auto_generator.py | 05.07.21 |
| Добавление и удаление команд | admin | teams.py  | 26.07.21 |
| Добавление и удаление участников команд | admin | teams.py | 26.07.21 |
| &nbsp; | | | |
| Настройка предмета | Предметник | results.py | 19.07.21 |
| Сохранение результатов | Предметник | results.py | 05.07.21 |
| Публикация результатов | admin | results.py, auto_generator.py | 19.07.21 |
| Публикация рейтинга | admin | results.py, auto_generator.py | 21.07.21 |
