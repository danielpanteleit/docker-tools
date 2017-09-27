import json

from docker_tools.common import docker, docker_list


class Command:
    HELP = None

    def run(self, opts):
        pass

    @classmethod
    def help(cls):
        return cls.HELP

    @classmethod
    def addArguments(cls, parser):
        pass

class Verify(Command):
    HELP = "Verifies that containers use images as intended (e.g. using exposed ports and volumes)"

    def run(self, opts):
        for containerId in docker_list("ps", "-aq"):
            info = json.loads(docker("inspect", containerId))
            assert len(info) == 1
            info = info[0]
            name = info["Name"].lstrip("/")

            verifyUnexposedPorts(name, info)


def verifyUnexposedPorts(name, info):
    # verify used ports were all exposed

    imageInfo = json.loads(docker("inspect", info["Image"]))[0]

    exposed_ports = set(imageInfo["Config"].get("ExposedPorts", {}).keys())
    for p in info["HostConfig"]["PortBindings"] or []:
        if p not in exposed_ports:
            print("%s: port %s mapped but not exposed" % (name, p))
