#!/usr/bin/env python

from setuptools import setup, find_packages
from hopper.version import VERSION

README = open('README.md').read()

setup(name='Hopper',
      version=VERSION,
      description='Portable Issue Tracker',
      long_description=README,
      author='Nick Reynolds',
      author_email='ndreynolds@gmail.com',
      url='hopperhq.com/hopper',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['markdown', 
                        'pygments', 
                        'dulwich', 
                        'configobj',
                        'docutils',
                        'flask',
                        'sqlalchemy'],
      entry_points={
          'console_scripts': [
              'hpr = hopper.hpr.cli:main'
              ]
          },
      license='MIT'
     )

print """\n\n\
**********************************************
Hopper %s is good to go.

To set this system up to serve issue trackers:
    hpr server-setup

To create a new issue tracker:
    hpr create-tracker [tracker]

To use an existing issue tracker:
    hpr serve
""" % VERSION
