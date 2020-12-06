import re
from setuptools import setup

version = re.search(
    r'^__version__\s*=\s*"(.*)"',
    open('jsccf/jsccf.py').read()
).group(1)

with open("Readme.md", "rb") as f:
    long_description = f.read().decode("utf-8")

setup(
    name="jsccf",
    packages=["jsccf"],
    entry_points={
        "console_scripts": ['jsccf = jsccf.jsccf:main']
    },
    version=version,
    description="Renaming and documenting tool for JavaScript",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Sergei Yarema",
    author_email="isara.isara8@gmail.com",
    url="https://github.com/SergySanJj/metaprogramming/tree/lab2/lab2",
)
