#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup

with open('requirements.txt') as fp:
    install_requires = fp.read()
setup(
    name="upsonic",
    version="0.4.9",
    description="""Magic Cloud Layer""",
    long_description="".join(open("README.md", encoding="utf-8").readlines()),
    long_description_content_type="text/markdown",
    url="https://github.com/Upsonic/Upsonic",
    author="Upsonic",
    author_email="onur.atakan.ulusoy@upsonic.co",
    license="MIT",
    packages=["upsonic", "upsonic.remote"],
    install_requires=install_requires,
    python_requires=">= 3",
    zip_safe=False,
)

