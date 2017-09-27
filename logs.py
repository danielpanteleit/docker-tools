#!/usr/bin/env python3

import json
import re

import subprocess

import os
from operator import itemgetter

from tabulate import tabulate

from docker_tools.common import docker, docker_list


def main():
    # TODO: check for unused volumes and networks

    table = []
    for containerId in docker_list("ps", "-aq"):
        info = json.loads(docker("inspect", containerId))
        assert len(info) == 1
        info = info[0]
        name = info["Name"].lstrip("/")

        if info["HostConfig"]["LogConfig"]["Type"] != "json-file":
            continue

        logFile = info["LogPath"]
        if not logFile:
            continue
        #print(name, logFile)
        size = os.path.getsize(logFile)

        table.append([name, "%.1f" % (size/10**6)])

    print(tabulate(sorted(table, key=itemgetter(0)), headers=["Container", "Log-Size (MB)"]))


if __name__ == '__main__':
    main()
