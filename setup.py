from setuptools import setup, find_packages

setup(name="dwca-writer",
      version="0.0.6",
      author="Pieter Provoost",
      author_email="pieterprovoost@gmail.com",
      description="Python package for writing Darwin Core Archives (DwC-A)",
      license="MIT",
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      package_data={"dwcawriter": ["data/**/*"]},
)
