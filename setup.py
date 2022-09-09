"""Setup module."""

from setuptools import setup
import pkg_resources


def get_abs_path(relative):
    """Get absolute path of file."""
    return pkg_resources.resource_filename(__name__, relative)


with open(get_abs_path("README.md"), "r") as _f:
    _long_description = _f.read().strip()

with open(get_abs_path("imaids/VERSION"), "r") as _f:
    __version__ = _f.read().strip()

with open(get_abs_path("requirements.txt"), "r") as _f:
    _requirements = _f.read().strip().split("\n")


setup(
    name='imaids',
    version=__version__,
    author='lnls-ima',
    description='Insertion devices package',
    long_description=_long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lnls-ima/insertion-devices",
    download_url="https://github.com/lnls-ima/insertion-devices",
    license='MIT License',
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
    ],
    packages=['imaids'],
    package_data={
        'imaids': ['presets/*']
    },
    install_requires=_requirements,
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False)
