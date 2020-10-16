# -*- coding: utf-8 -*-

# ########################## Copyrights and license ########################## #
#                                                                              #
# Copyright 2020 Greg Caufield <greg@embeddedcoffee.ca>                        #
#                                                                              #
# This file is part of MonkeyPack Package Manager                              #
#                                                                              #
# The MIT Licence                                                              #
#                                                                              #
# Permission is hereby granted, free of charge, to any person obtaining a copy #
# of this software and associated documentation files (the "Software"), to     #
# deal in the Software without restriction, including without limitation the   #
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or  #
# sell copies of the Software, and to permit persons to whom the Software is   #
# furnished to do so, subject to the following conditions:                     #
#                                                                              #
# The above copyright notice and this permission notice shall be included in   #
# all copies or substantial portions of the Software.                          #
#                                                                              #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR   #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,     #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER       #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING      #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS #
# IN THE SOFTWARE.                                                             #
#                                                                              #
# ############################################################################ #

import os
import logging

from mbget.errors import Error
from mbget.dependency import Dependency
from mbget.github_downloader import GithubDownloader
from mbget.project import Project


class Update(object):
    """Update handler"""

    def __init__(self, project: Project, downloader: GithubDownloader):
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
