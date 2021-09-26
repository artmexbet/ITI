from backend import app
from flask import render_template, request, send_file
from flask_cors import cross_origin
from flask_login import login_required
import shutil
import glob
import os
from .help import check_status, check_block_year, SplitFile
from ..help import init_mail_messages, ExcelReader, ExcelWriter, FileManager
from ..database import DataBase, SubjectsTable, Subject, YearsTable, Year, YearsSubjectsTable, TeamsTable,\
    TeamsStudentsTable, AppealsTable, GroupResultsTable, ResultsTable, StudentsCodesTable, SubjectsFilesTable,\
    SubjectsStudentsTable, HistoriesTable
from .auto_generator import Generator
from .file_creator import FileCreator
from ..config import Config
'''
    Функции ниже доступны только full, если не указано иного.
    _delete_year()                                  Функция для удаления года ИТИ.
    /add_year               add_year()              Создаёт новый год ИТИ.
    /delete_year            delete_year()           Удаляет год ИТИ.
    /add_subject            add_subject()           Создаёт новый предмет.
    /edit_subject           edit_subject()          Редактирует предмет.
    /delete_subject         delete_subject()        Удаляет предмет.
    /global_settings        global_settings()       Сохраняет глобальные настройки (пароль от почты).
    /db                     db()                    Делает SQL запросы к базе данных.
    /<year>/year_block      year_block()            Блокирует последующее редактирование года для всех.
    /load_data_from_excel   load_data_from_excel()  Загружает данные из Excel таблицы.
    /<year>/download_excel  download_excel()        Выгружает данные в Excel.
'''


def _delete_year(year: int):
    AppealsTable.delete_by_year(year)
    HistoriesTable.delete_by_year(year)
    ResultsTable.delete_by_year(year)
    StudentsCodesTable.delete_by_year(year)
    SubjectsFilesTable.delete_by_year(year)
    SubjectsStudentsTable.delete_by_year(year)
    YearsTable.delete(year)
    YearsSubjectsTable.delete_by_year(year)

    teams = TeamsTable.select_by_year(year)
    for team in teams:
        GroupResultsTable.delete_by_team(team.id)
        TeamsStudentsTable.delete_by_team(team.id)
    TeamsTable.delete_by_year(year)

    Generator.gen_years_lists()
    dir1, dir2 = Config.UPLOAD_FOLDER + '/' + str(year), Config.TEMPLATES_FOLDER + '/' + str(year)
    dir3, dir4 = Config.DATA_FOLDER + '/sheet_' + str(year), Config.DATA_FOLDER + '/data_' + str(year)
    for file in glob.glob(dir3 + '.*'):
        FileManager.delete(file)
        os.remove(file)
    for file in glob.glob(dir4 + '.*'):
        FileManager.delete(file)
        os.remove(file)
    FileManager.delete_dir(dir1)
    FileManager.delete_dir(dir2)
    try:
        shutil.rmtree(dir1)
    except FileNotFoundError:
        pass
    try:
        shutil.rmtree(dir2)
    except FileNotFoundError:
        pass


