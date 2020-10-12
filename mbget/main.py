import argparse
import logging

from mbget.cache import Cache
from mbget.config import Config
from mbget.manifest import Manifest
from mbget.packages import Packages
from mbget.project import Project
from mbget.update import Update


def run_update(args):
    config = Config(args)

    manifest = Manifest(args.manifest)
    packages = Packages(config)
    cache = Cache(config)

    project = Project(manifest, packages, cache, config)
    updater = Update(project)

    updater.update_project()


def main():
    parser = argparse.ArgumentParser(description="Connect IQ Package Manager")
    parser.add_argument("-t", "--token", nargs=1, help="Github API token for requests")
    parser.add_argument(
        "-m", "--manifest", default="manifest.xml", help="Specify application manifest"
    )
    parser.add_argument(
        "-p",
        "--package",
        default="packages.txt",
        help="Specify the package map text file",
    )
    parser.add_argument(
        "-j", "--jungle", default="barrels.jungle", help="Barrel Jungle file"
    )
    parser.add_argument(
        "-o",
        "--directory",
        default=".mbpkg",
        help="Specify directory to store barrels in",
    )
    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers()
    update_parser = subparsers.add_parser(
        "update", help="Download and update dependencies"
    )
    update_parser.set_defaults(func=run_update)

    args = parser.parse_args()

    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    if args.func is not None:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
