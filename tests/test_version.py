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

from mbget.version import Version


class TestVersion(unittest.TestCase):
    def test_version_matches(self):
        ver = Version("0.2.4")
        self.assertTrue(ver.matches("0.2.4"))

    def test_version_matches_v(self):
        ver = Version("0.2.4")
        self.assertTrue(ver.matches("v0.2.4"))

    def test_version_doesnt_match(self):
        ver = Version("0.4.7")
        self.assertFalse(ver.matches("v0.2.4"))

    def test_version_matches_version(self):
        ver = Version("0.4.5")
        ver2 = Version("0.4.5")
        self.assertTrue(ver.matches(ver2))

    def test_version_str_returns_ver(self):
        ver = Version("0.4.5")
        self.assertEqual("0.4.5", str(ver))

    def test_version_eq_self(self):
        ver = Version("0.4.7")
        self.assertEqual(ver, ver)

    def test_version_eq_other(self):
        ver = Version("0.4.7")
        ver2 = Version("0.4.7")
        self.assertEqual(ver, ver2)

    def test_version_ne_other(self):
        ver = Version("0.4.7")
        ver2 = Version("0.4.5")
        self.assertNotEqual(ver, ver2)

    def test_version_ne_different_type(self):
        ver = Version("0.4.5")
        self.assertNotEqual(34, ver)
