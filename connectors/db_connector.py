import os
import random

import psycopg2
from dotenv import load_dotenv

from util.print_util import verbose_print


# singleton
# manage connection and cursor to DB
class DBConnector(object):
    __conn, __cur, __initialized, obj = None, None, False, None

    def __new__(cls):
        cls.obj = super(DBConnector, cls).__new__(cls)
        if cls.__initialized:
            return cls.obj
        try:
            load_dotenv()
            # Connect to an existing database
            cls.__conn = psycopg2.connect(user=os.getenv("DB_USER"),
                                          password=os.getenv("DB_PASS"),
                                          host=os.getenv("DB_SERVER"),
                                          port="5432",
                                          database=os.getenv("DB_DB"))

            # Create a cursor to perform database operations
            cls.__cur = cls.__conn.cursor()
            cls.__initialized = True
            cls.obj.__dict__ = {
                "__conn": cls.__conn,
                "__cur": cls.__cur,
                "__initialized": True
            }
            verbose_print("DBConnector has been initialized")
            return cls.obj
        except Exception as e:
            print("db connector failed")
            print(e)

    @staticmethod
    def get_connection():
        if not DBConnector.__initialized:
            DBConnector()
        return DBConnector.__conn

    @staticmethod
    def get_cursor():
        if not DBConnector.__initialized:
            DBConnector()
        return DBConnector.__cur

    @staticmethod
    def is_db_initialized():
        return DBConnector.__initialized

    @staticmethod
    def check_connection(verbose=False):
        if not DBConnector.__initialized:
            return False, False
        conn_status, cur_status = False, False
        if DBConnector.__conn.closed == 0:
            conn_status = True
            verbose_print("connection is alive", verbose)
        else:
            verbose_print("connection is closed", verbose)
        if DBConnector.__cur.closed == 0:
            cur_status = True
            verbose_print("cursor is alive", verbose)
        else:
            verbose_print("cursor is closed", verbose)
        return conn_status, cur_status

    @staticmethod
    def terminate(verbose=False):
        if DBConnector.__initialized:
            DBConnector.__cur.close()
            DBConnector.__conn.close()
            verbose_print("DBConnector has been terminated", verbose)
        else:
            verbose_print("DBConnector wasn't initialized", verbose)


def get_connection():
    return DBConnector.get_connection()


def get_cursor():
    return DBConnector.get_cursor()


def terminate_db_connection():
    DBConnector.terminate()


if __name__ == "__main__":
    DBConnector()
    conn, cur = get_connection(), get_cursor()
    conn2, cur2 = get_connection(), get_cursor()
    cur.execute("create table if not exists test (id serial primary key, num float);")
    conn.commit()
    cur.execute(f"insert into test (num) values({random.random()})")
    conn.commit()
    cur2.execute(f"insert into test (num) values({random.random()})")
    conn2.commit()
    cur.execute("select * from test")
    all_results = cur.fetchall()
    print(*all_results, sep="\n")
    DBConnector.check_connection()
    print("terminating dbc, dbc2 should also be closed")
    terminate_db_connection()
    DBConnector.check_connection()
