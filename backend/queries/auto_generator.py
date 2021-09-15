from .help import SplitFile, all_templates, tr_format, compare
from ..database import YearsTable, SubjectsTable, YearsSubjectsTable, StudentsTable, ResultsTable, StudentsCodesTable, \
    TeamsTable, TeamsStudentsTable, GroupResultsTable, Result, Student, Team, YearSubject, SubjectsFilesTable,\
    GroupResult
from backend.config import Config
import glob
'''
    class Generator             Заменяет комментарии специального вида на код.
        gen_years_lists()                   Изменяет списки годов.
        gen_subjects_lists()                Изменяет глобальные списки предметов.
        gen_years_subjects_list(year)       Изменяет списки предметов для одного года.
        gen_students_list(class_n)          Изменяет таблицу учеников класса class_n.
        gen_codes(year)                     Генерирует страницу с кодами участников.
        get_net_score(...)                  Генерирует балл в рейтинг.
        get_codes(...)                      Отображает код участника в участника.
        get_student_team(...)               Отображает участника в команду.
        gen_results(year, sub, file)        Генерирует таблицу результатов по предмету sub.
        gen_group_results(year, sub, file)  Генерирует таблицу групповых результатов по предмету sub.
        gen_ratings(year)                   Генерирует рейтинговые таблицы года year.
        gen_teams(year)                     Генерирует списки команд года year.
        gen_teams_students(year)            Генерирует списки участников команд года year.
        gen_timetable(year)                 Генерирует расписание предметов года year.
        gen_files_list(year, sub, path)     Генерирует список предметных файлов.
'''


