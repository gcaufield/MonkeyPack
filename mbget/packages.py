from typing import TextIO, Dict

from mbget.config import Config
from mbget.errors import UpdateError


class Packages(object):
    def __init__(self, config: Config):
        self.package_map: Dict[str, str] = {}
        config.open_file(config.package, "r", self.__parse_packages)

    def get_repo_for_package(self, package) -> str:
        return self.package_map[package]

    def __parse_packages(self, f: TextIO):
        i = 0
        for line in f.readlines():
            i += 1
            line = line.rstrip()
            if len(line) > 0:
                words = line.split("=>")
                if len(words) == 2:
                    self.package_map[words[0].rstrip()] = words[1].rstrip()
                else:
                    raise UpdateError(
                        "Poorly formatted package map on line {line_num}: {line}".format(
                            line_num=i, line=line
                        )
                    )
