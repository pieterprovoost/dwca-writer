from setuptools import setup, find_packages


try:
    import pypandoc
    long_description = pypandoc.convert_file("README.md", "rst")
except(IOError, ImportError):
    long_description = open("README.md").read()


setup(name="dwca-writer",
      version="0.0.8",
      author="Pieter Provoost",
      author_email="pieterprovoost@gmail.com",
      description="Python package for writing Darwin Core Archives (DwC-A)",
      long_description=long_description,
      url="https://github.com/pieterprovoost/dwca-writer",
      license="MIT",
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      package_data={"dwcawriter": ["data/**/*"]},
)
