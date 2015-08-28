from setuptools import setup

setup(name='pybeagle',
      version='0.1',
      description='Beagle Wrapper',
      author='Thomas Dias-Alves',
      packages=['pybeagle'],
      install_requires=[
          'numpy',
          'pandas'
      ],
      test_suite='pybeagle.test',
      zip_safe=False)
