
import os
from setuptools import setup


basedir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(basedir, 'VERSION'), 'r') as _f:
    __version__ = _f.read().strip()


setup(
    name='imaids',
    version=__version__,
    description='Insertion devices package',
    author='lnls-ima',
    license='MIT License',
    packages=['imaids'],
    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'openpyxl',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False)
