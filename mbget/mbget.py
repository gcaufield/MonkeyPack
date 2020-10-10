import argparse

from impl.cache import Cache
from impl.config import Config
from impl.manifest import Manifest
from impl.packages import Packages
from impl.project import Project
from impl.update import Update


def update(args):
    config = Config(args)

    manifest = Manifest(args.manifest)
    with open(args.package, 'r') as package_f:
        packages = Packages(package_f)

    cache = Cache(config)
    project = Project(manifest, packages, cache, config)
    updater = Update(project)

    updater.update_project()


def main():
    parser = argparse.ArgumentParser(description='Connect IQ Package Manager')
    parser.add_argument('-t', '--token', nargs=1, help='Github API token for requests')
    parser.add_argument('-m', '--manifest', default='manifest.xml',
                        help='Specify application manifest')
    parser.add_argument('-p', '--package', default='packages.txt',
                        help='Specify the package map text file')
    parser.add_argument('-j', '--jungle', default='barrels.jungle', help='Barrel Jungle file')
    parser.add_argument('-o', '--directory', default='barrels',
                        help='Specify directory to store barrels in')
    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers()
    update_parser = subparsers.add_parser('update', help='Download and update dependencies')
    update_parser.set_defaults(func=update)

    args = parser.parse_args()
    if args.func is not None:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
