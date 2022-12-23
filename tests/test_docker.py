import docker
import time
import requests
import pytest
from requests.exceptions import ConnectionError


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False

def wait_until_responsive(func, pause: float, timeout: float = 30.0):
    start = time.time()
    while not func():
        if time.time() - start >= timeout:
            raise Exception
        time.sleep(pause)


@pytest.fixture
def container():
    client = docker.from_env()
    run_list = client.containers.list()
    if len(run_list) == 0:
        raise Exception
    network = list(run_list[0].attrs["NetworkSettings"]["Networks"].keys())[0]

    container = client.containers.run(
        "kennethreitz/httpbin:latest",
        detach=True,
        network=network,
        name="tests_httpbin_1",
        remove=True,
    )

    try:
        wait_until_responsive(lambda: is_responsive("http://tests_httpbin_1"), 1.0)
        yield container
    except Exception as e:
        print(e)
    finally:
        print("Teardown...")
        container.stop()



def test_status_code(container):
    url = "http://tests_httpbin_1/status/200"

    response = requests.get(url)

    assert response.status_code == 200

