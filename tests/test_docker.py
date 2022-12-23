import docker
import time
import requests
# import pytest
# import requests

# from requests.exceptions import ConnectionError


# def is_responsive(url):
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             return True

#     except ConnectionError:
#         return False


# @pytest.fixture(scope="session")
# def http_service(docker_ip, docker_services):
#     port = docker_services.port_for("httpbin", 80)
#     # url = "http://{}:{}".format(docker_ip, port)
#     url = "http://tests_httpbin_1"
#     docker_services.wait_until_responsive(
#         timeout=30.0, pause=0.1, check=lambda: is_responsive(url),
#     )

#     return urld

    


# def test_status_code(http_service):
def test_status_code():
    client = docker.from_env()
    run_list = client.containers.list()
    if len(run_list) == 0:
        print("There is no running image")
        assert False
    network = list(run_list[0].attrs["NetworkSettings"]["Networks"].keys())[0]
    print(network)

    # Run a new container
    container = client.containers.run("kennethreitz/httpbin:latest", detach=True, network=network, name="tests_httpbin_1", remove=True)
    time.sleep(10)
    print(container.logs())
    url = "http://tests_httpbin_1/status/200"

    response = requests.get(url)

    print(response.status_code)
    print(response)

    container.stop()
    
    assert False
    # status = 418
    # response = requests.get(http_service + "/status/{}".format(status))

    # assert response.status_code == status
