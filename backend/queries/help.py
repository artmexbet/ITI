from backend.help.errors import forbidden_error
from flask_login import current_user
from functools import wraps, cmp_to_key
from glob import glob
from jinja2 import Environment, FileSystemLoader
from backend.config import Config
from ..help import FileManager, correct_slash, krsk_time
from ..database import Iti
import re
import os
'''
    LOGIN_REQUIRED_FILES = []       Файлы, доступные после входа на сайт.
    STATUS_REQUIRED_FILES = {}      Отображение файла и доступа к нему.
    all_templates()                 Список всех файлов-шаблонов из папки шаблонов.
    correct_new_line(str)           Заменяет все переносы строк на '\n'.
    split_class(str)                Разбивает класс на букву и цифру.
    empty_checker(*args)            Проверяет аргументы на пустую строку и выбрасывает ValueError.
    path_to_subject(path)           Извлекает id предмета из имени файла.
    parse_files()                   Проходит все файлы, генерирует списки доступа.
    @check_status(status)           Проверяет открыт ли доступ для текущего пользователя.
    @check_block_iti()              Проверяет открыто ли редактирование ИТИ.
    class FilePart                  Один кусочек html-страницы (поля 'text' и 'is_comment').
    class SplitFile                 Связывает html-страницу и программное представление.
        __init__(file_name)                                 Парсит файл 'file_name'.
        insert_after_comment(comment, text, is_comment)     Добавляет 'text' после комментария 'comment'.
        replace_comment(comment, text)                      Заменяет комментарий 'comment' на 'text'.
        writable()                                          Генерирует строку для записи в файл.
        save_file(file_name)                                Сохраняет файл под именем 'file_name'.
'''

LOGIN_REQUIRED_FILES = []
STATUS_REQUIRED_FILES = {}


def all_templates():
    return glob(Config.TEMPLATES_FOLDER + '/**/*.html', recursive=True)


def correct_new_line(s: str):
    return re.sub(r'[\n\r]+', r'\n', s)


def split_class(class_):
    class_ = str(class_)
    if len(class_) == 0:
        return ['', '']
    if len(class_) == 1:
        return int(class_), ''
    return int(class_[:-1]), class_[-1].capitalize()


def empty_checker(*args):
    for x in args:
        if not x or not len(x):
            raise ValueError


def path_to_subject(path: str) -> int:
    return int(path.rsplit('.', 1)[0])


def compare(*args, field=False):
    def cmp(a, b):
        n = len(args)
        if not field:
            for i in range(0, n, 2):
                x, y = args[i](args[i + 1](a)), args[i](args[i + 1](b))
                if x != y:
                    return -1 if x < y else 1
        else:
            for arg in args:
                x, y = arg(a), arg(b)
                if x != y:
                    return -1 if x < y else 1
        return 0
    return cmp_to_key(cmp)


def parse_files():
    if len(LOGIN_REQUIRED_FILES) > 0:
        return
    path = Config.TEMPLATES_FOLDER + "/"
    length = len(path)
    for file_name in all_templates():
        with open(file_name, 'r', encoding='utf-8') as f:
            line1 = f.readline()
            line2 = f.readline()
        if line1 == "<!-- login required -->\n":
            LOGIN_REQUIRED_FILES.append(correct_slash(file_name[length:]))
            begin = line2[0:5]
            end = line2[-5:-1]
            if begin == '<!-- ' and end == ' -->':
                value = int(line2[5:-5])
                if value > 0:
                    STATUS_REQUIRED_FILES[correct_slash(file_name[length:])] = {value, -2, -1}
                elif value == -1:
                    STATUS_REQUIRED_FILES[correct_slash(file_name[length:])] = {-2, -1}
                else:
                    STATUS_REQUIRED_FILES[correct_slash(file_name[length:])] = {-2}
    print("Login required files: " + str(LOGIN_REQUIRED_FILES))
    print("Status: " + str(STATUS_REQUIRED_FILES))


