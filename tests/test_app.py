import os
import docker
import time
import pytest
import psycopg2

import app

IS_LOCAL = os.getenv("IS_LOCAL", False)
LOCAL_PORT = "5434"

POSTGRES_HOST = "postgres"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "admin"


def wait_until_responsive(func, pause: float, timeout: float = 30.0):
    start = time.time()
    while not func():
        if time.time() - start >= timeout:
            raise Exception
        time.sleep(pause)


def check(container):
    try:
        logs = container.logs().decode("UTF-8")
        if "PostgreSQL init process complete; ready for start up." in logs:
            return True
    except Exception:
        return False


@pytest.fixture
def container():
    client = docker.from_env()
    options = {
        "detach": True,
        "name": POSTGRES_HOST,
        "remove": True,
        "environment": {
            "POSTGRES_USER": POSTGRES_USER,
            "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
        },
    }

    if IS_LOCAL:
        options["ports"] = {"5432/tcp": f"{LOCAL_PORT}"}
    else:
        run_list = client.containers.list()
        if len(run_list) > 0:
            network = list(
                run_list[0].attrs["NetworkSettings"]["Networks"].keys()
            )[0]
            options["network"] = network

    container = client.containers.run(
        "postgres:13.9-bullseye",
        **options,
    )

    try:
        wait_until_responsive(lambda: check(container), 1.0)
        yield container
    except Exception as e:
        print(e)
    finally:
        container.stop()


def test_status_code(container):
    if IS_LOCAL:
        host = "localhost"
        port = LOCAL_PORT
    else:
        host = POSTGRES_HOST
        port = "5432"

    tables = {
        "user": "CREATE TABLE IF NOT EXISTS user (id TEXT PRIMARY KEY, name TEXT);",
        "item": "CREATE TABLE IF NOT EXISTS item (id SERIAL PRIMARY KEY, name TEXT, userid TEXT);",
    }


    with psycopg2.connect(
        host=host,
        port=port,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    ) as db:
        for table, query in tables.items():
            app.create(db, query)
            app.drop(db, table)
            app.create(db, query)
