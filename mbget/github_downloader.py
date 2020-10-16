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

import re

import requests
from github import Github
from github.GitRelease import GitRelease
from github.GitReleaseAsset import GitReleaseAsset

from mbget.barrel_asset import BarrelAsset
from mbget.errors import Error
from mbget.dependency import Dependency


class GithubDownloader(object):
    BARREL_FILE = re.compile(r"^.+\.barrel$")

    def __init__(self, token: str = None):
        self.__token = token

        if token is not None:
            self.__github = Github(login_or_token=token)
        else:
            self.__github = Github()

    def download_barrel(self, dependency: Dependency) -> BarrelAsset:
        release = self.__find_release(dependency)
        asset = self.__get_barrel_asset(release)
        content = self.__request_barrel_content(asset)

        return BarrelAsset(asset.name, release.tag_name, content)

    def __request_barrel_content(self, asset: GitReleaseAsset) -> bytes:
        # Found a barrel file, Download it.
        headers = {"Accept": "application/octet-stream"}

        if self.__token is not None:
            headers["Authorization"] = "token {token}".format(token=self.__token)

        req = requests.get(asset.url, headers=headers)
        return req.content

    def __get_barrel_asset(self, release: GitRelease) -> GitReleaseAsset:
        # Matching tag download the barrels
        for asset in release.get_assets():
            if self.BARREL_FILE.match(asset.name) is not None:
                return asset

        raise Error(
            "No barrel asset found in release: {rel}".format(rel=release.tag_name)
        )

    def __find_release(self, dependency: Dependency) -> GitRelease:
        assert dependency.repo is not None
        assert dependency.version is not None

        repo = self.__github.get_repo(dependency.repo)

        # Search the releases for a version that we can use
        for release in repo.get_releases():
            if not dependency.version.matches(release.tag_name):
                # Version does not match our requirement
                continue
            return release

        raise Error(
            "Unable to find matching version {version}".format(
                version=dependency.version
            )
        )
