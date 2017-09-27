#!/usr/bin/env python3
import subprocess

def main():
    output = subprocess.check_output(["docker", "ps", "-a", "--format", "{{.Image}}"], universal_newlines=True)
    container_images = set(output.strip().split("\n"))

    output = subprocess.check_output(["docker", "images", "--format", "{{.ID}} {{.Repository}}:{{.Tag}}"], universal_newlines=True)
    names = {imageId: imageId if name.endswith("<none>") else name for line in output.strip().split("\n") for imageId, name in [line.split(" ", 1)]}
    unused = set(names.keys())

    for ci in container_images:
        output = subprocess.check_output(["docker", "history", "-q", ci], universal_newlines=True)
        history_images = {i for i in output.strip().split("\n") if i != "<missing>"}
        unused -= history_images

    for i in sorted(unused):
        print(names[i])

if __name__ == '__main__':
    main()
