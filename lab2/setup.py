from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="jsccf",
    packages=["jsccf"],
    entry_points={
        "console_scripts": ['jsccf = jsccf.jsccf:main']
    },
    version='0.0.1',
    description="Renaming and documenting tool for JavaScript",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Sergei Yarema",
    author_email="isara.isara8@gmail.com",
    url="https://github.com/SergySanJj/metaprogramming/tree/lab2/lab2",
)
