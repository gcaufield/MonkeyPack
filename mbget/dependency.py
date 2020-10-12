from typing import Optional, Any

from mbget.version import Version


class Dependency(object):
    def __init__(self, package_name: str):
        self.__package_name = package_name
        self.__required_version: Optional[Version] = None
        self.__repo: Optional[str] = None
        self.__barrel_name: Optional[str] = None
        pass

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Dependency):
            return False

        return (
            other.__package_name == self.__package_name
            and other.__required_version == self.__required_version
            and other.__repo == self.__repo
        )

    @property
    def package_name(self) -> str:
        return self.__package_name

    @property
    def version(self) -> Optional[Version]:
        return self.__required_version

    def set_version(self, version: str) -> None:
        self.__required_version = Version(version)

    @property
    def repo(self) -> Optional[str]:
        return self.__repo

    def set_repo(self, repo: str) -> None:
        self.__repo = repo

    @property
    def barrel_name(self) -> Optional[str]:
        return self.__barrel_name

    def set_barrel_name(self, name: str) -> None:
        self.__barrel_name = name
