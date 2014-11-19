# Copyright (c) 2014, Alcides Viamontes Esquivel
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list
# of conditions and the following disclaimer in the documentation and/or other materials
#    provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used
#    to endorse or promote products derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from __future__ import print_function

import sys
import argparse


if sys.version_info[0] < 3:
    print('I require python 3 to run', file=sys.stderr)
    exit(3)


class TestPlan(object):
    """
    Simple class that  really does almost everything...
    """

    def __init__(self,
                 name,
                 thread_count,
                 rampup_time,
                 urls
    ):
        # Make these fields public...
        self.name = name
        self.thread_count = thread_count
        self.rampup_time = rampup_time
        self.urls = urls

    @staticmethod
    def parse_jmx(jmx_file):
        """
        Parses a jmx file and get this class attributes from there

        Example:

        >>> print(TestPlan.parse_jmx( open('test_data/Jmetertestplan.xml') ))
        Name: My test plan
        Thread count: 50
        Ramp-up time: 60.0
        Urls:
            GET test.loadimpact.com/
            GET test.loadimpact.com/news.php
            GET test.loadimpact.com/
            GET test.loadimpact.com/flip_coin.php
            GET test.loadimpact.com/flip_coin.php
        """
        from lxml import etree

        tree = etree.parse(jmx_file)

        name = tree.xpath('//TestPlan')[0].get('testname')
        thread_count = int(tree.xpath('//stringProp[@name="ThreadGroup.num_threads"]')[0].text)
        rampup_time = float(tree.xpath('//stringProp[@name="ThreadGroup.ramp_time"]')[0].text)
        urls = list(TestPlan._obtain_urls(tree))

        return TestPlan(name, thread_count, rampup_time, urls)

    @staticmethod
    def _obtain_urls(tree):
        domain = tree.xpath('//ConfigTestElement//stringProp[@name="HTTPSampler.domain"]')[0].text
        for e in tree.xpath('//HTTPSamplerProxy//stringProp[@name="HTTPSampler.path"]'):
            rl = e.text
            method = e.getnext().text
            yield (domain, rl, method)

    def __str__(self):
        return \
"""Name: {name}
Thread count: {thread_count}
Ramp-up time: {rampup_time}
Urls:
{urls}"""        .format(
            name=self.name,
            thread_count=self.thread_count,
            rampup_time=self.rampup_time,
            urls=
                  '\n'.join(
                     ("    " + method + " " + domain + rl) for (domain, rl, method) in self.urls
                  )
            )


def main():
    parser = argparse.ArgumentParser(
        description='Register jmx file in LoadImpact PaaS'
    )
    parser.add_argument('jmx', metavar='JMX', type=argparse.FileType(),
                        help='The file to read and processs')

    args = parser.parse_args()
    test_plan = TestPlan.parse_jmx(args.jmx)


if __name__ == '__main__':
    main()

