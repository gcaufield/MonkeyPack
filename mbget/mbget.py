import argparse
import hashlib
import json
import os
import re
import xml.etree.ElementTree as Et
from typing import TextIO, BinaryIO, List

import requests
from github import Github, GitRelease, GitReleaseAsset


class Error(Exception):
    """
    Base Class for exceptions in the module
    """

    def __init__(self, message: str):
        self.message = message


class ManifestError(Error):
    def __init__(self, message):
        Error.__init__(self, message)


class UpdateError(Error):
    """An Update specific error"""

    def __init__(self, message):
        Error.__init__(self, message)


class Config(object):
    def __init__(self, args):
        self.__output_dir = args.directory
        self.__jungle = args.jungle

    @property
    def jungle(self):
        return self.__jungle

    @property
    def barrel_dir(self):
        return self.__output_dir

    def prepare_project_dir(self) -> None:
        """
        Put the project dir into a state where mbget can assume that all output
        locations are valid
        :return:
        """
        self.__build_output_dir()

    def open_file(self, name, mode, callback) -> None:
        with open(name, mode) as f:
            callback(f)

    def __build_output_dir(self):
        """
        Builds the output dir if its required.

        :return:
        """
        if not os.path.exists(self.__output_dir):
            os.mkdir(self.__output_dir)

    def read_file_content(self, file, callback):
        with open(file, "r") as f:
            callback(f)

    def write_text_file(self, file, callback):
        with open(file, "w") as f:
            callback(f)


class Version(object):

    def __init__(self, version: str):
        self.version = version

    def __str__(self) -> str:
        return self.version

    def matches(self, other) -> bool:
        """

        :param other:
        :return:
        """
        tag_match = re.compile("^v?{version}".format(version=self.version))
        if tag_match.match(other) is None:
            return False

        return True


class Dependency(object):
    def __init__(self, package_name: str):
        self.__package_name = package_name
        self.__required_version = None
        self.__repo = None
        self.__barrel_name = None
        pass

    def __eq__(self, other):
        if other is not Dependency:
            return False

        return other.__package_name == self.__package_name and \
               other.__required_version == self.__required_version and \
               other.__repo == self.__repo

    @property
    def package_name(self) -> str:
        return self.__package_name

    @property
    def version(self) -> Version:
        return self.__required_version

    def set_version(self, version: str) -> None:
        self.__required_version = Version(version)

    @property
    def repo(self) -> str:
        return self.__repo

    def set_repo(self, repo: str) -> None:
        self.__repo = repo

    @property
    def barrel_name(self) -> str:
        return self.__barrel_name

    def set_barrel_name(self, name):
        self.__barrel_name = name


class Manifest(object):
    ns = {"iq": "http://www.garmin.com/xml/connectiq"}

    def __init__(self, manifest_stream: TextIO):
        self.root = Et.ElementTree(file=manifest_stream).getroot()
        self.__validate_manifest()
        self.__build_version_map()

    def get_depends(self):
        return self.version_map.keys()

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


class FileHasher(object):
    BLOCK_SIZE = 65535

    def __init__(self):
        pass

    def match(self, file_path, expected_hash) -> bool:
        return self.hash_file(file_path) == expected_hash

    def hash_file(self, file_path):
        """

        :param file_path:
        :return:
        """
        with open(file_path, 'rb') as f:
            return self.__hash_file(f)

    def __hash_file(self, f: BinaryIO) -> str:
        h = hashlib.sha256()
        fb = f.read(self.BLOCK_SIZE)
        while len(fb) > 0:
            h.update(fb)
            fb = f.read(self.BLOCK_SIZE)

        return h.hexdigest()


class Cache(object):
    def __init__(self, config: Config, hasher: FileHasher = FileHasher()):
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
            raise Error("Couldn't read cache file")

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

    def add_dependency(self, dependency: Dependency):
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

    def __contains__(self, item: Dependency) -> bool:
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


