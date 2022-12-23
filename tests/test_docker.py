import docker
import time
import pytest
import psycopg2


def wait_until_responsive(func, pause: float, timeout: float = 30.0):
    start = time.time()
    while not func():
        if time.time() - start >= timeout:
            raise Exception
        time.sleep(pause)


def check(container):
    try:
        logs = container.logs().decode("UTF-8")
        print(logs)
        if "database system is ready to accept connections" in logs:
            return True
    except Exception:
        return False
        

@pytest.fixture
def container():
    client = docker.from_env()
    run_list = client.containers.list()
    if len(run_list) == 0:
        raise Exception
    network = list(run_list[0].attrs["NetworkSettings"]["Networks"].keys())[0]
    container = client.containers.run(
        "postgres:13.9-bullseye",
        detach=True,
        network=network,
        name="tests_httpbin_1",
        remove=True,
        environment={
            "POSTGRES_PASSWORD": "admin",
        },
    )

    try:
        wait_until_responsive(lambda: check(container), 1.0)
        yield container
    except Exception as e:
        print(e)
    finally:
        container.stop()


def test_status_code(container):
    with psycopg2.connect(
            host="tests_httpbin_1",
            user="postgres",
            password="admin",
    ) as db:
        with db.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS test (id TEXT PRIMARY KEY, name TEXT);")
            db.commit()
