
## Translating .jmx files to Load Impact PaaS. 

This script does just that. Usage instructions:

    $ jmx2li.py --help
    usage: jmx2li.py [-h] [--api-token API_TOKEN] JMX

    Register jmx file in LoadImpact PaaS

    positional arguments:
      JMX                   The file to read and processs

    optional arguments:
      -h, --help            show this help message and exit
      --api-token API_TOKEN, -k API_TOKEN
                            Api key... (uses environment var otherwise)

All in all, this is how you would run it:

    $ jmx2li.py -k API_KEY test_data/Jmetertestplan.xml

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
