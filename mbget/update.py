import os

from mbget.dependency import Dependency
from mbget.github_downloader import GithubDownloader
from mbget.project import Project


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
