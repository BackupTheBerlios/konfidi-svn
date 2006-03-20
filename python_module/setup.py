#!/usr/bin/env python

from distutils.core import setup

setup(name='Konfidi',
      version='0.1',
      description='Python package for interacting with Konfidi systems.',
      author='Andrew Schamp',
      author_email='schamp@gmail.com',
      url='http://www.konfidi.org/',
      # for the rest of Konfidi, do something like this?
      # see: http://docs.python.org/dist/dist.html for more.
      #scripts=['scripts/TrustServer'],
      #data_files=[('config', ['cfg/data.cfg']),
      #            ('/etc/init.d', ['init-script'])]
      packages=['Konfidi']
      #package_dir={'Konfidi': 'src/Konfidi'}
      )