def check_status(status: str):
    def my_decorator(function_to_decorate):

        @wraps(function_to_decorate)
        def wrapped(*args, **kwargs):
            if status == 'admin':
                value = -1
            elif status == 'full':
                value = -2
            else:
                value = int(status)
            if not current_user.can_do(value):
                return forbidden_error()
            return function_to_decorate(*args, **kwargs)

        return wrapped

    return my_decorator


def check_block_iti():
    def my_decorator(function_to_decorate):

        @wraps(function_to_decorate)
        def wrapped(*args, **kwargs):
            if len(kwargs):
                try:
                    iti_id = kwargs['iti_id']
                except Exception:
                    return function_to_decorate(*args, **kwargs)
                iti_info = Iti.select(iti_id)
                if not iti_info or iti_info.block:
                    return forbidden_error()
                kwargs['iti'] = iti_info
                kwargs.pop('iti_id', None)
            return function_to_decorate(*args, **kwargs)

        return wrapped

    return my_decorator


class FilePart:
    def __init__(self, text, is_comment=False):
        self.text = text
        self.is_comment = is_comment


class SplitFile:
    def read_file(self):
        with open(self.file_name, 'r', encoding='UTF-8') as f:
            data = f.read()
        return re.split(r'(<!--|-->)', data)

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.parts = []
        self.replace = {}
        self.edited = False
        is_comment = False
        parts = self.read_file()
        for part in parts:
            if part == '<!--':
                is_comment = True
            elif part == '-->':
                is_comment = False
            else:
                self.parts.append(FilePart(part, is_comment))

    def insert_after_comment(self, comment: str, text: str, is_comment: bool = False, append: bool = False):
        for index in range(len(self.parts)):
            if self.parts[index].is_comment and self.parts[index].text == comment:
                self.edited = True
                if not self.parts[index + 1].is_comment:
                    if not append:
                        self.parts[index + 1] = FilePart(text, is_comment)
                    else:
                        self.parts[index + 1] = FilePart(self.parts[index + 1].text + text, is_comment)
                else:
                    self.parts.insert(index + 1, FilePart(text))

    def replace_comment(self, comment: str, text: str):
        for index in range(len(self.parts)):
            if self.parts[index].is_comment and self.parts[index].text == comment:
                self.edited = True
                self.replace[index] = text

    def writable(self) -> str:
        result = ''
        index = 0
        for part in self.parts:
            if index in self.replace:
                result += self.replace[index]
            else:
                if part.is_comment:
                    result += '<!--'
                result += part.text
                if part.is_comment:
                    result += '-->'
            index += 1
        return result

    def save_file(self, file_name=None):
        if not file_name:
            file_name = self.file_name
        if self.edited:
            if not os.path.exists(os.path.dirname(file_name)):
                os.makedirs(os.path.dirname(file_name))
            with open(file_name, 'w', encoding='UTF-8') as f:
                f.write(self.writable())
            FileManager.save(file_name)
        self.replace = {}


default_replace = [['<!-- replace 1 -->', '{% extends "base.html" %}{% block content %}'],
                   ['<!-- replace 2 -->', '{% endblock %}\n']]


def set_filter(seq):
    return set(seq)


def html_render(template_name: str, output_name: str, template_folder: str = Config.HTML_FOLDER,
                output_folder: str = Config.TEMPLATES_FOLDER, replaced: list = None, **data):
    if replaced is None:
        replaced = []
    env = Environment(loader=FileSystemLoader(template_folder))
    env.filters['set'] = set_filter
    template = env.get_template(template_name)
    data['krsk_moment'] = krsk_time
    data = template.render(**data)
    for rep in default_replace:
        data = data.replace(rep[0], rep[1])
    for rep in replaced:
        data = data.replace(rep[0], rep[1])
    with open(output_folder + '/' + output_name, 'w', encoding='UTF-8') as f:
        f.write(data)
