import os

# Docker host. When running from Docker container you can set
# -v /var/run/docker.sock:/tmp/docker.sock
DOCKER_HOST = os.getenv('DOCKER_HOST', '/tmp/docker.sock')
# Address where you want to send events. You might want to
# consider using SSL endpoint.
CALLBACK_URL = os.environ['CALLBACK_URL']
# Some secret key so your callback can do auth for event
SECRET_KEY = os.environ['SECRET_KEY']
