from typing import TextIO
from xml.etree import ElementTree as Et

from mbget.errors import Error


class Manifest(object):
    ns = {"iq": "http://www.garmin.com/xml/connectiq"}

    def __init__(self, manifest_stream: TextIO):
        self.root = Et.ElementTree(file=manifest_stream).getroot()
        self.__validate_manifest()
        self.__build_version_map()

    def get_depends(self):
        return list(self.version_map.keys())

    def __validate_manifest(self) -> None:
        """

        :return:
        """
        if self.root.tag != "{{{iq}}}manifest".format(iq=self.ns["iq"]):
            raise Error("Invalid manifest XML")

    def __build_version_map(self):
        self.version_map = {}
        for dep in self.root.findall(".//iq:barrels/iq:depends", namespaces=self.ns):
            self.version_map[dep.attrib["name"]] = dep.attrib["version"]

    def get_required_version(self, dep: str) -> str:
        return self.version_map[dep]