@app.route("/add_year", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def add_year():
    try:
        name = int(request.form['name'])
    except ValueError:
        return render_template('subjects_and_years.html', error1='Некорректный год')

    year = YearsTable.select_by_year(name)
    if not year.__is_none__:
        return render_template('subjects_and_years.html', error1='Год уже существует')
    year = Year([name, '', 0])
    YearsTable.insert(year)
    FileCreator.create_year(name)
    Generator.gen_years_lists()
    Generator.gen_years_subjects_list(name)
    return render_template('subjects_and_years.html', error1='Год добавлен')


@app.route("/delete_year", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def delete_year():
    try:
        year = int(request.form['year'])
    except ValueError:
        return render_template('subjects_and_years.html', error6='Некорректный год')
    _delete_year(year)
    return render_template('subjects_and_years.html', error6='Год удалён')


@app.route("/add_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def add_subject():
    try:
        name = request.form['name']
        subject_type = request.form['type']
    except Exception:
        return render_template('subjects_and_years.html', error2='Некорректные данные')

    subject = SubjectsTable.select_by_name(name)
    if not subject.__is_none__:
        return render_template('subjects_and_years.html', error2='Предмет уже существует')
    subject = Subject([None, name, subject_type])
    SubjectsTable.insert(subject)
    Generator.gen_subjects_lists()
    return render_template('subjects_and_years.html', error2='Предмет добавлен')


@app.route("/edit_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def edit_subject():
    try:
        id = int(request.form['id'])
        new_name = request.form['new_name']
        subject_type = request.form['new_type']
    except Exception:
        return render_template('subjects_and_years.html',  error3='Некорректные данные')

    subject = SubjectsTable.select_by_id(id)
    if subject.__is_none__:
        return render_template('subjects_and_years.html',  error3='Предмета не существует')
    subject.name = new_name
    subject.type = subject_type
    SubjectsTable.update_by_id(subject)
    Generator.gen_subjects_lists()
    return render_template('subjects_and_years.html', error3='Предмет обнавлён')


@app.route("/delete_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def delete_subject():
    try:
        id = int(request.form['id'])
    except ValueError:
        return render_template('subjects_and_years.html',  error4='Некорректный id')

    subject = SubjectsTable.select_by_id(id)
    if subject.__is_none__:
        return render_template('subjects_and_years.html', error4='Предмета не существует')
    SubjectsTable.delete(subject)
    Generator.gen_subjects_lists()
    return render_template('subjects_and_years.html', error4='Предмет удалён')


@app.route("/global_settings", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def global_settings():
    app.config['MAIL_PASSWORD'] = request.form['password']
    init_mail_messages()
    return render_template('settings.html', error2='Успех', email=app.config['MAIL_USERNAME'],
                           admins=str(app.config['ADMINS']), password='Уже введён')


@app.route('/db')
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def db():
    sql = request.args.get('sql')
    t = request.args.get('type')
    if t and t != '':
        return str(DataBase.execute(sql))
    DataBase.just_execute(sql)
    return 'OK'


@app.route('/<int:year>/year_block', methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
def year_block(year: int):
    try:
        is_block = int(request.form['is_block'])
    except ValueError:
        return render_template(str(year.year) + '/subjects_for_year.html', error8='Некорректный ввод', year=year.year)

    year = YearsTable.select_by_year(year)
    if year.__is_none__:
        return render_template(str(year.year) + '/subjects_for_year.html', error8='Этого года нет.', year=year.year)
    year.block = is_block
    YearsTable.update(year)
    data = SplitFile(Config.TEMPLATES_FOLDER + '/' + str(year.year) + '/subjects_for_year.html')
    data.insert_after_comment(' is_block ', '''
                <p><input type="radio" name="is_block" value="0" {0}>Разблокировано</p>
                <p><input type="radio" name="is_block" value="1" {1}>Заблокировано</p>
            '''.format('checked' if is_block == 0 else '', 'checked' if is_block == 1 else ''))
    data.save_file()
    return render_template(str(year.year) + '/subjects_for_year.html', error8='Сохранено.', year=year.year)


@app.route('/load_data_from_excel', methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def load_data_from_excel():
    try:
        year = int(request.form['year'])
        file = request.files['file']
        parts = [x.lower() for x in file.filename.rsplit('.', 1)]
        if len(parts) < 2:
            raise ValueError
        filename = Config.DATA_FOLDER + '/sheet_' + str(year) + '.' + parts[1]
    except Exception:
        return render_template('subjects_and_years.html',  error5='Некорректные данные')

    _delete_year(year)
    YearsTable.insert(Year([year, '', 1]))
    FileCreator.create_year(year)
    Generator.gen_years_lists()
    Generator.gen_years_subjects_list(year)

    file.save(filename)
    FileManager.save(filename)
    ExcelReader(filename, year).read()

    return render_template('subjects_and_years.html',  error5='Сохранено')


@app.route('/<int:year>/download_excel', methods=['GET'])
@cross_origin()
@login_required
@check_status('admin')
def download_excel(year: int):
    ExcelWriter(year).write(Config.DATA_FOLDER + '/data_{}.xlsx'.format(year))
    filename = './data/data_{}.xlsx'.format(year)
    return send_file(filename, as_attachment=True, attachment_filename='Данныe ИТИ {}.xlsx'.format(year))
