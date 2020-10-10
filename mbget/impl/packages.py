from typing import TextIO

from impl.errors import UpdateError


class Packages(object):
    def __init__(self, package_file: TextIO):
        self.package_map = {}
        self.__parse_packages(package_file)

    def get_repo_for_package(self, package) -> str:
        return self.package_map[package]

    def __parse_packages(self, package_stream: TextIO):
        i = 0
        for line in package_stream.readlines():
            i += 1
            line = line.rstrip()
            if len(line) > 0:
                words = line.split("=>")
                if len(words) == 2:
                    self.package_map[words[0].rstrip()] = words[1].rstrip()
                else:
                    raise UpdateError(
                        "Poorly formatted package map on line {line_num}: {line}".format(
                            line_num=i, line=line))