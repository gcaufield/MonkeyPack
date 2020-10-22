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
import unittest
from unittest.mock import patch, mock_open, Mock

from mbget.config import Config


class MicroMock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestConfig(unittest.TestCase):
    @staticmethod
    def __build_args(
        token=None, package=None, directory=None, jungle=None, manifest=None, config=None
    ):
        return MicroMock(
            token=token,
            package=package,
            directory=directory,
            jungle=jungle,
            manifest=manifest,
            config=config
        )

    @staticmethod
    def __build_cfg(package=None, directory=None, jungle=None, manifest=None) -> str:
        rv = "[mbget]\n"

        if package is not None:
            rv += "package = {}\n".format(package)

        if directory is not None:
            rv += "directory = {}\n".format(directory)

        if jungle is not None:
            rv += "jungle = {}\n".format(jungle)

        if manifest is not None:
            rv += "manifest = {}\n".format(manifest)

        return rv

    def setUp(self):
        super(TestConfig, self).setUp()
        pat = patch("os.path.exists")
        self.__mock_path = pat.start()
        self.__mock_path.return_value = False
        self.addCleanup(pat.stop)

    def test_can_init_config(self):
        Config(self.__build_args())

    def test_reads_default_config_file_if_exists(self):
        self.__mock_path.return_value = True
        m = mock_open(read_data="")
        with patch("builtins.open", m):
            Config(self.__build_args())

        m.assert_called_once_with("mbgetcfg.ini", "r")

    def test_reads_config_file_from_args(self):
        self.__mock_path.return_value = True
        m = mock_open(read_data="")
        with patch("builtins.open", m):
            Config(self.__build_args(config="test.ini"))

        m.assert_called_once_with("test.ini", "r")

    def test_token_is_none(self):
        cfg = Config(self.__build_args(token=None))
        self.assertIsNone(cfg.token)

    def test_token_is_valid(self):
        cfg = Config(self.__build_args(token="12345abc"))
        self.assertEqual("12345abc", cfg.token)

    def test_token_from_env_if_arg_is_none(self):
        with patch.dict("os.environ", {"MBGET_GH_TOKEN": "125aeb"}):
            cfg = Config(self.__build_args(token=None))
            self.assertEqual("125aeb", cfg.token)

    def test_token_prioritizes_args_over_env(self):
        with patch.dict("os.environ", {"MBGET_GH_TOKEN": "125aeb"}):
            cfg = Config(self.__build_args(token="12345abc"))
            self.assertEqual("12345abc", cfg.token)

    def test_default_barrel_dir_is_valid(self):
        cfg = Config(self.__build_args())
        self.assertEqual(".mbpkg", cfg.barrel_dir)

    def test_barrel_dir_is_valid(self):
        cfg = Config(self.__build_args(directory="barrels"))
        self.assertEqual("barrels", cfg.barrel_dir)

    def test_barrel_dir_from_cfg_is_valid(self):
        self.__mock_path.return_value = True
        m = mock_open(read_data=self.__build_cfg(directory="barrels"))
        with patch("builtins.open", m):
            cfg = Config(self.__build_args())

        self.assertEqual("barrels", cfg.barrel_dir)

    def test_default_package_is_valid(self):
        cfg = Config(self.__build_args())
        self.assertEqual("packages.txt", cfg.package)

    def test_package_is_valid(self):
        cfg = Config(self.__build_args(package="pck.txt"))
        self.assertEqual("pck.txt", cfg.package)

    def test_package_from_cfg_is_valid(self):
        self.__mock_path.return_value = True
        m = mock_open(read_data=self.__build_cfg(package="pack.txt"))
        with patch("builtins.open", m):
            cfg = Config(self.__build_args())

        self.assertEqual("pack.txt", cfg.package)

    def test_default_jungle_is_valid(self):
        cfg = Config(self.__build_args())
        self.assertEqual("barrels.jungle", cfg.jungle)

    def test_jungle_is_valid(self):
        cfg = Config(self.__build_args(jungle="brrls.jungle"))
        self.assertEqual("brrls.jungle", cfg.jungle)

    def test_jungle_from_cfg_is_valid(self):
        self.__mock_path.return_value = True
        m = mock_open(read_data=self.__build_cfg(jungle="brl.jungle"))
        with patch("builtins.open", m):
            cfg = Config(self.__build_args())

        self.assertEqual("brl.jungle", cfg.jungle)

    def test_default_manifest_is_valid(self):
        cfg = Config(self.__build_args())
        self.assertEqual("manifest.xml", cfg.manifest)

    def test_manifest_is_valid(self):
        cfg = Config(self.__build_args(manifest="mfst.xml"))
        self.assertEqual("mfst.xml", cfg.manifest)

    def test_manifest_from_cfg_is_valid(self):
        self.__mock_path.return_value = True
        m = mock_open(read_data=self.__build_cfg(manifest="man.xml"))
        with patch("builtins.open", m):
            cfg = Config(self.__build_args())

        self.assertEqual("man.xml", cfg.manifest)

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
