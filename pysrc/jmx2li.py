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

import loadimpact

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

        self.domains = set(domain for domain, rl, method in urls)

    @classmethod
    def parse_jmx(cls, jmx_file):
        """
        Parses a jmx file and get this class attributes from there

        Example:

        >>> print(TestPlan.parse_jmx( open('test_data/Jmetertestplan.xml') ))
        Name: My test plan
        Thread count: 50
        Ramp-up time: 60
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
        rampup_time = int(tree.xpath('//stringProp[@name="ThreadGroup.ramp_time"]')[0].text)
        urls = list(cls._obtain_urls(tree))

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

    def to_lua(self):
        """Express the case as a lua script

        Example:

        >>> test_plan = TestPlan.parse_jmx( open('test_data/Jmetertestplan.xml') )
        >>> print(test_plan.to_lua())
        http.request_batch({
            {"GET", "test.loadimpact.com/"},{"GET", "test.loadimpact.com/news.php"},{"GET", "test.loadimpact.com/"},{"GET", "test.loadimpact.com/flip_coin.php"},{"GET", "test.loadimpact.com/flip_coin.php"}
        })
        """
        return """http.request_batch({{
    {operations}
}})""".format(
            operations=
              ','.join(
                    '{{"{method}", "{url}"}}'.format(
                        method=method,
                        url=domain + rl
                    ) for (domain, rl, method) in self.urls
                )
        )

    def install(self, client_instance):
        assert isinstance(client_instance, loadimpact.clients.Client)
        from loadimpact import LoadZone
        # Let's register the user scenario...
        user_scenario = client_instance.create_user_scenario({
            'name': self.name,
            'load_script': self.to_lua()
        })
        print('User scenario id: ', user_scenario)
        # And let's create a test...
        url_to_use = 'http://' + (
            '' if len(self.domains) == 0 else (next(iter(self.domains)) + '/'))
        config = client_instance.create_test_config({
            'name': self.name,
            'url': url_to_use,
            'config': {
                'load_schedule':
                    [{
                        'users': self.thread_count,
                        'duration': self.rampup_time,
                    }],
                'tracks':
                    [{
                        'clips': [{
                            'user_scenario_id': user_scenario.id,
                            'percent': 100
                        }],
                    }],
                'loadzone': LoadZone.AMAZON_US_ASHBURN
            }
        })
        print('Configuration id: ', config.id)

# Make the configuration in this variable global to the script
args = None


def main():
    global args
    parser = argparse.ArgumentParser(
        description='Register jmx file in LoadImpact PaaS'
    )
    parser.add_argument('jmx', metavar='JMX', type=argparse.FileType(),
                        help='The file to read and processs')
    parser.add_argument('--api-token', '-k', type=str,
                        default=None,
                        help='Api key... (uses environment var otherwise)')

    args = parser.parse_args()
    test_plan = TestPlan.parse_jmx(args.jmx)

    li_client = loadimpact.ApiTokenClient(api_token=args.api_token)
    test_plan.install(li_client)


if __name__ == '__main__':
    main()

