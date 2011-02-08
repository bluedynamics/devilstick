from setuptools import setup, find_packages
import sys, os

version = '0.9'
shortdesc ="devilstick"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()

setup(name='devilstick',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules'        
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url='http://github.com/bluedynamics/devilstick',
      license='Simplified BSD',
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools', 
          'node',
      ],
      extras_require={
          'test': [
              'interlude',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
