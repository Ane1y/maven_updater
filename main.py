import os
import re
import subprocess
from collections import namedtuple
from typing import List

import config
import utils

PackageInfo = namedtuple('PackageInfo', ['name', 'old_v', 'new_v'])

def get_updates():
    process = subprocess.run(["mvn", "versions:display-dependency-updates"], cwd=config.PATH_TO_PROJECT, capture_output=True,
                             text=True)
    review = process.stdout
    start_str = "newer versions:"
    start_pos = review.find(start_str)
    packages: List[PackageInfo] = []

    if start_pos == -1:
        return packages

    review = review[start_pos + len(start_str):review.find(
        "[INFO] ------------------------------------------------------------------------") - 9].split()
    print(review)
    package = []
    size = 6
    for i in range(1, len(review)):
        if i % size == 1:
            package.append(review[i])
        if i % size == 3:
            package.append(review[i])
        if i % size == 5:
            package.append(review[i])
        if i % size == 0:
            packages.append(PackageInfo._make(package))
            package = []
    packages.append(PackageInfo._make(package))

    return packages


def run_tabby(packages : List[PackageInfo]) :
    tabby_conf = config.PATH_TABBY + "config/settings.properties"
    tabby_conf_mod = tabby_conf + "2"

    for package in packages:
        print(f"start analysing a graph for {package.name} ver.{package.new_v}\n")
        path = utils.get_path(package.name)
        outfile = open(tabby_conf_mod, "w")
        for line in open(tabby_conf, "r"):
            if line.startswith('tabby.build.target'):
                outfile.write(line.replace(line, f'tabby.build.target                        = {config.MAVEN_REPO_PATH}{ "/".join(path)}/{package.new_v}/{path[-1]}-{package.new_v}.jar\n'))  # write in new fil
            else:
                outfile.write(line)
        outfile.close()
        os.rename(tabby_conf_mod, tabby_conf)
        process = subprocess.run(["run.sh"], cwd=config.PATH_TABBY,
                                 capture_output=True,
                                 text=True)
        print(process.stdout)
        return_code = process.returncode

        if return_code != 0:
            print(f"tabby did not build a graph for {package.name} ver.{package.new_v}\n")
        else:
            print(f"tabby built a graph for {package.name} ver.{package.new_v}\n")


def get_json_from_neo4j():
    process = subprocess.run(["cypher-shell", f"-u {config.NEO4J_LOGIN}", f"-p {config.NEO4J_PASSWORD}",
                              f"-a {config.NEO4J_ADDRESS}"],
                             capture_output=True,
                             text=True)


if __name__ == "__main__":
    packages = get_updates()
    print("Packages to update:\n", packages)

    if packages:
        run_tabby(packages)
        print("Retrieving data from neo4j\n")
        get_json_from_neo4j()

