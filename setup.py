from setuptools import setup
import re
import os

def find_version(version_file_path):
    file_path = os.path.abspath(os.path.dirname(__file__))
    version_file_path = os.path.join(file_path, version_file_path)
    version_file = open(version_file_path, "r").read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        print(version_match.group(1))
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

requirements = ['setuptools']

long_description = open('README.md', "r", encoding="utf-8").read()

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11'
    ]

setup(name='panoramacli',
      version=find_version(os.path.join('panoramacli', '__init__.py')),
      description='Panorama CLI',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/aws/aws-panorama-cli',
      author='AWS Panorama',
      license='Apache License 2.0',
      scripts=['panoramacli/panorama-cli'],
      packages=['panoramacli'],
      classifiers=classifiers,
      install_requires=requirements,
      package_data={'panoramacli': ['resources/*']},
      keywords='aws panorama',
      python_requires=">=3.6",
      )