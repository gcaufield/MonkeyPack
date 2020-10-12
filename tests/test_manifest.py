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
