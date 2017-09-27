#!/usr/bin/env python3

import json
import re

from docker_tools.common import docker, docker_list


def main():
    # TODO: check for unused volumes and networks

    for containerId in docker_list("ps", "-aq"):
        info = json.loads(docker("inspect", containerId))
        assert len(info) == 1
        info = info[0]
        name = info["Name"].lstrip("/")

        # verify used ports were all exposed
        exposed_ports = set(info["Config"].get("ExposedPorts", {}).keys())
        for p in info["HostConfig"]["PortBindings"] or []:
            if p not in exposed_ports:
                print("%s: port %s mapped but not exposed" % (name, p))

        # verify all binds are volumes
        # verify all volumes are bound (heuristically via volume name)
        volumes = set((info["Config"]["Volumes"] or {}).keys())
        left = set(volumes)
        for b in info["Mounts"] or []:
            dest = b["Destination"]
            if dest not in volumes:
                print("%s: directory %s bound but not a volume" % (name, dest))
            else:
                left.remove(dest)
            if b["Type"] == 'volume' and re.match(r"[0-9a-f]{64}$", b["Name"]):
                print("%s: using generated volume %s for mount %s" % (name, b["Name"], dest))

        for v in left:
            print("%s: volume %s not mounted" % (name, v))


if __name__ == '__main__':
    main()
