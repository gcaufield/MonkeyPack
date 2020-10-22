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
from configparser import ConfigParser
from typing import Optional


class Config(object):
    __DEFAULTS__ = {
        "package": "packages.txt",
        "directory": ".mbpkg",
        "jungle": "barrels.jungle",
        "manifest": "manifest.xml",
    }

    def __init__(self, args):
        self.__args = args
        self.__config_file = None
        if args.config is not None:
            config_path = args.config
        else:
            config_path = "mbgetcfg.ini"

        if os.path.exists(config_path):
            config = ConfigParser()
            with open(config_path, "r") as f:
                data = f.read()

            config.read_string(data)

            if "mbget" in config:
                self.__config_file = config["mbget"]

        self.__cached_vals = {}

        if args.token is not None:
            self.__token = args.token
        elif "MBGET_GH_TOKEN" in os.environ:
            self.__token = os.environ["MBGET_GH_TOKEN"]
        else:
            self.__token = None

    @property
    def jungle(self) -> str:
        return self.__get_cached_config("jungle")

    @property
    def package(self) -> str:
        return self.__get_cached_config("package")

    @property
    def barrel_dir(self) -> str:
        return self.__get_cached_config("directory")

    @property
    def token(self) -> Optional[str]:
        return self.__token

    @property
    def manifest(self) -> str:
        return self.__get_cached_config("manifest")

    def prepare_project_dir(self) -> None:
        """
        Put the project dir into a state where mbget can assume that all output
        locations are valid
        :return:
        """
        self.__build_output_dir()

    def __build_output_dir(self):
        """
        Builds the output dir if its required.

        :return:
        """
        if not os.path.exists(self.barrel_dir):
            os.mkdir(self.barrel_dir)

    def __get_cached_config(self, param) -> str:
        if param not in self.__cached_vals:
            self.__add_config_to_cache(param)

        return self.__cached_vals[param]

    def __add_config_to_cache(self, param):
        if hasattr(self.__args, param) and getattr(self.__args, param) is not None:
            val = getattr(self.__args, param)
        elif self.__config_file is not None and param in self.__config_file:
            val = self.__config_file[param]
        else:
            val = self.__DEFAULTS__[param]

        self.__cached_vals[param] = val

    @staticmethod
    def open_file(name, mode, callback) -> None:
        with open(name, mode) as f:
            callback(f)
