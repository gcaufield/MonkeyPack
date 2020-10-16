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
