from os.path import dirname

import syncloudlib.integration.conftest
from syncloudlib.integration.conftest import *

DIR = dirname(__file__)


@pytest.fixture(scope="session")
def project_dir():
    return join(DIR, '..')


def pytest_addoption(parser):
    syncloudlib.integration.conftest.pytest_addoption(parser)
    parser.addoption("--local", action="store", default="false")


@pytest.fixture(scope='session')
def local(request):
    return request.config.getoption("--local") == "true"

