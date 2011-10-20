#!/usr/bin/env python

from setuptools import setup, find_packages

readme = open('README.md').read()

setup(name='Hopper',
      version='1.0',
      description='Distributed Issue Tracking',
      long_description=readme,
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
                        'docutils'],
      entry_points={
          'console_scripts': [
              'hpr = hopper.hpr.hpr:main'
              ]
          },
      license='MIT'
     )
