from backend import app
from ..database import TeamsTable, Team, StudentsTable, Student, TeamsStudentsTable, TeamStudent, User,\
    YearsSubjectsTable, SubjectsTable, SubjectsStudentsTable, SubjectStudent, UsersTable
from .help import check_status, check_block_year, split_class, empty_checker
from .auto_generator import Generator
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required, current_user
'''
    teams_page_params(user, year)                               Параметры для страницы 'teams_for_year.html'
    /<year>/add_team                add_team()                  Добавляет команду.
    /<year>/delete_team             delete_team()               Удаляет команду.
    /<year>/add_student_team        add_student_team()          Добавляет участника в команду.
    /<year>/delete_student_team     delete_student_team()       Удаляет участника из команды.
    /<year>/student_subject         student_subject()           Добавляет командного участника на групповой тур.
    /<year>/team_edit               team_edit()                 redirect с параметрами на страницу редактирования.
    /<year>/add_user_team           add_user_team()             Добавляет руководителя команды.
    /<year>/delete_user_team        delete_user_team()          Удаляет руководителя команды.
'''


def teams_page_params(user: User, year: int):
    try:
        teams, res, subjects = user.teams_list(year), [], []
        for x in YearsSubjectsTable.select_by_year(year):
            subject = SubjectsTable.select_by_id(x.subject)
            if subject.type == 'g':
                subjects.append(subject)
        for now in teams:
            team, t = TeamsTable.select_by_id(now), []
            peoples = TeamsStudentsTable.select_by_team(team.id)
            for x in peoples:
                people = StudentsTable.select(x.student)
                subjects_for_people = set([_.subject for _ in SubjectsStudentsTable.select_by_student(year, people.id)])
                p = [[None, people.class_name()], [None, people.name_1], [None, people.name_2]]
                for subject in subjects:
                    p.append([subject.id, people.id, subject.id in subjects_for_people])
                t.append(p)
            res.append([team.name, t])
        return {'teams': res, 'subjects': [_.name for _ in subjects]}
    except Exception:
        return {}


