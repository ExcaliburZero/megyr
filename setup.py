#!/usr/bin/env python

from distutils.core import setup

setup(
    name="Megyr",
    version="0.2.0",
    description="Library for creating sccripts to automate MESA and GYRE runs.",
    author="Christopher Wells",
    author_email="cwells2@oswego.edu",
    url="",
    packages=["megyr"],
    install_requires=["pandas", "pystache"],
)
