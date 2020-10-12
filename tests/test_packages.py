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
