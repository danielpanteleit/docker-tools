#!/usr/bin/env python3
import re
import subprocess
import sys
from argparse import ArgumentParser

import requests

from common import docker_inspect_image


def main():
    parser = ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("--latest", help="check if the specified tag is the same as latest", action="store_true")
    opts = parser.parse_args()
    image = opts.image

    if ":" not in image:
        repo = image
        tag = "latest"
    else:
        repo, tag = image.split(":")

    if "/" not in image:
        repo = "library/" + repo

    current_info = docker_inspect_image(repo + ":" + tag)[0]
    current_digest = re.sub("^.*?@(?=sha256)", "", current_info["RepoDigests"][0])
    print("current digest is", current_digest)

    resp = requests.get("https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repo}:pull".format(repo=repo))
    resp.raise_for_status()
    token = resp.json()["token"]

    digest = get_digest(repo, tag, token)
    print("found digest", digest)

    if opts.latest:
        latest_digest = get_digest(repo, "latest", token)
        if latest_digest != digest:
            print("latest is not the same as %s" % tag)

    if digest == current_digest:
        print("no new version available")
        return

    newImage = "{repo}@{digest}".format(repo=repo, digest=digest)
    subprocess.check_call(["docker", "pull", newImage])
    new_info = docker_inspect_image(newImage)[0]

    show_diff("ports", exposed_ports(current_info), exposed_ports(new_info))
    show_diff("volumes", volumes(current_info), volumes(new_info))


def get_digest(repo, tag, token):
    resp = requests.get("https://index.docker.io/v2/{repo}/manifests/{tag}".format(repo=repo, tag=tag), headers={
        "Authorization": "Bearer %s" % token,
        "Accept": "application/vnd.docker.distribution.manifest.v2+json"
    })
    resp.raise_for_status()
    return resp.headers["Docker-Content-Digest"]


def exposed_ports(info):
    return set(info["Config"].get("ExposedPorts", {}).keys())


def volumes(info):
    return set((info["Config"]["Volumes"] or {}).keys())


def show_diff(name, old, new):
    removed = old - new
    added = new - old
    if removed:
        print("removed %s:" % name, " ".join(sorted(removed)))
    if added:
        print("added %s:" % name, " ".join(sorted(added)))


if __name__ == '__main__':
    main()
