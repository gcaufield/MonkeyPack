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
