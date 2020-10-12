import os
import logging

from mbget.errors import Error
from mbget.dependency import Dependency
from mbget.github_downloader import GithubDownloader
from mbget.project import Project


class Update(object):
    """Update handler"""

    def __init__(
        self, project: Project, downloader: GithubDownloader = GithubDownloader()
    ):
        self.__downloader = downloader
        self.__project = project

    def update_project(self) -> None:
        self.__project.config.prepare_project_dir()

        # Print info for cached dependencies
        for dep in self.__project.cached_dependencies:
            logging.info(
                "Using cached {barrel} for dependency {package}:{version}".format(
                    barrel=dep.barrel_name,
                    package=dep.package_name,
                    version=dep.version,
                )
            )

        for dep in self.__project.uncached_dependencies:
            self.__update_dependency(dep)

        self.__project.write_barrel_jungle()

    def __update_dependency(self, dep: Dependency) -> None:
        logging.info(
            "Updating Dependency {dep}:{version} from repository {repo}".format(
                dep=dep.package_name, version=dep.version, repo=dep.repo
            )
        )
        self.__download_dependency_assets(dep)
        self.__project.update_dependency(dep)

    def __download_dependency_assets(self, dep: Dependency) -> None:
        try:
            asset = self.__downloader.download_barrel(dep)
            logging.info(
                "Downloaded barrel {barrel} from release {tag}".format(
                    barrel=asset.name, tag=asset.version
                )
            )
        except Error as e:
            logging.error(
                "Failed to download barrel for {dep}:{version} - {msg}".format(
                    dep=dep.package_name, version=dep.version, msg=e.message
                )
            )
            return

        barrel_name = os.path.join(self.__project.config.barrel_dir, asset.name)
        self.__project.config.open_file(
            barrel_name, "wb", lambda f: f.write(asset.content)
        )
        dep.set_barrel_name(barrel_name)
