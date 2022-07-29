from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name="dwca-writer",
      version="0.0.7",
      author="Pieter Provoost",
      author_email="pieterprovoost@gmail.com",
      description="Python package for writing Darwin Core Archives (DwC-A)",
      long_description=read("README.md"),
      url="https://github.com/pieterprovoost/dwca-writer",
      license="MIT",
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      package_data={"dwcawriter": ["data/**/*"]},
)
