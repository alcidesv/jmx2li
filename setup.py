from __future__ import print_function

import sys
from setuptools import setup

# TODO: Make it multi-runtime
if sys.version_info[0] < 3:
    print("I require python 3 to run", file=sys.stderr)
    exit(3)


setup(
    name='jmx2li',
    version='0.1',
    scripts='pysrc/jmx2li.py',

    install_requires=["lxml==3.4.0", "loadimpact>=1.1.0"]
)