class Generator:
    @staticmethod
    def gen_years_lists():
        years = YearsTable.select_all()
        type1 = type2 = type3 = type4 = '\n'
        for year in years:
            type1 += '\t' * 7 + '<a class="dropdown-item" href="{0}/main.html">ИТИ-{0}</a>\n'.format(year.year)
            type2 += '\t' * 7 + '<a class="dropdown-item" href="../{0}/main.html">ИТИ-{0}</a>\n'.format(year.year)
            type3 += '\t' * 7 + '<a class="dropdown-item" href="../../{0}/main.html">ИТИ-{0}</a>\n'.format(year.year)
            type4 += '\t' * 7 + '<a class="dropdown-item" href="../../../{0}/main.html">ИТИ-{0}</a>\n'.format(year.year)
        for file_name in all_templates():
            data = SplitFile(file_name)
            data.insert_after_comment(' list of years (1) ', type1 + '\t' * 7)
            data.insert_after_comment(' list of years (2) ', type2 + '\t' * 7)
            data.insert_after_comment(' list of years (3) ', type3 + '\t' * 7)
            data.insert_after_comment(' list of years (4) ', type4 + '\t' * 7)
            data.save_file()

    @staticmethod
    def gen_subjects_lists():
        subjects = SubjectsTable.select_all()
        type1 = type2 = type3 = type4 = type5 = type6 = '\n'
        for subject in subjects:
            text1 = ' ' * 16 + '<p><input type="checkbox" name="status" value="{0}">{1}</p>\n'.format(subject.id, subject.name)
            text2 = ' ' * 12 + '<p>[ {0} ] {1}</p>\n'.format(subject.id, subject.name)
            if subject.type == 'i':
                type1 += text1
                type4 += text2
            elif subject.type == 'g':
                type2 += text1
                type5 += text2
            else:
                type3 += text1
                type6 += text2
        for file_name in all_templates():
            data = SplitFile(file_name)
            data.insert_after_comment(' list of individual tours (1) ', type1 + ' ' * 12)
            data.insert_after_comment(' list of group tours (1) ', type2 + ' ' * 12)
            data.insert_after_comment(' list of another tours (1) ', type3 + ' ' * 12)
            data.insert_after_comment(' list of individual tours (2) ', type4 + ' ' * 8)
            data.insert_after_comment(' list of group tours (2) ', type5 + ' ' * 8)
            data.insert_after_comment(' list of another tours (2) ', type6 + ' ' * 8)
            data.save_file()

    @staticmethod
    def gen_years_subjects_list(year: int):
        years_subjects = YearsSubjectsTable.select_by_year(year)
        years_subjects = set([x.subject for x in years_subjects])
        subjects = SubjectsTable.select_all()
        text1 = text2 = text3 = text4 = text5 = '\n'
        for subject in subjects:
            checked = ''
            if subject.id in years_subjects:
                checked = ' checked'
                if subject.type == 'i':
                    text4 += '<p><a href="individual/{0}.html">{1}</a></p>\n'.format(subject.id, subject.name)
                elif subject.type == 'g':
                    text5 += '<p><a href="group/{0}.html">{1}</a></p>\n'.format(subject.id, subject.name)
            text = '<p><input type="checkbox" name="subject" value="{0}"{1}>[ {0} ] {2}</p>\n'.\
                format(subject.id, checked, subject.name, tabs=7)
            if subject.type == 'i':
                text1 += text
            elif subject.type == 'g':
                text2 += text
            else:
                text3 += text
        for file_name in glob.glob(Config.TEMPLATES_FOLDER + '/' + str(year) + '/**/*.html', recursive=True):
            data = SplitFile(file_name)
            data.insert_after_comment(' list of year_individual tours ', text1 + ' ' * 24)
            data.insert_after_comment(' list of year_group tours ', text2 + ' ' * 24)
            data.insert_after_comment(' list of year_another tours ', text3 + ' ' * 24)
            data.insert_after_comment(' list of year_individual tour (main page) ', text4)
            data.insert_after_comment(' list of year_group tour (main page) ', text5)
            data.save_file()

    @staticmethod
    def gen_students_list_1(student):
        return tr_format(student.name_1, student.name_2, student.class_name())

    @staticmethod
    def gen_students_list(class_n: int):
        file_name = Config.TEMPLATES_FOLDER + '/students_' + str(class_n) + '.html'
        students = StudentsTable.select_by_class_n(class_n)
        length = len(students)
        m1 = length // 3
        m2 = length * 2 // 3
        text1 = text2 = text3 = '\n'
        for i in range(0, m1):
            text1 += Generator.gen_students_list_1(students[i])
        for i in range(m1, m2):
            text2 += Generator.gen_students_list_1(students[i])
        for i in range(m2, length):
            text3 += Generator.gen_students_list_1(students[i])
        data = SplitFile(file_name)
        data.insert_after_comment(' students_table 1 ', text3)
        data.insert_after_comment(' students_table 2 ', text2)
        data.insert_after_comment(' students_table 3 ', text1)
        data.save_file()

    @staticmethod
    def gen_codes_1(student):
        return tr_format(student[1].class_name(), student[1].name_1, student[1].name_2, student[0])

    @staticmethod
    def gen_codes(year: int):
        file_name = Config.TEMPLATES_FOLDER + "/" + str(year) + "/codes.html"
        students = Generator.get_codes(year)
        students = sorted(students.items(), key=compare(lambda x: Student.sort_by_class(x[1]), lambda x: x[1].name_1,
                                                        lambda x: x[1].name_2, field=True))
        length = len(students)
        m1 = length - length * 2 // 3
        m2 = length - length // 3
        text1 = text2 = text3 = '\n'
        for i in range(0, m1):
            text1 += Generator.gen_codes_1(students[i])
        for i in range(m1, m2):
            text2 += Generator.gen_codes_1(students[i])
        for i in range(m2, length):
            text3 += Generator.gen_codes_1(students[i])
        data = SplitFile(file_name)
        data.insert_after_comment(' codes_table 1 ', text1)
        data.insert_after_comment(' codes_table 2 ', text2)
        data.insert_after_comment(' codes_table 3 ', text3)
        data.save_file()

    @staticmethod
    def get_net_score(maximum: int, best_score: int, score: int) -> int:
        if 2 * best_score >= maximum:
            return int(0.5 + score * 100 / best_score)
        return int(0.5 + score * 200 / maximum)

    @staticmethod
    def get_codes(year):
        students = {_.id: _ for _ in StudentsTable.select_all()}
        all_codes = StudentsCodesTable.select_by_year(year)
        codes = {}
        for code in all_codes:
            codes[code.code] = students[code.student]
        return codes

    @staticmethod
    def get_student_team(year):
        teams = TeamsTable.select_by_year(year)
        ans = {}
        for team in teams:
            students = TeamsStudentsTable.select_by_team(team.id)
            for student in students:
                ans[student.student] = student.team
        return ans

    @staticmethod
    def gen_results_1(results: list, codes: map, maximum: int):
        if len(results) == 0:
            return None
        text = '''
        <table width="100%" border="1">
            <tr>
                <td width="10%">Место</td>
                <td width="30%">Фамилия</td>
                <td width="30%">Имя</td>
                <td width="10%">Класс</td>
                <td width="10%">Балл</td>
                <td width="10%">Балл в рейтинг</td>
            </tr>\n'''
        cnt, last_pos, last_result = 1, 0, None
        for result in results:
            if result.result > maximum:
                raise ValueError("Bad results are saved")
            people = codes[result.user]
            result.net_score = Generator.get_net_score(maximum, results[0].result, result.result)
            if last_result != result.result:
                last_pos, last_result = cnt, result.result
            text += tr_format(last_pos, people.name_1, people.name_2, people.class_name(), result.result,
                              result.net_score, color=last_pos, tabs=3)
            ResultsTable.update(result)
            cnt += 1
        text += ' ' * 8 + '</table>'
        return text

    @staticmethod
    def gen_results_protocol(results: list, codes: map, file_name: str, args: map):
        txt = '''
        <table border="1" class="td-1">
            <tr>
                <td width="5%">Место</td>
                <td width="15%">Фамилия</td>
                <td width="15%">Имя</td>
                <td width="10%">Класс</td>'''
        r_split = []
        ln = len(results)
        tasks_cnt = 0
        for result in results:
            r_split.append(result.text_result.split())
            tasks_cnt = max(tasks_cnt, len(r_split[-1]))
        for i in range(tasks_cnt):
            txt += '\n' + ' ' * 16 + '<td width="5%">№ {0}</td>'.format(i + 1)
        txt += '''
                <td width="5%">Балл</td>
                <td width="5%">Балл в рейтинг</td>
            </tr>\n'''
        last_pos, last_result = 0, None
        for i in range(ln):
            people = codes[results[i].user]
            if last_result != results[i].result:
                last_pos, last_result = i + 1, results[i].result
            row = [last_pos, people.name_1, people.name_2, people.class_name()]
            for x in range(tasks_cnt):
                if x < len(r_split[i]):
                    row.append(r_split[i][x])
                else:
                    row.append('—')
            txt += tr_format(*row, results[i].result, results[i].net_score, color=last_pos, tabs=3)
        txt += ' ' * 8 + '</table>\n' + ' ' * 4
        data = SplitFile(Config.HTML_FOLDER + "/protocol.html")
        data.insert_after_comment(' results table ', txt)
        for arg in args:
            data.replace_comment(arg, args[arg])
        data.save_file(file_name)

    @staticmethod
    def gen_results_2(results: list, codes: map, class_n: int, maximum: int, file_name: str, args: map):
        txt = Generator.gen_results_1(results, codes, maximum)
        if txt:
            txt = '''    <div class="col t-3">
        <center>
            <h3>{0} класс</h3>
            <p>(Максимум: {1} баллов)</p>
        </center>{2}
    </div>\n'''.format(class_n, maximum, txt)
            args[' {class} '] = str(class_n)
            Generator.gen_results_protocol(results, codes, file_name, args)
        return txt

    @staticmethod
    def gen_results(year: int, subject: int, file_name: str):
        results = ResultsTable.select_by_year_and_subject(year, subject)
        year_subject = YearsSubjectsTable.select(year, subject)
        codes = Generator.get_codes(year)
        sorted_results = [[] for _ in range(5)]
        for r in results:
            sorted_results[codes[r.user].class_n - 5].append(r)
        for lst in sorted_results:
            lst.sort(key=compare(lambda x: Result.sort_by_result(x), lambda x: codes[x.user].class_l,
                                 lambda x: codes[x.user].name_1, lambda x: codes[x.user].name_2, field=True))
        pth = Config.TEMPLATES_FOLDER + '/' + str(year) + '/individual/' + str(subject) + '/protocol'
        params = {' {year} ': str(year), ' {subject_id} ': str(subject),
                  ' {subject} ': SubjectsTable.select_by_id(subject).name}
        txt5 = Generator.gen_results_2(sorted_results[0], codes, 5, year_subject.score_5, pth + '_5.html', params)
        txt6 = Generator.gen_results_2(sorted_results[1], codes, 6, year_subject.score_6, pth + '_6.html', params)
        txt7 = Generator.gen_results_2(sorted_results[2], codes, 7, year_subject.score_7, pth + '_7.html', params)
        txt8 = Generator.gen_results_2(sorted_results[3], codes, 8, year_subject.score_8, pth + '_8.html', params)
        txt9 = Generator.gen_results_2(sorted_results[4], codes, 9, year_subject.score_9, pth + '_9.html', params)
        txt = '\n<center><h2>Результаты</h2></center>\n<div class="row col-12 justify-content-center">\n'
        protocols = '<center><h2>Протоколы</h2></center>\n'
        prot_start = '<p><a href="{0}/protocol_'.format(subject)
        protocols += prot_start + '5.html">5 класс</a></p>\n' if txt5 else ''
        protocols += prot_start + '6.html">6 класс</a></p>\n' if txt6 else ''
        protocols += prot_start + '7.html">7 класс</a></p>\n' if txt7 else ''
        protocols += prot_start + '8.html">8 класс</a></p>\n' if txt8 else ''
        protocols += prot_start + '9.html">9 класс</a></p>\n' if txt9 else ''
        txt += txt5 if txt5 else ''
        txt += txt6 if txt6 else ''
        txt += txt7 if txt7 else ''
        txt += txt8 if txt8 else ''
        txt += txt9 if txt9 else ''
        txt += '</div>\n' + protocols
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + file_name)
        data.insert_after_comment(' results table ', txt)
        data.save_file()

    @staticmethod
    def gen_group_results(year: int, subject: int, file_name: str):
        teams = TeamsTable.select_by_year(year)
        if len(teams) == 0:
            return None
        results = {_: GroupResultsTable.select_by_team_and_subject(_.id, subject) for _ in teams}
        results = sorted(results.items(), key=compare(Result.sort_by_result, lambda x: x[1],
                                                      Team.sort_by_later, lambda x: x[0]))
        txt = '''
    <center>
        <h2>Результаты</h2>
        <div class="row col-12 justify-content-center">
            <div class="col t-3">
                <table border="1">
                    <tr>
                        <td width="10%">Место</td>
                        <td width="30%">Команда</td>
                        <td width="10%">Балл в рейтинг</td>
                    </tr>\n'''
        i, last_pos, last_result = 1, 1, None
        for result in results:
            if result[1].result != last_result:
                last_pos, last_result = i, result[1].result
            txt += tr_format(last_pos, result[0].name, result[1].result, color=last_pos, tabs=5)
            i += 1
        txt += ' ' * 16 + '</table>\n' + ' ' * 12 + '</div>\n' + ' ' * 8 + '</div>\n' + ' ' * 4 + '</center>\n'
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + file_name)
        data.insert_after_comment(' results table ', txt)
        data.save_file()

    @staticmethod
    def gen_ratings_1(results: list, index: int, start: int):
        txt = '\n'
        last_pos, last_result = 0, None
        for i in range(min(20, len(results) - index)):
            s = results[index + i][1]
            if s.class_n != start:
                break
            if last_result != s.result:
                last_result, last_pos = s.result, i
            txt += tr_format(last_pos + 1, s.class_name(), s.name_1, s.name_2, s.result, color=last_pos + 1)
        while index < len(results) and results[index][1].class_n == start:
            index += 1
        return txt, index

    @staticmethod
    def gen_ratings_2(results: list):
        txt = '\n'
        i, last_pos, last_result = 0, 0, None
        for x in results:
            if x[1] != last_result:
                last_pos, last_result = i, x[1]
            txt += tr_format(last_pos + 1, x[0], x[1], color=last_pos + 1)
            i += 1
            if i == 20:
                break
        return txt

    @staticmethod
    def gen_ratings_3(year: int, results: map):
        subjects = []
        team = None
        new_results = []
        txt = '''
    <table width="90%" border="1">
        <tr>
            <td width="5%">Место</td>
            <td width="15%">Команда</td>
            <td width="8%">День 1 + День 2</td>\n'''
        for x in YearsSubjectsTable.select_by_year(year):
            subject = SubjectsTable.select_by_id(x.subject)
            if subject.type == 'g':
                subjects.append(subject)
                txt += ' ' * 12 + '<td width="8%">{0}</td>\n'.format(subject.name)
            elif subject.type == 'a':
                team = subject
        if team:
            subjects.append(team)
            txt += ' ' * 12 + '<td width="8%">Командный</td>\n'
        txt += ' ' * 12 + '<td width="8%">Сумма</td>\n' + ' ' * 8 + '</tr>\n'
        subject_ids = [_.id for _ in subjects]
        cols_result = [[] for i in range(len(subject_ids) + 2)]
        for x in results:
            summ = results[x]
            team_info = TeamsTable.select_by_id(x)
            row = [team_info.name, results[x]]
            cols_result[0].append(results[x])
            res = GroupResultsTable.select_by_team(team_info.id)
            res = {_.subject: _.result for _ in res} if res else {}
            pos = 1
            for subject in subject_ids:
                r = res[subject] if subject in res else 0
                row.append(r)
                summ += r
                cols_result[pos].append(r)
                pos += 1
            row.append(summ)
            new_results.append([row, summ])
            cols_result[-1].append(summ)
        new_results.sort(key=compare(lambda x: -x[1], lambda x: x[0][0], field=True))
        cols_result = [sorted(_, reverse=True) for _ in cols_result]
        i, last_pos, last_result = 1, 1, None
        for x in new_results:
            if x[1] != last_result:
                last_pos, last_result = i, x[1]
            colors = [4, 4]
            colors.extend([cols_result[i-1].index(x[0][i]) + 1 for i in range(1, len(x[0]))])
            txt += tr_format(last_pos, *x[0], tabs=2, color=colors)
            i += 1
        return txt + ' ' * 4 + '</table>\n'

    @staticmethod
    def gen_ratings_4(codes: map, class_n: int, filename: str, year: int, results: list):
        class_results = {}
        for x in codes:
            student = x[1]
            if student.class_n == class_n:
                if student.class_l in class_results:
                    class_results[student.class_l].append(student)
                else:
                    class_results[student.class_l] = [student]
        subjects, txt = [], ''
        template = '''
        <div class="col t-2">
            <center><h3>{0}</h3></center>
            <table width="100%" border="1">
                <tr>
                    <td width="10%">Место</td>
                    <td width="40%">Фамилия</td>
                    <td width="40%">Имя</td>\n'''
        for x in YearsSubjectsTable.select_by_year(year):
            subject = SubjectsTable.select_by_id(x.subject)
            if subject.type == 'i':
                subjects.append(subject)
                template += ' ' * 20 + '<td width="5%">{}</td>\n'.format(subject.name)
        template += ' ' * 20 + '<td width="10%">Сумма</td>\n' + ' ' * 16 + '</tr>\n'
        for r in class_results:
            txt += template.format(str(class_n) + r)
            position, last_pos, last_result = 1, 1, None
            for x in class_results[r]:
                if x.result != last_result:
                    last_pos, last_result = position, x.result
                row = [last_pos, x.name_1, x.name_2]
                for subject in subjects:
                    if x.id in results and subject.id in results[x.id]:
                        row.append(results[x.id][subject.id])
                    else:
                        row.append('—')
                txt += tr_format(*row, x.result, color=last_pos, tabs=4)
                position += 1
            txt += ' ' * 12 + '</table>\n' + ' ' * 8 + '</div>'
        txt += '\n    '
        data = SplitFile(filename)
        data.insert_after_comment(' results ', txt)
        data.save_file()

    @staticmethod
    def gen_ratings(year: int):
        results = ResultsTable.select_by_year(year)
        codes = Generator.get_codes(year)
        student_team = Generator.get_student_team(year)
        class_results, student_result, all_student_result = {}, {}, {}
        team_result = {_.id: 0 for _ in TeamsTable.select_by_year(year)}
        for r in results:
            student = codes[r.user]
            class_name = student.class_name()
            if class_name not in class_results:
                class_results[class_name] = 0
            class_results[class_name] += r.net_score
            if r.user not in student_result:
                student_result[r.user] = []
            student_result[r.user].append(r.net_score)
            if student.id not in all_student_result:
                all_student_result[student.id] = {}
            all_student_result[student.id][r.subject] = r.net_score
            if student.id in student_team:
                team_result[student_team[student.id]] += r.net_score
        for r in student_result:
            student_result[r].sort(reverse=True)
            cnt = 0
            for i in range(min(4, len(student_result[r]))):
                cnt += student_result[r][i]
            codes[r].result = cnt
        codes = sorted(codes.items(), key=compare(lambda x: -x[1].class_n, lambda x: -x[1].result,
                        lambda x: x[1].class_l, lambda x: x[1].name_1, lambda x: x[1].name_2, field=True))
        class_results = sorted(class_results.items(), key=compare(lambda x: -x[1], lambda x: x[0], field=True))
        index = 0
        best_9, index = Generator.gen_ratings_1(codes, index, 9)
        best_8, index = Generator.gen_ratings_1(codes, index, 8)
        best_7, index = Generator.gen_ratings_1(codes, index, 7)
        best_6, index = Generator.gen_ratings_1(codes, index, 6)
        best_5, index = Generator.gen_ratings_1(codes, index, 5)
        best_class = Generator.gen_ratings_2(class_results)
        best_team = Generator.gen_ratings_3(year, team_result)
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + str(year) + '/rating.html')
        data.insert_after_comment(' rating_teams ', best_team)
        data.insert_after_comment(' rating_class ', best_class)
        data.insert_after_comment(' rating_parallel_5 ', best_5)
        data.insert_after_comment(' rating_parallel_6 ', best_6)
        data.insert_after_comment(' rating_parallel_7 ', best_7)
        data.insert_after_comment(' rating_parallel_8 ', best_8)
        data.insert_after_comment(' rating_parallel_9 ', best_9)
        data.save_file()
        for i in range(5, 10):
            filename = Config.TEMPLATES_FOLDER + "/" + str(year) + '/rating_' + str(i) + '.html'
            Generator.gen_ratings_4(codes, i, filename, year, all_student_result)
        # лучшие результаты в первый / второй дни :(

    @staticmethod
    def gen_teams(year: int):
        teams = TeamsTable.select_by_year(year)
        text1, text2, text3 = '\n', '\n', '\n'
        for team in teams:
            row = [team.later, team.name]
            text1 += tr_format(team.id, *row, tabs=4)
            text2 += tr_format(*row, tabs=3)
            text3 += ' ' * 16 + '<p>{0}: <input type="text" name="score_{1}" value="{{{{ t{1} }}}}"></p>\n'.\
                format(team.name, team.id)
        text1 += ' ' * 16
        text2 += ' ' * 8
        text3 += ' ' * 12
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + str(year) + "/subjects_for_year.html")
        data.insert_after_comment(' list of teams (full) ', text1)
        data.save_file()
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + str(year) + "/teams.html")
        data.insert_after_comment(' list of teams ', text2)
        data.save_file()
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + str(year) + "/add_result.html")
        data.insert_after_comment(' teams list for saving group results ', text3)
        data.save_file()

    @staticmethod
    def gen_teams_students(year: int):
        codes = {_.id: _ for _ in StudentsTable.select_all()}
        teams = TeamsTable.select_by_year(year)
        teams.sort(key=Team.sort_by_later)
        txt = ''
        for team in teams:
            students = TeamsStudentsTable.select_by_team(team.id)
            students = [codes[_.student] for _ in students]
            students.sort(key=compare(lambda x: x.class_name(), lambda x: x.name_1, lambda x: x.name_2, field=True))
            if len(students) == 0:
                continue
            txt += '''
        <div class="t-3"><center><h2>{0}</h2></center>
            <table width="100%" border="1">
                <tr>
                    <td width="10%">Класс</td>
                    <td width="45%">Фамилия</td>
                    <td width="45%">Имя</td>
                </tr>\n'''.format(team.name)
            for student in students:
                txt += tr_format(student.class_name(), student.name_1, student.name_2, tabs=4)
            txt += ' ' * 12 + '</table>\n' + ' ' * 8 + '</div>\n'
        txt += ' ' * 4
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + str(year) + "/teams.html")
        data.insert_after_comment(' list of students_in_team ', txt)
        data.save_file()

    @staticmethod
    def gen_timetable(year: int):
        subjects = [_ for _ in YearsSubjectsTable.select_by_year(year) if _.start or _.end or _.place]
        subjects.sort(key=YearSubject.sort_by_start)
        txt = '\n'
        for subject in subjects:
            txt += tr_format(subject.date_str(), SubjectsTable.select_by_id(subject.subject).name, subject.classes,
                             subject.start_str(), subject.end_str(), subject.place, tabs=3)
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + str(year) + "/timetable.html")
        data.insert_after_comment(' timetable ', txt + ' ' * 8)
        data.save_file()

    @staticmethod
    def gen_files_list(year: int, subject: int, path: str):
        data = SplitFile(Config.TEMPLATES_FOLDER + '/' + str(year) + '/' + path)
        files = SubjectsFilesTable.select_by_subject(year, subject)
        txt = '\n    <center><h2>Файлы</h2></center>\n' if len(files) != 0 else '\n'
        for file in files:
            txt += '    <p><a href="/' + file.file + '">' + file.just_filename() + '</a></p>\n'
        data.insert_after_comment(' files ', txt)
        data.save_file()
