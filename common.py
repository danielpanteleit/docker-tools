import json

from docker_tools.common import docker


def docker_inspect_image(image):
    return json.loads(docker("inspect", "--type", "image", image))
