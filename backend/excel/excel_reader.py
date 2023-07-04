import pandas as pd
from backend.queries.file_creator import FileCreator, SplitFile
from backend.queries.auto_generator import Generator
from backend.queries.help import split_class
from ..database import Result, Student, StudentClass, StudentCode, Subject, Team, TeamStudent, Year, YearSubject,\
    get_student_by_params
from backend.config import Config


def find(titles, exists, not_exists=None):
    i = 0
    for x in titles:
        t = x.lower()
        if exists in t and (not not_exists or not_exists not in t):
            return i
        i += 1
    return -1


class ExcelFullReader:
    RES = ['subject', 'code', 'result']
    CODES = ['name', 'cls', 'gender', 'code', 'team']
    STUDENTS = ['name', 'cls', 'gender']

    def __init__(self, file: str, year: Year, qtype: int):
        self.file = file
        self.year = year
        self.qtype = qtype

    def __frames__(self):
        sheet_name = list(self.sheet.keys())
        self.sheet = list(self.sheet.values())
        ans, codes = find(sheet_name, 'ответы'), find(sheet_name, 'код')
        self.result, self.code = self.sheet[ans], self.sheet[codes]

    def __get_result_cols__(self):
        columns = self.result.columns
        sub, code = find(columns, 'предмет'), find(columns, 'номер')
        result = find(columns, 'балл', 'чист')
        frame = pd.DataFrame(self.result, columns=[columns[sub], columns[code], columns[result]])
        frame.columns = self.RES
        self.result = frame[frame[self.RES[0]].notna() & frame[self.RES[1]].notna() & frame[self.RES[2]].notna()]

    def __get_codes_cols__(self):
        columns = self.code.columns
        name, cls = columns[find(columns, 'имя')], columns[find(columns, 'класс')]
        code, team = columns[find(columns, 'код')], columns[find(columns, 'команда')]
        gender = columns[find(columns, 'пол')]
        frame = pd.DataFrame(self.code, columns=[name, cls, gender, code, team])
        frame.columns = self.CODES
        self.code = frame[frame[self.CODES[0]].notna() & frame[self.CODES[1]].notna() & frame[self.CODES[2]].notna()
                          & frame[self.CODES[3]].notna()]

    def __get_students_cols__(self):
        columns = self.code.columns
        name, cls = columns[find(columns, 'имя')], columns[find(columns, 'класс')]
        gender = columns[find(columns, 'пол')]
        frame = pd.DataFrame(self.code, columns=[name, cls, gender])
        frame.columns = self.STUDENTS
        self.student = frame[frame[self.STUDENTS[0]].notna() & frame[self.STUDENTS[1]].notna() & frame[self.STUDENTS[2]].notna()]

    def __gen_subject__(self):
        subjects = self.result[self.RES[0]].unique().tolist()
        all_subject = Subject.select_all()
        all_names = [_.name for _ in all_subject]
        all_map = {_.name: _.id for _ in all_subject}
        self.subjects = {}
        for subject in subjects:
            f = find(all_names, subject.lower())
            if f == -1:
                raise ValueError(subject)
            self.subjects[subject] = all_map[all_names[f]]

        for subject in self.subjects:
            ys = YearSubject.build(self.year.year, self.subjects[subject], 30, 30, 30, 30, 30, 0, 0, '', '', 1)
            YearSubject.insert(ys)
        FileCreator.create_subjects(self.year.year, list(self.subjects.values()))
        Generator.gen_years_subjects_list(self.year.year)
        self.all_subjects = {_.id: _ for _ in all_subject}

    def __gen_teams__(self):
        teams = [str(_) for _ in self.code[self.CODES[4]].unique().tolist() if str(_) != 'nan']
        for team in teams:
            Team.insert(Team.build(None, 'Вертикаль ' + team, self.year.year, team))
        self.teams = {}
        for team in teams:
            self.teams[team] = Team.select_by_year_and_later(self.year.year, team).id
        Generator.gen_teams(self.year.year)

    def __gen_students__(self):
        self.student = {}
        self.students_codes = []
        for i, row in self.code.iterrows():
            names = row[0].split()
            class_ = split_class(row[1])
            student = Student.build(None, names[0], names[1], 0)
            student.set_gender(row[2])
            st = get_student_by_params(self.year, names[0], names[1], class_[0], class_[1])
            sc = StudentClass.build(0, self.year, class_[0], class_[1])
            if st is None:
                sc.student_id = sid = Student.insert(student, return_id=True)
                StudentClass.insert(sc)
            else:
                sc.student_id = student.id = sid = st.id
                Student.update(student)
                StudentClass.update(sc)
            self.student[(row[0], row[1])] = sid
            c = StudentCode.build(self.year.year, int(row[3]), int(row[3]), sid)
            StudentCode.insert(c)
            self.students_codes.append(int(row[3]))
            if str(row[4]) != 'nan':
                ts = TeamStudent.build(self.teams[str(row[4])], sid)
                TeamStudent.insert(ts)
        self.students_codes = set(self.students_codes)

    def __gen_results__(self):
        for i, row in self.result.iterrows():
            if row[0] in self.subjects and int(row[1]) in self.students_codes and str(row[2]) != 'nan':
                Result.replace(Result.build(self.year.year, self.subjects[row[0]], int(row[1]), row[2], 0, str(row[2]), 0))
        for subject in self.subjects.values():
            t = self.all_subjects[subject].type_str()
            Generator.gen_results(self.year, subject, str(self.year.year) + '/' + t + '/' + str(subject) + '.html')

    def __gen_pages__(self):
        Generator.gen_ratings(self.year.year)
        Generator.gen_timetable(self.year.year)
        data = SplitFile(Config.TEMPLATES_FOLDER + '/' + str(self.year.year) + '/subjects_for_year.html')
        data.insert_after_comment(' is_block ', '''
                    <p><input type="radio" name="is_block" value="0">Разблокировано</p>
                    <p><input type="radio" name="is_block" value="1" checked>Заблокировано</p>
                ''')
        data.save_file()

    def __gen_only_students__(self):
        for i, row in self.student.iterrows():
            names = row[0].split()
            class_ = split_class(row[1])
            student = Student.build(None, names[0], names[1], 0)
            student.set_gender(row[2])
            st = get_student_by_params(self.year, names[0], names[1], class_[0], class_[1])
            sc = StudentClass.build(0, self.year, class_[0], class_[1])
            if st is None:
                sc.student_id = Student.insert(student, return_id=True)
                StudentClass.insert(sc)
            else:
                sc.student_id = student.id = st.id
                Student.update(student)
                StudentClass.update(sc)

    def read(self):
        self.sheet = pd.read_excel(self.file, sheet_name=None, engine="openpyxl")
        self.__frames__()
        if self.qtype == 2:
            self.__get_students_cols__()
            self.__gen_only_students__()
        else:
            self.__get_codes_cols__()
            self.__get_result_cols__()
            self.__gen_subject__()
            self.__gen_teams__()
            self.__gen_students__()
            self.__gen_results__()
            self.__gen_pages__()
