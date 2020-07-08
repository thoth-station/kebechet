"""This file contains packaging information for kebechet module."""
import os
from setuptools import setup, find_packages
from pathlib import Path


def get_install_requires():  # noqa: D103
    with open("requirements.txt", "r") as requirements_file:
        # TODO: respect hashes in requirements.txt file
        res = requirements_file.readlines()
        return [req.split(" ", maxsplit=1)[0] for req in res if req]


def get_version():  # noqa: D103
    with open(os.path.join("kebechet", "__init__.py")) as f:
        content = f.readlines()

    for line in content:
        if line.startswith("__version__ ="):
            # dirty, remove trailing and leading chars
            return line.split(" = ")[1][1:-2]
    raise ValueError("No version identifier found")


setup(
    name="kebechet",
    entry_points={"console_scripts": ["kebechet=kebechet.cli:cli"]},
    version=get_version(),
    description="Keep your dependencies in your projects fresh and up2date",
    long_description=Path("README.rst").read_text(),
    author="Fridolin Pokorny",
    author_email="fridolin@redhat.com",
    license="GPLv3+",
    packages=find_packages(),
    install_requires=get_install_requires(),
)
