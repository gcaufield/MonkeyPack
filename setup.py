"""Setup information for the MonkeyPack Package Manager."""

import pathlib
from setuptools import setup

here = pathlib.Path(__file__).parent

readme = (here / "README.md").read_text()

requires = ["requests>=2.0,<3", "PyGithub~=1.53"]

setup(
    name="mbpkg",
    version="1.2.1",
    description="Connect IQ Package Manager",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Greg Caufield",
    author_email="greg@embeddedcoffee.ca",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="garmin connectiq packages",
    url="https://github.com/gcaufield/MonkeyPack",
    project_urls={
        "Source": "https://github.com/gcaufield/MonkeyPack.git",
        "Tracker": "https://github.com/gcaufield/MonkeyPack/issues",
    },
    packages=["mbget"],
    python_requires=">=3.5.*, < 4",
    install_requires=requires,
    entry_points={"console_scripts": ["mbget=mbget.main:main"]},
)
