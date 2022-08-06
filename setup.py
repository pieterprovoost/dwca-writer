from setuptools import setup, find_packages


long_description = open("README.md").read()


setup(name="dwca-writer",
      version="0.1.0",
      author="Pieter Provoost",
      author_email="pieterprovoost@gmail.com",
      description="Python package for writing Darwin Core Archives (DwC-A)",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/pieterprovoost/dwca-writer",
      license="MIT",
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      package_data={"dwcawriter": ["data/**/*"], "": ["README.md"]},
)
