import os
import psycopg


class DatabaseService:

    def __init__(self):

        self.connection = psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            connect_timeout=10
        )

    def consultar(self, sql, parametros=None):

        with self.connection.cursor() as cursor:

            cursor.execute(
                sql,
                parametros or ()
            )

            return cursor.fetchall()

    def consultar_uno(self, sql, parametros=None):

        with self.connection.cursor() as cursor:

            cursor.execute(
                sql,
                parametros or ()
            )

            return cursor.fetchone()

    def cerrar(self):

        if self.connection:
            self.connection.close()