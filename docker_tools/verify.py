import json
import re

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
            verifyVolumeMounts(name, info)


def verifyUnexposedPorts(name, info):
    # verify used ports were all exposed

    imageInfo = json.loads(docker("inspect", info["Image"]))[0]

    exposed_ports = set(imageInfo["Config"].get("ExposedPorts", {}).keys())
    for p in info["HostConfig"]["PortBindings"] or []:
        if p not in exposed_ports:
            print("%s: port %s mapped but not exposed" % (name, p))


def verifyVolumeMounts(name, info):
    # verify all binds are volumes
    # verify all volumes are bound (heuristically via volume name)

    imageInfo = json.loads(docker("inspect", info["Image"]))[0]

    imageVolumes = set((imageInfo["ContainerConfig"]["Volumes"] or {}).keys())
    left = set(imageVolumes)
    for b in info["Mounts"] or []:
        dest = b["Destination"]
        if dest not in imageVolumes:
            print("%s: directory %s bound but not a volume" % (name, dest))
        else:
            left.remove(dest)
        if b["Type"] == 'volume' and re.match(r"[0-9a-f]{64}$", b["Name"]):
            print("%s: using generated volume %s for mount %s" % (name, b["Name"], dest))

    for v in left:
        print("%s: volume %s not mounted" % (name, v))
