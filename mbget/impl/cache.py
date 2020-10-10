import json
import os
from typing import TextIO

from impl.file_hasher import FileHasher
from impl import dependency, errors, config


class Cache(object):
    def __init__(self, config: config, hasher: FileHasher = FileHasher()):
        self.cache = {}
        self.hasher = hasher
        self.__config = config

        self.__read_cache_file_if_exists()
        self.__validate_cache()
        self.__dirty = False

    def __process_cache(self, file: TextIO):
        try:
            self.cache = json.load(file)
        except (OSError, json.JSONDecodeError):
            # Couldn't open cache TODO add CacheError
            raise errors.Error("Couldn't read cache file")

    def __read_cache_file_if_exists(self) -> None:
        """

        :param file:
        :return:
        """
        if os.path.exists(self.__cache_file):
            self.__config.open_file(self.__cache_file, "r", self.__process_cache)

    def write_cache(self):
        """

        :param file:
        :return:
        """
        self.__config.open_file(self.__cache_file, "w", lambda f: json.dump(self.cache, f))
        self.__dirty = False

    def add_dependency(self, dependency: dependency):
        entry = {"asset": dependency.barrel_name,
                 "hash": self.hasher.hash_file(dependency.barrel_name),
                 "version": str(dependency.version)}

        self.cache[dependency.package_name] = entry
        self.__dirty = True

    def __validate_cache(self):
        invalid_entries = []
        for key in self.cache:
            if not self.__asset_exists(key):
                invalid_entries.append(key)
            elif not self.__is_asset_valid(key):
                invalid_entries.append(key)

        for entry in invalid_entries:
            self.cache.pop(entry)

    def __contains__(self, item: dependency) -> bool:
        if item.package_name not in self.cache:
            return False

        cached_dep = self.cache[item.package_name]
        return item.version.matches(cached_dep["version"])

    @property
    def __cache_file(self):
        return os.path.join(self.__config.barrel_dir, '.mbgetcache')

    def __asset_exists(self, key):
        return os.path.exists(self.cache[key]["asset"])

    def __is_asset_valid(self, key):
        asset_path = self.cache[key]["asset"]
        expected_hash = self.cache[key]["hash"]
        return self.hasher.match(asset_path, expected_hash)

    def get_barrel_for_package(self, dep) -> str:
        return self.cache[dep.package_name]["asset"]