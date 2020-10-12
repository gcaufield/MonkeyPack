from typing import Dict, List

from mbget.cache import Cache
from mbget.manifest import Manifest
from mbget.packages import Packages
from mbget.dependency import Dependency
from mbget.config import Config


class Project(object):
    def __init__(
        self, manifest: Manifest, packages: Packages, cache: Cache, config: Config
    ):
        """"""
        self.dependencies: Dict[str, Dependency] = {}
        self.manifest = manifest
        self.packages = packages
        self.__cache = cache
        self.__config = config
        self.__build_dependencies()

    @property
    def config(self) -> Config:
        return self.__config

    @property
    def cached_dependencies(self) -> List[Dependency]:
        deps = []
        for dep in self.dependencies.values():
            if dep in self.__cache:
                deps.append(dep)
        return deps

    @property
    def uncached_dependencies(self) -> List[Dependency]:
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
        file.write("# Do not hand edit this auto generated file from mbget\n")

        for dep in self.dependencies.values():
            file.write(
                '{name} = "{asset}"\n'.format(
                    name=dep.package_name, asset=dep.barrel_name
                )
            )
            barrel_path += ";$({name})".format(name=dep.package_name)

        file.write("base.barrelPath = {barrel_path}".format(barrel_path=barrel_path))

    def write_barrel_jungle(self) -> None:
        """
        Write the barrel.jungle file out to disk
        """
        self.__config.open_file(self.__config.jungle, "w", self.__write_barrel_jungle)

    def __build_dependencies(self):
        for dep in self.manifest.get_depends():
            self.__initialize_dependency(dep)

    def __initialize_dependency(self, package_name: str) -> None:
        new_dep = Dependency(package_name)
        new_dep.set_version(self.manifest.get_required_version(package_name))
        new_dep.set_repo(self.packages.get_repo_for_package(package_name))

        if new_dep in self.__cache:
            new_dep.set_barrel_name(self.__cache.get_barrel_for_package(new_dep))

        self.__add_dependency(new_dep)

    def __add_dependency(self, dep: Dependency) -> None:
        self.dependencies[dep.package_name] = dep
