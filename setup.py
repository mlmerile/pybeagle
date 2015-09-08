from setuptools import setup, find_packages

setup(name='pybeagle',
      version='0.1',
      description='Beagle Wrapper',
      author='Thomas Dias-Alves',
      packages=find_packages(),
      install_requires=[
          'numpy',
          'pandas'
      ],
      test_suite='pybeagle.test',
      zip_safe=False)
