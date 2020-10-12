import json
import os
import logging
from typing import TextIO, Dict

from mbget.config import Config
from mbget.dependency import Dependency
from mbget.file_hasher import FileHasher


class Cache(object):
    def __init__(self, config: Config, hasher: FileHasher = FileHasher()):
        self.cache: Dict[str, Dict[str, str]] = {}
        self.__hasher = hasher
        self.__config = config

        self.__read_cache_file_if_exists()
        self.__validate_cache()
        self.__dirty = False

    def __process_cache(self, file: TextIO):
        try:
            self.cache = json.load(file)
        except (OSError, json.JSONDecodeError):
            logging.debug("Cache file is corrupt.")

    def __read_cache_file_if_exists(self) -> None:
        """
        Open and read the cache file if it exists
        """
        if os.path.exists(self.__cache_file):
            self.__config.open_file(self.__cache_file, "r", self.__process_cache)

    def write_cache(self):
        """
        Write the cache file out to disk
        """
        self.__config.open_file(
            self.__cache_file, "w", lambda f: json.dump(self.cache, f)
        )
        self.__dirty = False

    def add_dependency(self, dependency: Dependency):
        entry = {
            "asset": str(dependency.barrel_name),
            "hash": self.__hasher.hash_file(dependency.barrel_name),
            "version": str(dependency.version),
        }

        self.cache[dependency.package_name] = entry
        self.__dirty = True

    def __get_asset(self, key: str) -> str:
        assert key in self.cache
        return self.cache[key]["asset"]

    def __validate_cache(self):
        invalid_entries = []
        for key in self.cache:
            if not self.__asset_exists(key):
                logging.debug(
                    "Asset {asset} removed.".format(asset=self.__get_asset(key))
                )
                invalid_entries.append(key)
            elif not self.__is_asset_valid(key):
                logging.debug(
                    "Asset {asset} corrupt.".format(asset=self.__get_asset(key))
                )
                invalid_entries.append(key)

        for entry in invalid_entries:
            self.cache.pop(entry)

    def __contains__(self, item: Dependency) -> bool:
        if item.package_name not in self.cache:
            return False

        cached_dep = self.cache[item.package_name]
        if item.version is not None:
            return item.version.matches(cached_dep["version"])
        return False

    @property
    def __cache_file(self):
        return os.path.join(self.__config.barrel_dir, ".mbgetcache")

    def __asset_exists(self, key):
        return os.path.exists(self.__get_asset(key))

    def __is_asset_valid(self, key):
        asset_path = self.__get_asset(key)
        expected_hash = self.cache[key]["hash"]
        return self.__hasher.match(asset_path, expected_hash)

    def get_barrel_for_package(self, dep) -> str:
        return self.cache[dep.package_name]["asset"]
