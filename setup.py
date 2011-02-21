"""Akhet installation script.
"""
import os

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.txt")).read()
CHANGES = open(os.path.join(here, "CHANGES.txt")).read()

requires = [
    "pyramid", 
    ]

entry_points = """
    [paste.paster_create_template]
    pyramid_sqla=pyramid_sqla.paster_templates:PyramidSQLAProjectTemplate
"""

setup(name="pyramid_sqla",
      version="1.0rc1",
      description="A SQLAlchemy library and Pylons-like application template for Pyramid",
      long_description=README + "\n\n" +  CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pylons",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        ],
      keywords="web wsgi pylons pyramid",
      author="Mike Orr",
      author_email="sluggoster@gmail.com",
      url="http://docs.pylonshq.com",
      license="MIT",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      tests_require = requires,
      install_requires = requires,
      test_suite="pyramid_sqla",
      entry_points=entry_points,
      )

