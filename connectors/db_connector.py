import os
import random

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

from util.print_util import verbose_print


# manage connection and cursor to DB
# recommend using helper function instead of using the DBConnector class itself
class DBConnector(object):
    __conn, __cur = None, None

    def __init__(self):
        try:
            load_dotenv()
            # Connect to an existing database
            self.__conn = psycopg2.connect(user=os.getenv("DB_USER"),
                                           password=os.getenv("DB_PASS"),
                                           host=os.getenv("DB_SERVER"),
                                           port="5432",
                                           database=os.getenv("DB_DB"))

            # Create a cursor to perform database operations
            self.__cur = self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            verbose_print("DBConnector has been initialized")
        except Exception as e:
            print("db connector failed")
            print(e)

    def get_connection(self):
        return self.__conn

    def get_cursor(self):
        return self.__cur

    def check_connection(self, verbose=False):
        verbose_print(f"connection: {self.__conn.closed}", verbose)
        verbose_print(f"cursor: {self.__cur.closed}", verbose)
        return self.__conn.closed, self.__cur.closed

    def terminate(self, verbose=False):
        self.__cur.close()
        self.__conn.close()
        verbose_print("DBConnector has been terminated", verbose)

    def execute(self, *args):
        return self.__cur.execute(*args)

    def commit(self):
        return self.__conn.commit()

    def fetchone(self):
        try:
            return self.__cur.fetchone()
        except psycopg2.ProgrammingError:
            return None

    def fetchmany(self, size):
        try:
            return self.__cur.fetchmany(size)
        except psycopg2.ProgrammingError:
            return None

    def fetchall(self):
        try:
            return self.__cur.fetchall()
        except psycopg2.ProgrammingError:
            return None


# execute query and return the result of commit
# takes same arguments as execute
# will open and close connection & cursor (open late, close early)
def execute_commit(*args):
    db_ = DBConnector()
    db_.execute(*args)
    result = db_.commit()
    test_db.terminate()
    return result


# execute query and return the result of fetchone
# takes same arguments as execute
# will open and close connection & cursor (open late, close early)
def select_one(*args):
    return select_all(*args, 1)[0]


# execute query and return the result of fetchmany with specified size
# takes same arguments as execute
# will open and close connection & cursor (open late, close early)
def select_many(*args, size):
    return select_all(*args, size)


# execute query and return the result of fetchall
# takes same arguments as execute
# will open and close connection & cursor (open late, close early)
def select_all(*args, size=-1):
    db_ = DBConnector()
    try:
        db_.execute(*args)
        if size == 1:
            result = [db_.fetchone()]
        elif size > 0:
            result = db_.fetchmany(5)
        else:
            result = db_.fetchall()
    except psycopg2.ProgrammingError:
        result = []
    db_.terminate()
    return result


if __name__ == "__main__":
    test_db = DBConnector()
    test_db.execute("create table if not exists test (id serial primary key, num float);")
    test_db.commit()
    test_db.execute(f"insert into test (num) values({random.random()})")
    test_db.commit()
    test_db.get_cursor().execute(f"insert into test (num) values({random.random()})")
    test_db.get_connection().commit()
    test_db.get_cursor().execute("select * from test")
    all_results = test_db.get_cursor().fetchall()
    print(*all_results, sep="\n")
    test_db.check_connection(verbose=True)
    print("terminating dbc, dbc2 should also be closed")
    test_db.terminate(verbose=True)
    test_db.check_connection(verbose=True)
