#!/usr/bin/env python

from setuptools import setup, find_packages

readme = open('README.md').read()

setup(name='Hopper',
      version='1.0',
      description='Minimalist Issue Tracker',
      long_description=readme,
      author='Nick Reynolds',
      author_email='ndreynolds@gmail.com',
      url='hopperhq.com/hopper',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['markdown', 'pygments', 'dulwich', 
                        'configobj'],
      license='MIT'
      )
