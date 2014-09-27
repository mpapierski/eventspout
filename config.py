import os

DOCKER_HOST = os.getenv('DOCKER_HOST', '/tmp/docker.sock')
CALLBACK_URL = os.environ['CALLBACK_URL']
