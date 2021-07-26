import sqlite3
from typing import Tuple


class DataBase:
    @staticmethod
    def execute(sql: str, params=()) -> list:
        print("SQL : " + sql + ", params = " + str(params))
        connection = sqlite3.connect('backend/database.db')
        cursor = connection.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchall()
        connection.commit()
        connection.close()
        return result

    @staticmethod
    def execute_one(sql: str, params=()) -> Tuple:
        result = DataBase.execute(sql, params)
        if not result or len(result) == 0:
            return ()
        return result[0]


class Row:
    def __init__(self, cls, row):
        if len(row) == 0:
            self.__is_none__ = True
            return
        self.__is_none__ = False
        position = 0
        self.cls = cls
        for field in cls.fields:
            self.__setattr__(field, row[position])
            position += 1

    def __repr__(self):
        if self.__is_none__:
            return "{None}"
        data = {}
        for field in self.cls.fields:
            data[field] = self.__getattribute__(field)
        return str(data)

    def update_string(self):
        if self.__is_none__:
            raise ValueError("Updates row is {None}")
        text = ""
        params = []
        for field in self.cls.fields:
            text += ", " + field + " = ?"
            params.append(getattr(self, field))
        return text[2:], params


class Table:
    @staticmethod
    def conditional_query(args):
        text = ' WHERE '
        params = []
        for i in range(0, len(args), 2):
            if i > 0:
                text += ' AND '
            text += args[i] + ' = ?'
            params.append(args[i + 1])
        return text, params

    @staticmethod
    def select_all(table_name: str, cls) -> list:
        return [cls(_) for _ in DataBase.execute("SELECT * FROM " + table_name)]

    @staticmethod
    def select_by_field(table_name: str, field: str, value, cls):
        return cls(DataBase.execute_one("SELECT * FROM " + table_name + " WHERE " + field + " = ?", (value,)))

    @staticmethod
    def select_by_fields(table_name: str, cls, *args):
        x = Table.conditional_query(args)
        return cls(DataBase.execute_one("SELECT * FROM " + table_name + x[0], x[1]))

    @staticmethod
    def select_list_by_field(table_name: str, field: str, value, cls) -> list:
        return [cls(_) for _ in DataBase.execute("SELECT * FROM " + table_name + " WHERE " + field + " = ?", (value,))]

    @staticmethod
    def select_list_by_fields(table_name: str, cls, *args):
        x = Table.conditional_query(args)
        return [cls(_) for _ in DataBase.execute("SELECT * FROM " + table_name + x[0], x[1])]

    @staticmethod
    def update_by_field(table_name: str, field: str, value):
        params = value.update_string()
        params[1].append(getattr(value, field))
        return DataBase.execute("UPDATE " + table_name + " SET " + params[0] + " WHERE " + field + " = ?", params[1])

    @staticmethod
    def update_by_fields(table_name: str, new, *args):
        new = new.update_string()
        x = Table.conditional_query(args)
        return DataBase.execute("UPDATE " + table_name + " SET " + new[0] + x[0], new[1] + x[1])

    @staticmethod
    def insert_query(table_name: str, fields: list):
        text = "INSERT INTO " + table_name + "("
        for field in fields:
            text += field + ", "
        return text[:-2] + ") VALUES"

    @staticmethod
    def insert_value(value, fields):
        params = []
        text = '('
        for field in fields:
            text += "?, "
            params.append(getattr(value, field))
        return text[:-2] + ')', params

    @staticmethod
    def insert(table_name: str, value, fields: list):
        if value.__is_none__:
            raise ValueError("Insert row is {None}")
        text, params = Table.insert_value(value, fields)
        return DataBase.execute(Table.insert_query(table_name, fields) + text, params)

    @staticmethod
    def insert_all_columns(table_name: str, value):
        return Table.insert(table_name, value, value.cls.fields)

    @staticmethod
    def insert_rows(table_name: str, rows: list):
        if rows is None or len(rows) == 0:
            raise ValueError("Insert empty list of rows")
        fields = rows[0].cls.fields
        text = Table.insert_query(table_name, fields)
        params = []
        for row in rows:
            t, p = Table.insert_value(row, fields)
            text += t + ', '
            params.extend(p)
        return DataBase.execute(text[:-2], params)

    @staticmethod
    def delete(table_name: str, value):
        return DataBase.execute("DELETE FROM " + table_name + " WHERE id = ?", (value.id,))

    @staticmethod
    def delete_by_field(table_name: str, field: str, value):
        return DataBase.execute("DELETE FROM " + table_name + " WHERE " + field + " = ?", (value,))

    @staticmethod
    def delete_by_fields(table_name: str, *args):
        x = Table.conditional_query(args)
        return DataBase.execute("DELETE FROM " + table_name + x[0], x[1])
