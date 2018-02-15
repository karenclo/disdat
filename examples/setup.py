from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from setuptools import find_packages, setup

setup(
    name='pipelines',
    version=0.1,
    packages=find_packages(exclude=['config']),
    install_requires=[
        'tensorflow',
        'pandas==0.20.3',
        'luigi',
    ],
)
