import os
import random
import psycopg2
from dotenv import load_dotenv
from util.print_util import verbose_print

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

    def check_connection(self, verbose=False):
        if not self.__initialized:
            return False, False
        conn_status, cur_status = False, False
        if self.__conn.closed == 0:
            conn_status = True
            verbose_print("connection is alive", verbose)
        else:
            verbose_print("connection is closed", verbose)
        if self.__cur.closed == 0:
            cur_status = True
            verbose_print("cursor is alive", verbose)
        else:
            verbose_print("cursor is closed", verbose)
        return conn_status, cur_status

    def get_connector_cursor(self):
        return self.__conn, self.__cur

    def terminate(self, verbose=False):
        if self.__initialized:
            self.__cur.close()
            self.__conn.close()
            verbose_print("DBConnector has been terminated", verbose)
        else:
            verbose_print("DBConnector wasn't initialized", verbose)


if __name__ == "__main__":
    dbc = DBConnector()
    dbc2 = DBConnector()
    dbc.check_connection()
    conn, cur = dbc.get_connector_cursor()
    conn2, cur2 = dbc.get_connector_cursor()
    cur.execute("create table if not exists test (id serial primary key, num float);")
    conn.commit()
    cur.execute(f"insert into test (num) values({random.random()})")
    conn.commit()
    cur2.execute(f"insert into test (num) values({random.random()})")
    conn2.commit()
    cur.execute("select * from test")
    all_results = cur.fetchall()
    print(*all_results, sep="\n")
    print("terminating dbc, dbc2 should also be closed")
    dbc.terminate()
    dbc.check_connection()
    dbc2.check_connection()
    dbc2.terminate()
