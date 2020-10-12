import unittest

from mbget.dependency import Dependency


class TestDependency(unittest.TestCase):

    def test_dependency_name_is_correct(self):
        dep = Dependency("Depend")

        self.assertEqual("Depend", dep.package_name)

    def test_dependency_can_get_version(self):
        dep = Dependency("Depend")
        dep.set_version("1.2.3")

        self.assertEqual("1.2.3", str(dep.version))

    def test_dependency_can_get_repo(self):
        dep = Dependency("Depend")
        dep.set_repo("owner/Depend")

        self.assertEqual("owner/Depend", dep.repo)

    def test_dependency_can_get_barrel_name(self):
        dep = Dependency("Depend")
        dep.set_barrel_name("x.barrel")

        self.assertEqual("x.barrel", dep.barrel_name)

    def test_dependecy_eq_with_self(self):
        dep = Dependency("Depend")
        dep.set_version("1.2.3")
        dep.set_repo("owner/Depend")

        self.assertEqual(dep, dep)

    def test_dependency_eq_with_other(self):
        dep = Dependency("Depend")
        dep.set_version("1.2.3")
        dep.set_repo("owner/Depend")

        dep2 = Dependency("Depend")
        dep2.set_version("1.2.3")
        dep2.set_repo("owner/Depend")

        self.assertEqual(dep, dep2)

    def test_dependency_ne_with_different_version(self):
        dep = Dependency("Depend")
        dep.set_version("1.2.3")
        dep.set_repo("owner/Depend")

        dep2 = Dependency("Depend")
        dep2.set_version("1.2.4")
        dep2.set_repo("owner/Depend")

        self.assertNotEqual(dep, dep2)

    def test_dependency_ne_with_different_package_name(self):
        dep = Dependency("Depend")
        dep.set_version("1.2.3")
        dep.set_repo("owner/Depend")

        dep2 = Dependency("Depend2")
        dep2.set_version("1.2.3")
        dep2.set_repo("owner/Depend")

        self.assertNotEqual(dep, dep2)

    def test_dependency_ne_with_different_repo(self):
        dep = Dependency("Depend")
        dep.set_version("1.2.3")
        dep.set_repo("owner/Depend")

        dep2 = Dependency("Depend")
        dep2.set_version("1.2.3")
        dep2.set_repo("owner2/Depend")

        self.assertNotEqual(dep, dep2)

    def test_dependency_eq_with_different_barrel_name(self):
        dep = Dependency("Depend")
        dep.set_version("1.2.3")
        dep.set_repo("owner/Depend")
        dep.set_barrel_name("x.barrel")

        dep2 = Dependency("Depend")
        dep2.set_version("1.2.3")
        dep2.set_repo("owner/Depend")
        dep.set_barrel_name("y.barrel")

        self.assertEqual(dep, dep2)
