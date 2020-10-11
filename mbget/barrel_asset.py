from mbget.version import Version


class BarrelAsset(object):
    def __init__(self, asset_name: str, asset_version: str, asset_content: bytes):
        self.__name = asset_name
        self.__version = Version(asset_version)
        self.__content = asset_content

    @property
    def name(self) -> str:
        return self.__name

    @property
    def version(self) -> Version:
        return self.__version

    @property
    def content(self) -> bytes:
        return self.__content
