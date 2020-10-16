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
from io import StringIO

from mbget.manifest import Manifest


class TestManifest(unittest.TestCase):
    @staticmethod
    def __build_fake_manifest(depends: dict) -> str:
        manifest_str = (
            r'<iq:manifest xmlns:iq="http://www.garmin.com/xml/connectiq">'
            r"<iq:application><iq:products/><iq:permissions/><iq:languages/><iq:barrels>"
        )
        for key in depends.keys():
            manifest_str += '<iq:depends name="{name}" version="{version}"/>'.format(
                name=key, version=depends[key]
            )
        return manifest_str + "</iq:barrels></iq:application></iq:manifest>"

    def test_get_depends_returns_single_depends_element(self):
        fake_manifest = StringIO(self.__build_fake_manifest({"TestBarrel": "0.2.5"}))

        manifest = Manifest(fake_manifest)
        depends = manifest.get_depends()

        self.assertEqual(1, len(depends))

    def test_get_depends_returns_correct_depends(self):
        fake_manifest = StringIO(self.__build_fake_manifest({"TestBarrel": "0.2.5"}))

        manifest = Manifest(fake_manifest)
        depends = manifest.get_depends()

        self.assertIn("TestBarrel", depends)

    def test_get_depends_returns_all_dependencies(self):
        fake_manifest = StringIO(
            self.__build_fake_manifest({"TestBarrel": "0.2.5", "OtherBarrel": "0.4.5"})
        )

        manifest = Manifest(fake_manifest)
        depends = manifest.get_depends()

        self.assertEqual(2, len(depends))
        self.assertIn("TestBarrel", depends)
        self.assertIn("OtherBarrel", depends)

    def test_get_required_version_returns_correct_version(self):
        fake_manifest = StringIO(
            self.__build_fake_manifest({"TestBarrel": "0.2.5", "OtherBarrel": "0.4.5"})
        )

        manifest = Manifest(fake_manifest)

        self.assertEqual("0.2.5", manifest.get_required_version("TestBarrel"))
