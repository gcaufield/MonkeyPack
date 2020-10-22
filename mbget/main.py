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

import argparse
import logging

from mbget.github_downloader import GithubDownloader
from mbget.cache import Cache
from mbget.config import Config
from mbget.manifest import Manifest
from mbget.packages import Packages
from mbget.project import Project
from mbget.update import Update


def run_update(args):
    config = Config(args)

    manifest = Manifest(config.manifest)
    packages = Packages(config)
    cache = Cache(config)

    project = Project(manifest, packages, cache, config)
    downloader = GithubDownloader(config.token)
    updater = Update(project, downloader)

    updater.update_project()


def main():
    parser = argparse.ArgumentParser(description="Connect IQ Package Manager")
    parser.add_argument("-t", "--token", help="Github API token for requests")
    parser.add_argument("-c", "--config", help="Specify path to config INI")
    parser.add_argument("-m", "--manifest", help="Specify application manifest")
    parser.add_argument("-p", "--package", help="Specify the package map text file")
    parser.add_argument("-j", "--jungle", help="Barrel Jungle file")
    parser.add_argument(
        "-o",
        "--directory",
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