@app.route("/<int:year>/add_team", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def add_team(year: int):
    args = teams_page_params(current_user, year)
    try:
        name = request.form['name']
        later = request.form['later'].capitalize()
        empty_checker(name, later)
    except Exception:
        return render_template(str(year) + '/teams_for_year.html', **args, error1='Некорректные данные')

    if not TeamsTable.select_by_year_and_later(year, later).__is_none__:
        return render_template(str(year) + '/teams_for_year.html', **args, error1='Команда от этой вертикали уже есть')
    TeamsTable.insert(Team([None, name, year, later]))
    Generator.gen_teams(year)
    return render_template(str(year) + '/teams_for_year.html', **args, error1='Команда добавлена')


@app.route("/<int:year>/delete_team", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def delete_team(year: int):
    try:
        id = int(request.form['id'])
    except Exception:
        return render_template(str(year) + '/teams_for_year.html', **teams_page_params(current_user, year),
                               error2='Некорректные данные')

    TeamsTable.delete(Team([id, '', year, '']))
    Generator.gen_teams(year)
    return render_template(str(year) + '/teams_for_year.html', **teams_page_params(current_user, year),
                           error2='Команда удалена')


@app.route("/<int:year>/add_student_team", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def add_student_team(year: int):
    args = teams_page_params(current_user, year)
    try:
        team = int(request.form['team'])
        name1 = request.form['name1'].capitalize()
        name2 = request.form['name2'].capitalize()
        class_ = split_class(request.form['class'])
        class_[1].capitalize()
        empty_checker(name1, name2)
    except Exception:
        return render_template(str(year) + '/teams_for_year.html', **args, error3='Некорректные данные')

    if TeamsTable.select_by_id(team).__is_none__:
        return render_template(str(year) + '/teams_for_year.html', **args, error3='Такой команды нет')
    student = StudentsTable.select_by_student(Student([None, name1, name2, class_[0], class_[1]]))
    if student.__is_none__:
        return render_template(str(year) + '/teams_for_year.html', **args, error3='Такого участника нет')
    team_student = TeamStudent([team, student.id])
    if not TeamsStudentsTable.select(team_student).__is_none__:
        return render_template(str(year) + '/teams_for_year.html', **args, error3='Этот участник уже в этой команде')
    TeamsStudentsTable.insert(team_student)
    Generator.gen_teams_students(year)
    return render_template(str(year) + '/teams_for_year.html', **teams_page_params(current_user, year),
                           error3='Участник добавлен')


@app.route("/<int:year>/delete_student_team", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def delete_student_team(year: int):
    args = teams_page_params(current_user, year)
    try:
        team = int(request.form['team'])
        name1 = request.form['name1'].capitalize()
        name2 = request.form['name2'].capitalize()
        class_ = split_class(request.form['class'])
        class_[1].capitalize()
        empty_checker(name1, name2)
    except Exception:
        return render_template(str(year) + '/teams_for_year.html', **args, error4='Некорректные данные')

    if TeamsTable.select_by_id(team).__is_none__:
        return render_template(str(year) + '/teams_for_year.html', **args, error4='Такой команды нет')
    student = StudentsTable.select_by_student(Student([None, name1, name2, class_[0], class_[1]]))
    if student.__is_none__:
        return render_template(str(year) + '/teams_for_year.html', **args, error4='Такого участника нет')
    team_student = TeamStudent([team, student.id])
    if TeamsStudentsTable.select(team_student).__is_none__:
        return render_template(str(year) + '/teams_for_year.html', **args, error4='Этого человека нет в этой команде')
    TeamsStudentsTable.delete(team_student)
    Generator.gen_teams_students(year)
    return render_template(str(year) + '/teams_for_year.html', **teams_page_params(current_user, year),
                           error4='Участник удалён')


@app.route("/<int:year>/student_subject", methods=['POST'])
@cross_origin()
@login_required
@check_block_year()
def student_subject(year: int):
    subjects = set(request.form.getlist('subject'))
    old_subjects = set(request.form.getlist('old_subject'))
    different = subjects.symmetric_difference(old_subjects)
    for x in different:
        t = x.split('_')
        t = SubjectStudent([year, int(t[0]), int(t[1])])
        if x in subjects:
            SubjectsStudentsTable.insert(t)
        else:
            SubjectsStudentsTable.delete(t)
    return render_template(str(year) + '/teams_for_year.html', **teams_page_params(current_user, year),
                           error5='Сохранено')


@app.route("/<int:year>/team_edit")
@cross_origin()
@login_required
@check_block_year()
def team_edit(year: int):
    return render_template(str(year) + '/teams_for_year.html', **teams_page_params(current_user, year))


@app.route("/<int:year>/add_user_team", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def add_user_team(year: int):
    args = teams_page_params(current_user, year)
    try:
        login = request.form['login']
        team = int(request.form['team'])
        empty_checker(login)
    except Exception:
        return render_template(str(year) + '/teams_for_year.html', **args, error6='Некорректные данные')

    user = UsersTable.select_by_login(login)
    if user.__is_none__:
        return render_template(str(year) + '/teams_for_year.html', **args, error6='Несуществующий логин')
    if user.is_exists_team(team):
        return render_template(str(year) + '/teams_for_year.html', **args, error6='Пользователь уже руководит этой'
                                                                                  'командой')
    user.add_team(team)
    UsersTable.update_by_login(user)
    return render_template(str(year) + '/teams_for_year.html', **args, error6='Руководитель добавлен')


@app.route("/<int:year>/delete_user_team", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def delete_user_team(year: int):
    args = teams_page_params(current_user, year)
    try:
        login = request.form['login']
        team = int(request.form['team'])
        empty_checker(login)
    except Exception:
        return render_template(str(year) + '/teams_for_year.html', **args, error7='Некорректные данные')

    user = UsersTable.select_by_login(login)
    if user.__is_none__:
        return render_template(str(year) + '/teams_for_year.html', **args, error7='Несуществующий логин')
    if not user.is_exists_team(team):
        return render_template(str(year) + '/teams_for_year.html', **args, error7='Пользователь не руководит этой '
                                                                                  'командой')
    user.delete_team(team)
    UsersTable.update_by_login(user)
    return render_template(str(year) + '/teams_for_year.html', **args, error7='Руководитель удалён')
