from github import Github
import requests
import re
import argparse
import xml.etree.cElementTree as ET
import os
import json
import hashlib

BARREL_FILE = re.compile(r'^.+\.barrel$')


def parse_packages(package_file):
    """
    Parse a map of packages to Github repos out of a provided package map text file

    :param package_file: The package map file
    :return: Dictionary mapping Barrel Dependencies to Github repositories
    """
    package_map = {}
    try:
        with open(package_file, 'r') as f:
            i = 0
            for line in f.readlines():
                i += 1
                line = line.rstrip()
                if len(line) > 0:
                    words = line.split("=>")
                    if len(words) == 2:
                        package_map[words[0].rstrip()] = words[1].rstrip()
                    else:
                        print("Poorly formatted package map on line {line_num}: {line}".format(line_num=i, line=line))
                        return None
    except FileNotFoundError:
        print("Package file '{file}' not found".format(file=package_file))
        return None

    return package_map


def parse_manifest(manifest_file):
    """
    Parse a ConnectIQ Manifest file to access the declared barrel dependencies and versions

    :param manifest_file: Path to the project manifest file
    :return: A map of packages to version expectations
    """
    barrel_map = {}
    ns = {"iq": "http://www.garmin.com/xml/connectiq"}

    tree = ET.ElementTree(file=manifest_file)
    root = tree.getroot()
    if root.tag != "{{{iq}}}manifest".format(iq=ns["iq"]):
        print("Invalid manifest XML provided '{file}'".format(file=manifest_file))
        return None

    for dep in root.findall(".//iq:barrels/iq:depends", namespaces=ns):
        barrel_map[dep.attrib["name"]] = {"version": dep.attrib["version"]}

    return barrel_map


def hash_file(path):
    """

    :param path:
    :return:
    """
    BLOCK_SIZE = 65535
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            h.update(fb)
            fb = f.read(BLOCK_SIZE)

    return h.hexdigest()


def read_cache_file(barrel_dir):
    """

    :param barrel_dir:
    :return:
    """
    cache_file = os.path.join(barrel_dir, '.mbgetcache')

    packages = {}
    cache = None

    try:
        with open(cache_file, 'r') as f:
            cache = json.load(f)
    except (OSError, json.JSONDecodeError):
        # Couldn't open cache
        return None

    return packages


def save_cache_file(barrel_dir, packages):
    """

    :param barrel_dir:
    :param packages:
    :return:
    """
    cache = {}
    for package in packages.keys():
        cache_entry = {}
        cache_entry["tag"] = packages[package]["tag"]
        cache_entry["asset"] = packages[package]["asset"]
        try:
            cache_entry["hash"] = hash_file(packages[package]["asset"])
        except OSError:
            # Something went wrong parsing the cache entry, don't return it
            continue

        cache[package] = cache_entry

    cache_file = os.path.join(barrel_dir, '.mbgetcache')

    # TODO Try/Except
    with open(cache_file, 'w') as f:
        json.dump(cache, f)


def download_dep(dep, data, token, barrel_dir):
    """

    :param dep:
    :param data:
    :param token:
    :param barrel_dir:
    :return:
    """
    print("Get dependency {dep} ({version})".format(dep=dep, version=data["version"]))

    if token is not None:
        github = Github(token[0])
    else:
        github = Github()

    repo = github.get_repo(data["repo"])

    # Search the releases for a version that we can use
    for release in repo.get_releases():
        tag_match = re.compile("^v{version}".format(version=data["version"]))
        if tag_match.match(release.tag_name) is None:
            continue

        # Matching tag download the barrels
        for asset in release.get_assets():
            if BARREL_FILE.match(asset.name) is not None:
                print("Downloading asset {asset} from release {rel}".format(asset=asset.name, rel=release.tag_name))

                # Found a barrel file, Download it.
                headers = {'Accept': 'application/octet-stream'}

                if token is not None:
                    headers['Authorization'] = 'token {token}'.format(token=token[0])

                req = requests.get(asset.url, headers=headers)
                filename = os.path.join(barrel_dir, asset.name)
                with open(filename, 'wb') as f:
                    f.write(req.content)

                # Save the asset name and the release tag
                data["asset"] = filename
                data["tag"] = release.tag_name
                return

        print("No asset available for version {version}".format(version=version))

    print("Unable to find matching version {version}".format(version=version))
    return None


def update_barrel_jungle(file, barrels):
    """

    :param file:
    :param barrels:
    :return:
    """
    barrel_path = "$(base.barrelPath)"
    with open(file, 'w') as f:
        f.write('# Do not hand edit this auto generated file from mbget\n')
        for key in barrels.keys():
            asset = barrels[key]["asset"]
            if asset is None:
                continue
            f.write('{name} = "{asset}"\n'.format(name=key, asset=asset.replace('/', '\\')))
            barrel_path += ";$({name})".format(name=key)
        f.write("base.barrelPath = {barrel_path}".format(barrel_path=barrel_path))


def main():
    parser = argparse.ArgumentParser(description='Connect IQ Package Manager')
    parser.add_argument('-t', '--token', nargs=1, help='Github API token for requests')
    parser.add_argument('-m', '--manifest', default='manifest.xml', help='Specify application manifest')
    parser.add_argument('-p', '--package', default='packages.txt', help='Specify the package map text file')
    parser.add_argument('-j', '--jungle', default='barrels.jungle', help='Barrel Jungle file')
    parser.add_argument('-o', '--directory', default='barrels', help='Specify directory to store barrels in')
    args = parser.parse_args()

    dependencies = parse_manifest(args.manifest)
    if dependencies is None:
        # Invalid manifest
        return

    if len(dependencies) == 0:
        print("No dependencies to download")
        return

    package_map = parse_packages(args.package)
    if package_map is None:
        # Invalid package map... Exit.
        return

    for key in package_map.keys():
        if dependencies[key] is not None:
            dependencies[key]["repo"] = package_map[key]
        # else:
        # TODO warn, unused package in packages.txt

    # Build the args directory if we need it
    if not os.path.exists(args.directory):
        os.mkdir(args.directory)

    for dep in dependencies.keys():
        if dependencies[dep]["repo"] is None:
            print("No package repository defined for '{dep}'".format(dep=dep))
            continue

        download_dep(dep, dependencies[dep], args.token, args.directory)

    update_barrel_jungle(args.jungle, dependencies)
    save_cache_file(args.directory, dependencies)


if __name__ == "__main__":
    main()
