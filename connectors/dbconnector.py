import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import os
import random


def verbose_print(message, verbose=False):
    if verbose:
        print(message)


class DBConnector:
    __conn, __cur, __initialized = None, None, False

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
            self.__cur = self.__conn.cursor()
            self.__initialized = True
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

    def terminate(self):
        if self.__initialized:
            self.__cur.close()
            self.__conn.close()


if __name__ == "__main__":
    dbc = DBConnector()
    dbc.check_connection(True)
    conn, cur = dbc.get_connector_cursor()
    cur.execute("create table if not exists test (id serial primary key, num float);")
    conn.commit()
    cur.execute(f"insert into test (num) values({random.random()})")
    conn.commit()
    cur.execute("select * from test")
    all_results = cur.fetchall()
    print(*all_results, sep="\n")
    dbc.terminate()
    dbc.check_connection(True)
