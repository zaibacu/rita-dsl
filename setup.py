# coding: UTF-8
from setuptools import setup, find_packages

try:
    from pip._internal.req import parse_requirements
except:
    from pip.req import parse_requirements

from rita import get_version


install_reqs = list(parse_requirements("requirements/main.txt", session={}))
test_reqs = list(parse_requirements("requirements/test.txt", session={}))

with open("README.md", "r") as f:
    desc = f.read()

with open("CHANGELOG.md", "r") as f:
    desc += "## Changelog\n" + f.read()

setup(
    name="rita-dsl",
    version=get_version(),
    long_description=desc,
    long_description_content_type="text/markdown",
    description="DSL for building language rules",
    url="https://github.com/zaibacu/rita-dsl",
    author="Šarūnas Navickas",
    author_email="zaibacu@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[str(ir.req) for ir in install_reqs],
    test_suite="pytest",
    tests_require=[str(tr.req) for tr in test_reqs],
    setup_requires=["pytest-runner"],
    entry_points={"console_scripts": ["rita = rita.run:main"]},
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
