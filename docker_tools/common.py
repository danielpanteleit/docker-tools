import subprocess


def docker(*args):
    return subprocess.check_output(["docker"] + list(args), universal_newlines=True)


def docker_list(*args):
    output = docker(*args)
    return output.rstrip().split("\n")