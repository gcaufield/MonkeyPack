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

from typing import TextIO, Union
from xml.etree import ElementTree as Et

from mbget.errors import Error


class Manifest(object):
    ns = {"iq": "http://www.garmin.com/xml/connectiq"}

    def __init__(self, manifest_stream: Union[TextIO, str]):
        self.root = Et.ElementTree(file=manifest_stream).getroot()
        self.__validate_manifest()
        self.__build_version_map()

    def get_depends(self):
        return list(self.version_map.keys())

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
