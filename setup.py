#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="megyr",
    version="0.2.0",
    description="A library for creating scripts to automate MESA and GYRE runs.",
    author="Christopher Wells",
    author_email="cwells2@oswego.edu",
    url="https://github.com/ExcaliburZero/megyr",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["megyr"],
    install_requires=["pandas", "pystache"],
)
