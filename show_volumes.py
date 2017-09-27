#!/usr/bin/env python3

from collections import defaultdict

from docker_tools.common import docker_list


def main():

    volumes = docker_list("volume", "ls", "-f", "driver=local", "-q")
    #print(volumes)

    usage = {v: [] for v in volumes}
    perContainer = defaultdict(list)

    for line in docker_list("ps", "-a", "--format", "{{.ID}}\t{{.Mounts}}\t{{.Names}}", "--no-trunc"):
        containerId, mounts, names = line.split("\t")
        if not mounts:
            continue
        mounts = [m for m in mounts.split(",") if "/" not in m]
        for m in mounts:
            usage[m].append(names)
            perContainer[names].append(m)


    print("Volumes\n")
    for volume, containers in sorted(usage.items(), key=lambda x: len(x[1]), reverse=True):
        if not containers:
            continue
        print(volume)
        for c in containers:
            print(" -", c)
        print()

    #pprint(usage)



    # docker volume ls -f driver=local -q
    #output = subprocess.check_output(["docker", "ps", "-a", "--format", "{{.Image}}"], universal_newlines=True)


if __name__ == '__main__':
    main()
