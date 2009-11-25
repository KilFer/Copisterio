from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='Copisterio',
      version=version,
      description="Copisterio project main daemon",
      long_description="""\
Copisterio is a *content regulation system* for the information-sharing project of the same name _"Copisterio"_.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='It manages free disk space, smartly cleaning it up and provides a content administration system, to filter illegal things.sharing, hacktivism, copisterio, downgrade, hacklab',
      author='Copisterio Work Team',
      author_email='downgrade@gmail.com',
      url='http://sites.google.com/site/copisterioes',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
