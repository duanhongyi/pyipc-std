import os
import sys
from setuptools import setup, find_packages



here = os.path.abspath(os.path.dirname(__file__))


def read_text(file_path):
    """
    fix the default operating system encoding is not utf8.
    """
    if sys.version_info.major < 3:
        return open(file_path).read()
    return open(file_path, encoding="utf8").read()

README = read_text(os.path.join(here, 'README.md'))
CHANGES = read_text(os.path.join(here, 'CHANGES.txt'))

requires = [
    'nose',
]

setup(
    name='pyipc-std',
    description='a python ipc tools, use std.',
    version='1.1.4',
    author='duanhongyi',
    author_email='duanhyi@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    long_description=README + '\n\n' + CHANGES,
    url='https://github.com/duanhongyi/pyipc-std',
    install_requires=requires,
    platforms='all platform',
    license='BSD',
)
