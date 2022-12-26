import os

import psycopg2
from psycopg2.extensions import connection, cursor

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

tables = {
    "user": "CREATE TABLE IF NOT EXISTS user (id TEXT PRIMARY KEY, name TEXT);",
    "item": "CREATE TABLE IF NOT EXISTS item (id SERIAL PRIMARY KEY, name TEXT, userid TEXT);",
}

def drop(db: connection, table: str):
    with db.cursor() as cur:
        cur: cursor = cur
        cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
        db.commit()


def create(db: connection, query: str):
    with db.cursor() as cur:
        cur: cursor = cur
        cur.execute(query)
        db.commit()



def main():
    with psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
    ) as db:
        db: connection = db

        for table, create_query in tables.items():
            drop(db, table)
            create(db, create_query)


if __name__ == "__main__":
    main()
