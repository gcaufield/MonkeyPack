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

import unittest
from unittest.mock import patch, mock_open, Mock

from mbget.config import Config


class MicroMock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestConfig(unittest.TestCase):
    @staticmethod
    def __build_args(
        token=None, package="packages.txt", directory="barrels", jungle="barrels.jungle"
    ):
        return MicroMock(
            token=token, package=package, directory=directory, jungle=jungle
        )

    def test_can_init_config(self):
        Config(self.__build_args())

    def test_token_is_none(self):
        cfg = Config(self.__build_args(token=None))
        self.assertIsNone(cfg.token)

    def test_token_is_valid(self):
        cfg = Config(self.__build_args(token=["12345abc"]))
        self.assertEqual("12345abc", cfg.token)

    def test_token_from_env_if_arg_is_none(self):
        with patch.dict("os.environ", {"MBGET_GH_TOKEN": "125aeb"}):
            cfg = Config(self.__build_args(token=None))
            self.assertEqual("125aeb", cfg.token)

    def test_token_prioritizes_args_over_env(self):
        with patch.dict("os.environ", {"MBGET_GH_TOKEN": "125aeb"}):
            cfg = Config(self.__build_args(token=["12345abc"]))
            self.assertEqual("12345abc", cfg.token)

    def test_barrel_dir_is_valid(self):
        cfg = Config(self.__build_args(directory="barrels"))
        self.assertEqual("barrels", cfg.barrel_dir)

    def test_package_is_valid(self):
        cfg = Config(self.__build_args(package="packages.txt"))
        self.assertEqual("packages.txt", cfg.package)

    def test_jungle_is_valid(self):
        cfg = Config(self.__build_args(jungle="barrels.jungle"))
        self.assertEqual("barrels.jungle", cfg.jungle)

    def test_prepare_builds_output_dir_if_not_exists(self):
        cfg = Config(self.__build_args(directory="barrels"))

        with patch("os.path.exists") as e, patch("os.mkdir") as m:
            e.return_value = False
            cfg.prepare_project_dir()
            m.assert_called_once_with("barrels")

    def test_prepare_does_not_build_output_dir_if_exists(self):
        cfg = Config(self.__build_args(directory="barrels"))

        with patch("os.path.exists") as e, patch("os.mkdir") as m:
            e.return_value = True
            cfg.prepare_project_dir()
            m.assert_not_called()

    def test_open_file_calls_callback_with_expected_stream(self):
        cfg = Config(self.__build_args())
        cb = Mock()

        with patch("builtins.open", mock_open(read_data="A Test file")):
            cfg.open_file("mockfile", "r", cb)

        cb.assert_called_once()

    def test_open_file_passes_file_to_callback(self):
        cfg = Config(self.__build_args())

        with patch("builtins.open", mock_open(read_data="A Test file")):
            cfg.open_file(
                "mockfile", "r", lambda f: self.assertEqual("A Test file", f.readline())
            )

    def test_open_file_can_write(self):
        cfg = Config(self.__build_args())
        m = mock_open()

        with patch("builtins.open", m):
            cfg.open_file("mockfile", "w", lambda f: f.write("some data"))

        m.assert_called_once_with("mockfile", "w")
        handle = m()
        handle.write.assert_called_once_with("some data")
