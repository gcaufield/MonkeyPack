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

import json
import unittest
from io import StringIO
from unittest.mock import patch, Mock

from mbget.dependency import Dependency
from mbget.file_hasher import FileHasher
from mbget.config import Config
from mbget.cache import Cache


class CacheTest(unittest.TestCase):
    @staticmethod
    def __build_fake_cache(count: int = 0) -> str:

        if count == 0:
            cache = {
                "Depend": {"hash": "012345", "asset": "test.barrel", "version": "0.1.2"}
            }
        else:
            cache = {}
            for i in range(count):
                cache["Depend{}".format(i)] = {
                    "hash": "012345",
                    "asset": "test{}.barrel".format(i),
                    "version": "0.1.2",
                }

        return json.dumps(cache)

    def test_cache_initializes_empty_if_cache_doesnt_exist(self):
        mock_config = Mock(Config)
        config = {"exists.return_value": False}
        with patch("os.path", **config):
            cache = Cache(mock_config)

        self.assertIsNotNone(cache)

        depTest = Dependency("Depend2")
        depTest.set_version("0.1.2")
        depTest.set_barrel_name("test.barrel")
        self.assertNotIn(depTest, cache)

    def test_cache_reads_cache_file(self):
        mock_config = Mock(Config)
        config = {"exists.return_value": True}
        with patch("os.path", **config):
            Cache(mock_config)

        mock_config.open_file.assert_called_once()

    def test_cache_reads_json_cache_file(self):
        fake_cache = StringIO(self.__build_fake_cache())

        mock_config = Mock(Config)
        attr = {"open_file.side_effect": lambda name, mode, cb: cb(fake_cache)}
        mock_config.configure_mock(**attr)

        mock_hasher = Mock(FileHasher)
        hash_attr = {"match.return_value": True}
        mock_hasher.configure_mock(**hash_attr)

        config = {"exists.return_value": True}
        with patch("os.path", **config):
            cache = Cache(mock_config, mock_hasher)

        depTest = Dependency("Depend")
        depTest.set_version("0.1.2")

        self.assertTrue(depTest in cache)

    def test_cache_does_not_contain_uncached(self):
        fake_cache = StringIO(self.__build_fake_cache())

        mock_config = Mock(Config)
        attr = {"open_file.side_effect": lambda name, mode, cb: cb(fake_cache)}
        mock_config.configure_mock(**attr)

        mock_hasher = Mock(FileHasher)
        hash_attr = {"match.return_value": True}
        mock_hasher.configure_mock(**hash_attr)

        config = {"exists.return_value": True}
        with patch("os.path", **config):
            cache = Cache(mock_config, mock_hasher)

        depTest = Dependency("Depend2")
        depTest.set_version("0.1.2")

        self.assertFalse(depTest in cache)

    def test_can_add_dependency(self):
        mock_config = Mock(Config)

        mock_hasher = Mock(FileHasher)
        hash_attr = {"hash_file.return_value": "0123"}
        mock_hasher.configure_mock(**hash_attr)

        config = {"exists.return_value": False}
        with patch("os.path", **config):
            cache = Cache(mock_config, mock_hasher)

        depTest = Dependency("Depend2")
        depTest.set_version("0.1.2")
        depTest.set_barrel_name("test.barrel")

        cache.add_dependency(depTest)
        self.assertIn(depTest, cache)

    def test_can_overwrite_dependency(self):
        fake_cache = StringIO(self.__build_fake_cache())

        mock_config = Mock(Config)
        attr = {"open_file.side_effect": lambda name, mode, cb: cb(fake_cache)}
        mock_config.configure_mock(**attr)

        mock_hasher = Mock(FileHasher)
        hash_attr = {"hash_file.return_value": "0123"}
        mock_hasher.configure_mock(**hash_attr)

        config = {"exists.return_value": True}
        with patch("os.path", **config):
            cache = Cache(mock_config, mock_hasher)

        depTest = Dependency("Depend")
        depTest.set_version("0.1.2")
        self.assertIn(depTest, cache)
        self.assertNotEqual("test3.barrel", cache.get_barrel_for_package(depTest))

        depTest.set_barrel_name("test3.barrel")
        cache.add_dependency(depTest)

        self.assertEqual("test3.barrel", cache.get_barrel_for_package(depTest))

    def test_corrupt_barrel_not_in_cache(self):
        fake_cache = StringIO(self.__build_fake_cache())

        mock_config = Mock(Config)
        attr = {"open_file.side_effect": lambda name, mode, cb: cb(fake_cache)}
        mock_config.configure_mock(**attr)

        mock_hasher = Mock(FileHasher)
        hash_attr = {"match.return_value": False}
        mock_hasher.configure_mock(**hash_attr)

        config = {"exists.return_value": True}
        with patch("os.path", **config):
            cache = Cache(mock_config, mock_hasher)

        depTest = Dependency("Depend")
        depTest.set_version("0.1.2")

        self.assertNotIn(depTest, cache)

    def test_removed_barrel_not_in_cache(self):
        fake_cache = StringIO(self.__build_fake_cache(2))

        mock_config = Mock(Config)
        attr = {"open_file.side_effect": lambda name, mode, cb: cb(fake_cache)}
        mock_config.configure_mock(**attr)

        mock_hasher = Mock(FileHasher)
        hash_attr = {"match.return_value": True}
        mock_hasher.configure_mock(**hash_attr)

        config = {"exists.side_effect": lambda x: {"test0.barrel": False}.get(x, True)}
        with patch("os.path", **config):
            cache = Cache(mock_config, mock_hasher)

        dep1Test = Dependency("Depend0")
        dep1Test.set_version("0.1.2")

        dep2Test = Dependency("Depend1")
        dep2Test.set_version("0.1.2")

        self.assertIn(dep2Test, cache)
        self.assertNotIn(dep1Test, cache)
