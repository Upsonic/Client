#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup

with open("requirements.txt") as fp:
    install_requires = fp.read()
setup(
    name="upsonic",
    version="0.30.0",
    description="""Magic Cloud Layer""",
    long_description="".join(open("README.md", encoding="utf-8").readlines()),
    long_description_content_type="text/markdown",
    url="https://github.com/Upsonic/Upsonic",
    author="Upsonic",
    author_email="onur.atakan.ulusoy@upsonic.co",
    license="MIT",
    packages=["upsonic", "upsonic.remote", "upsonic.remote.localimport"],
    install_requires=install_requires,
    entry_points={
        "console_scripts": ["upsonic=upsonic.remote.interface:Upsonic_CLI"],
    },
    python_requires=">= 3",
    zip_safe=False,
)