class GithubDownloader(object):
    BARREL_FILE = re.compile(r'^.+\.barrel$')

    def __init__(self, token: str = None):
        self.__token = token

        if token is not None:
            self.__github = Github(login_or_token=token)
        else:
            self.__github = Github()

    def download_barrel(self, dependency: Dependency) -> BarrelAsset:
        release = self.__find_release(dependency)
        asset = self.__get_barrel_asset(release)

        print("Downloading asset {asset} from release {rel}".format(asset=asset.name,
                                                                    rel=release.tag_name))

        content = self.__request_barrel_content(asset)
        return BarrelAsset(asset.name, release.tag_name, content)

    def __request_barrel_content(self, asset: GitReleaseAsset) -> bytes:
        # Found a barrel file, Download it.
        headers = {'Accept': 'application/octet-stream'}

        if self.__token is not None:
            headers['Authorization'] = 'token {token}'.format(token=self.__token)

        req = requests.get(asset.url, headers=headers)
        return req.content

    def __get_barrel_asset(self, release: GitRelease) -> GitReleaseAsset:
        # Matching tag download the barrels
        for asset in release.get_assets():
            if self.BARREL_FILE.match(asset.name) is not None:
                return asset

        raise Error("No barrel asset found in release: {rel}".format(rel=release.tag_name))

    def __find_release(self, dependency: Dependency) -> GitRelease:
        repo = self.__github.get_repo(dependency.repo)

        # Search the releases for a version that we can use
        for release in repo.get_releases():
            if not dependency.version.matches(release.tag_name):
                # Version does not match our requirement
                continue
            return release

        raise Error("Unable to find matching version {version}".format(
            version=dependency.version))


class Project(object):
    def __init__(self, manifest: Manifest, packages: Packages, cache: Cache, config: Config):
        """
        """
        self.dependencies = dict()
        self.manifest = manifest
        self.packages = packages
        self.__cache = cache
        self.__config = config
        self.__build_dependencies()

    @property
    def config(self) -> Config:
        return self.__config

    @property
    def cache(self):
        return self.__cache

    @property
    def uncached_dependencies(self):
        deps = []
        for dep in self.dependencies.values():
            if dep not in self.__cache:
                deps.append(dep)
        return deps

    def update_dependency(self, dependency: Dependency):
        self.__cache.add_dependency(dependency)
        self.__cache.write_cache()
        self.__add_dependency(dependency)

    def __write_barrel_jungle(self, file) -> None:
        barrel_path = "$(base.barrelPath)"
        file.write('# Do not hand edit this auto generated file from mbget\n')

        for dep in self.dependencies.values():
            file.write('{name} = "{asset}"\n'.format(name=dep.package_name, asset=dep.barrel_name))
            barrel_path += ";$({name})".format(name=dep.package_name)

        file.write("base.barrelPath = {barrel_path}".format(barrel_path=barrel_path))

    def write_barrel_jungle(self) -> None:
        """

        :param file:
        :param barrels:
        :return:
        """
        self.__config.open_file(self.__config.jungle, 'w', self.__write_barrel_jungle)


    def __build_dependencies(self):
        for dep in self.manifest.get_depends():
            self.__initialize_dependency(dep)

    def __initialize_dependency(self, dep):
        new_dep = Dependency(dep)
        new_dep.set_version(self.manifest.get_required_version(dep))
        new_dep.set_repo(self.packages.get_repo_for_package(dep))

        if new_dep in self.__cache:
            new_dep.set_barrel_name(self.__cache.get_barrel_for_package(new_dep))

        self.__add_dependency(new_dep)

    def __add_dependency(self, dep):
        self.dependencies[dep.package_name] = dep



class Update(object):
    """Update handler"""

    def __init__(self, project: Project, downloader: GithubDownloader = GithubDownloader()):
        self.__downloader = downloader
        self.__project = project

    def update_project(self) -> None:
        for dep in self.__project.uncached_dependencies:
            self.__update_dependency(dep)

        self.__project.write_barrel_jungle()

    def __update_dependency(self, dep: Dependency) -> None:
        self.__download_dependency_assets(dep)
        self.__project.update_dependency(dep)

    def __download_dependency_assets(self, dep: Dependency) -> None:
        asset = self.__downloader.download_barrel(dep)
        barrel_name = os.path.join(self.__project.config.barrel_dir, asset.name)
        self.__project.config.open_file(barrel_name, "wb", lambda f: f.write(asset.content))
        dep.set_barrel_name(barrel_name)


def update(args):
    config = Config(args)

    manifest = Manifest(args.manifest)
    with open(args.package, 'r') as package_f:
        packages = Packages(package_f)

    cache = Cache(config)
    project = Project(manifest, packages, cache, config)
    updater = Update(project)

    updater.update_project()


def main():
    parser = argparse.ArgumentParser(description='Connect IQ Package Manager')
    parser.add_argument('-t', '--token', nargs=1, help='Github API token for requests')
    parser.add_argument('-m', '--manifest', default='manifest.xml',
                        help='Specify application manifest')
    parser.add_argument('-p', '--package', default='packages.txt',
                        help='Specify the package map text file')
    parser.add_argument('-j', '--jungle', default='barrels.jungle', help='Barrel Jungle file')
    parser.add_argument('-o', '--directory', default='barrels',
                        help='Specify directory to store barrels in')
    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers()
    update_parser = subparsers.add_parser('update', help='Download and update dependencies')
    update_parser.set_defaults(func=update)

    args = parser.parse_args()
    if args.func is not None:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
