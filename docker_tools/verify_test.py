import json
import sys
import unittest
from contextlib import contextmanager
from io import StringIO
from tempfile import TemporaryDirectory
from textwrap import dedent

from docker_tools.common import docker
from docker_tools.verify import verifyUnexposedPorts


class VerifyUnexposedPortsTest(unittest.TestCase):
    def test_(self):
        dockerfile = dedent("""
        FROM busybox
        
        EXPOSE 80
        
        CMD tail -f /dev/null
        """)
        with containerFromDockerfile(dockerfile, "-p=127.0.0.1::12345", "-p=127.0.0.1::80") as containerId:
            info = json.loads(docker("inspect", containerId))
            assert len(info) == 1
            info = info[0]
            name = info["Name"].lstrip("/")
            with capturedStdout() as b:
                verifyUnexposedPorts(name, info)
            output = b.getvalue()

            print(output)
            self.assertIn("port 12345/tcp mapped but not exposed", output)
            self.assertNotIn("port 80/tcp mapped but not exposed", output)


@contextmanager
def containerFromDockerfile(dockerfile, *args):
    with TemporaryDirectory() as tmpdir:
        with open("%s/Dockerfile" % tmpdir, "w") as f:
            f.write(dockerfile)
        docker("build", "-t=docker-tools_test_123", tmpdir)
        try:
            runArgs = ["run", "-d"] + list(args) + ["docker-tools_test_123"]
            containerId = docker(*runArgs).strip()
            try:
                yield containerId
            finally:
                docker("rm", "-f", containerId)
        finally:
            docker("rmi", "docker-tools_test_123")


@contextmanager
def capturedStdout():
    oldStdout = sys.stdout
    sys.stdout = StringIO()
    try:
        yield sys.stdout
    finally:
        sys.stdout = oldStdout
