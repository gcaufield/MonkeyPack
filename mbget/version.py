import re
from typing import Any


class Version(object):
    def __init__(self, version: str):
        self.version = version

    def __str__(self) -> str:
        return self.version

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            return False

        return other.version == self.version

    def matches(self, other) -> bool:
        """

        :param other:
        :return:
        """
        tag_match = re.compile("^v?{version}".format(version=self.version))
        if tag_match.match(str(other)) is None:
            return False

        return True
