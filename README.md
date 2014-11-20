
## Translating .jmx files to Load Impact PaaS. 

This script does just that. Usage instructions:

    $ jmx2li --help


## Pre-requisites

Python 2 is great for maintaining legacy applications. 
But this script has been written for Python 3. 

## Installation

Use the standard pip way on this repository:

    $ pip install git+https://github.com/alcidesv/jmx2li#master

If you want to develop this project, create a virtualenv the usual way and 
install the dependencies...they include ipython, for your API-testing convenience:

    $ virtualenv -p /usr/bin/python3.4 venv
    $ venv/bin/pip install -r dev_helpers/requirements.txt

There are some doctests in the code. You can run them by doing

    $ python -m doctest -v pysrc/jmx2li.py
