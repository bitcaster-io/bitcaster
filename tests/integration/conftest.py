import os
from pathlib import Path
from time import sleep

import docker
import pytest

# base =
# build = os.path.join(base, '~build')
# export = os.path.join(build, 'export')
# data = os.path.join(build, 'data')
# data2 = os.path.join(build, 'data2')


@pytest.fixture(scope='module')
def workingdir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


@pytest.fixture(scope='module')
def image_name():
    return 'bitcasterc/bitcaster:test'


@pytest.fixture(scope='module')
def client():
    return docker.from_env()


@pytest.fixture(scope='module')
def image(client, image_name, workingdir):
    assert Path(workingdir).is_dir()
    assert (Path(workingdir) / 'docker' / 'Dockerfile').exists()
    dockerfile = str(Path(workingdir) / 'docker' / 'Dockerfile')
    client.images.build(path=workingdir,
                        dockerfile=dockerfile,
                        buildargs={'DEVELOP': 1},
                        tag=image_name,
                        rm=False)
    return client
    # client.images.remove(image_name)


@pytest.fixture(scope='module')
def container(image, client):
    c = client.containers.run(image_name,
                              ports={8000: 9999},
                              remove=True,
                              detach=True)
    sleep(5)
    yield c
    c.stop()
