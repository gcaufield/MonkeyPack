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
from io import StringIO
from unittest.mock import Mock, PropertyMock, ANY

from mbget.config import Config
from mbget.packages import Packages


class TestPackages(unittest.TestCase):
    def test_init_attempts_read(self):
        packages = StringIO("")
        mock_config = Mock(Config)
        attr = {"open_file.side_effect": lambda name, mode, cb: cb(packages)}
        mock_config.configure_mock(**attr)

        packages = Packages(mock_config)

        mock_config.open_file.assert_called_once()

    def test_init_reads_package_file(self):
        packages = StringIO("")
        mock_config = Mock(Config)
        package_mock = PropertyMock(return_value="package.txt")
        type(mock_config).package = package_mock

        attr = {"open_file.side_effect": lambda name, mode, cb: cb(packages)}
        mock_config.configure_mock(**attr)

        packages = Packages(mock_config)

        mock_config.open_file.assert_called_once_with("package.txt", ANY, ANY)

    def test_init_gets_correct_repo_path_from_package(self):
        packages = StringIO("Depend1=>owner/Depend1")
        mock_config = Mock(Config)
        attr = {"open_file.side_effect": lambda name, mode, cb: cb(packages)}
        mock_config.configure_mock(**attr)

        packages = Packages(mock_config)

        self.assertEqual("owner/Depend1", packages.get_repo_for_package("Depend1"))

    def test_init_gets_multiple_correct_repos_from_package(self):
        packages = StringIO("Depend1=>owner/Depend1\nDepend2=>owner2/Depend2")
        mock_config = Mock(Config)
        attr = {"open_file.side_effect": lambda name, mode, cb: cb(packages)}
        mock_config.configure_mock(**attr)

        packages = Packages(mock_config)

        self.assertEqual("owner/Depend1", packages.get_repo_for_package("Depend1"))
        self.assertEqual("owner2/Depend2", packages.get_repo_for_package("Depend2"))
