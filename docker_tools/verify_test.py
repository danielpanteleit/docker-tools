import json
import re
import sys
import unittest
import uuid
from contextlib import contextmanager
from io import StringIO
from random import random
from tempfile import TemporaryDirectory
from textwrap import dedent

from docker_tools.common import docker
from docker_tools.verify import verifyUnexposedPorts, verifyVolumeMounts


class VerifyUnexposedPortsTest(unittest.TestCase):
    def test_usingUnexposedPort_emitsWarning(self):
        dockerfile = makeDockerfile()
        with containerFromDockerfile(dockerfile, "-p=127.0.0.1::80") as (containerName, containerId):
            output = self.runVerify(containerId)

        assert "%s: port 80/tcp mapped but not exposed" % containerName in output

    def test_usingExposedPort_doesNotEmitWarning(self):
        dockerfile = makeDockerfile("""
            EXPOSE 80
        """)

        with containerFromDockerfile(dockerfile, "-p=127.0.0.1::80") as (containerName, containerId):
            output = self.runVerify(containerId)

        assert output == ""

    def runVerify(self, containerId):
        info = json.loads(docker("inspect", containerId))
        assert len(info) == 1
        info = info[0]
        name = info["Name"].lstrip("/")
        with capturedStdout() as b:
            verifyUnexposedPorts(name, info)
        output = b.getvalue()
        return output


class VerifyVolumeMountsTest(unittest.TestCase):
    def test_mountingNonVolume_emitsWarning(self):
        dockerfile = makeDockerfile()

        with containerFromDockerfile(dockerfile, "-v=/tmp/somedir:/data") as (containerName, containerId):
            output = self.runVerify(containerId)

        assert "%s: directory /data bound but not a volume" % containerName in output

    def test_mountingAVolume_doesNotEmitWarnings(self):
        dockerfile = makeDockerfile("""
            VOLUME /data
        """)

        with containerFromDockerfile(dockerfile, "-v=/tmp/somedir:/data") as (containerName, containerId):
            output = self.runVerify(containerId)

        assert output == ""

    def test_notMountingAVolume_emitsAWarning(self):
        dockerfile = makeDockerfile("""
            VOLUME /data
        """)

        with containerFromDockerfile(dockerfile) as (containerName, containerId):
            output = self.runVerify(containerId)

        print(output)
        self.assertRegex(output, r"%s: using generated volume [0-9a-f]+ for mount /data" % containerName)

    def runVerify(self, containerId):
        info = json.loads(docker("inspect", containerId))
        assert len(info) == 1
        info = info[0]
        name = info["Name"].lstrip("/")
        with capturedStdout() as b:
            verifyVolumeMounts(name, info)
        output = b.getvalue()
        return output


def makeDockerfile(lines=""):
    return "FROM busybox\n%s\nCMD tail -f /dev/null\n" % dedent(lines).lstrip()


@contextmanager
def containerFromDockerfile(dockerfile, *args):
    with TemporaryDirectory() as tmpdir:
        with open("%s/Dockerfile" % tmpdir, "w") as f:
            f.write(dockerfile)
        imageName = "docker-tools_test_i%s" % uuid.uuid4()
        docker("build", "-t", imageName, tmpdir)
        try:

            containerName = "docker-tools_test_c%s" % uuid.uuid4()
            runArgs = ["run", "-d", "--name", containerName] + list(args) + [imageName]
            containerId = docker(*runArgs).strip()
            try:
                yield containerName, containerId
            finally:
                docker("rm", "-fv", containerId)
        finally:
            docker("rmi", imageName)


@contextmanager
def capturedStdout():
    oldStdout = sys.stdout
    sys.stdout = StringIO()
    try:
        yield sys.stdout
    finally:
        sys.stdout = oldStdout
