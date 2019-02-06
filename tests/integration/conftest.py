import os
from time import sleep

import docker
import pytest

base = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'docker'))
build = os.path.join(base, '~build')
export = os.path.join(build, 'export')
data = os.path.join(build, 'data')
data2 = os.path.join(build, 'data2')


@pytest.fixture(scope='module')
def image_name():
    return 'bitcasterc/bitcaster:test'


@pytest.fixture(scope='module')
def client():
    return docker.from_env()


@pytest.fixture(scope='module')
def image(client, image_name):
    client.images.build(path=base, tag=image_name, rm=False)
    return client
    # client.images.remove(image_name)


@pytest.fixture(scope='module')
def container(image, client):
    c = client.containers.run(image_name,
                              volumes={data: '/mnt'},
                              ports={8000: 9999},
                              remove=True,
                              detach=True)
    sleep(5)
    yield c
    c.stop()
