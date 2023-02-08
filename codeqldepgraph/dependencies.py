from typing import *
import os
import logging
from datetime import datetime

from codeqldepgraph import __name__, __version__, __url__

logger = logging.getLogger(__name__)


class Dependency:
    def __init__(self, **kwargs):
        self.namespace = kwargs.get("namespace")
        self.name = kwargs.get("name")
        self.version = kwargs.get("version")
        self.manager = kwargs.get("manager")
        self.path = kwargs.get("path")

    @staticmethod
    def parse(data: str) -> "Dependency":
        filepath, name, version = data.split("<|>")

        dep = Dependency(name=name, version=version, path=filepath).parseJava()
        return dep

    def parseJava(self):
        if self.path and self.path.endswith(".jar"):
            # We assume that we are using Maven
            self.manager = "maven"

            pathcomps = self.path.split(os.path.sep)
            jar = pathcomps[-1].replace(".jar", "")
            # split on last dash
            self.name, self.version = jar.rsplit("-", 1)

            next = False
            for part in reversed(pathcomps):
                if next:
                    self.namespace = part
                    break
                elif part == self.name:
                    next = True
        return self

    def getName(self):
        if self.manager == "maven":
            return f"{self.namespace}.{self.name}"
        return self.name

    def getPurl(self):
        return f"pkg:{self.manager}/{self.namespace}/{self.name}@{self.version}"

    def __str__(self) -> str:
        """Return a string representation of the dependency"""
        return self.getPurl()


def parseDependencies(data: str) -> list[Dependency]:
    results = []
    results_purl = []

    for line in data:
        dep = Dependency.parse(line)
        if dep.getPurl() not in results_purl:
            results.append(dep)
            results_purl.append(dep.getPurl())
        else:
            logger.debug(f"Duplicate dependency: {dep.getPurl()}")
    return results


def exportDependencies(dependencies: list[Dependency], **kwargs):
    resolved = {}
    for dep in dependencies:
        name = dep.getName()
        purl = dep.getPurl()
        resolved[name] = {"package_url": purl}
    data = {
        "version": 0,
        "sha": kwargs.get("sha"),
        "ref": kwargs.get("ref"),
        "job": {"correlator": __name__, "id": __name__},
        "detector": {"name": __name__, "version": __version__, "url": __url__},
        "scanned": datetime.now().isoformat(),
        "manifests": {
            __name__: {
                "name": __name__,
                "file": {
                    "source_location": "codeql",
                },
                "resolved": resolved,
            }
        },
    }
    return data
