# -*- coding: utf-8 -*-

# ########################## Copyrights and license ########################## #
#                                                                              #
# Copyright 2020 Greg Caufield <greg@embeddedcoffee.ca>                        #
#                                                                              #
# This file is part of MonkeyPack Pacage Manager                               #
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

from typing import TextIO, Dict

from mbget.config import Config
from mbget.errors import UpdateError


class Packages(object):
    def __init__(self, config: Config):
        self.package_map: Dict[str, str] = {}
        config.open_file(config.package, "r", self.__parse_packages)

    def get_repo_for_package(self, package) -> str:
        return self.package_map[package]

    def __parse_packages(self, f: TextIO):
        i = 0
        for line in f.readlines():
            i += 1
            line = line.rstrip()
            if len(line) > 0:
                words = line.split("=>")
                if len(words) == 2:
                    self.package_map[words[0].rstrip()] = words[1].rstrip()
                else:
                    raise UpdateError(
                        "Poorly formatted package map on line {line_num}: {line}".format(
                            line_num=i, line=line
                        )
                    )
