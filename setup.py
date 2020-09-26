#!/usr/bin/env python

from distutils.core import setup

setup(name='batmeter',
      version='0.1',
      description='Notebook battery logging and plotting utility',
      license="GPLv3",
      author='z3nox',
      author_email='zenox@dukun.de',
      url='https://github.com/Z3NOX/batmeter',
      install_requires=[
          'tinydb>=4.1.1',
          'matplotlib>=3.3.1'
          ],
      scripts=['batmeter'],
     )
