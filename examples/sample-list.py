"""
HARK SaaS Sample Script
(c) 2015 Honda Research Institute Japan, Co., Ltd.

Listup Sessions:
  This script shows all the sessions.

Author: Takeshi Mizumoto
"""

import sys
import json
import pprint

import pyhark.saas

import six
if six.PY2:
    from exceptions import IndexError

if __name__ == "__main__":

    try:
        key = sys.argv[1]
    except IndexError:
        print("usage: python sample-list.py [KEYWORD]")
        key = ""

    ## Load authorization info.
    conf = json.load(open("auth.json"))

    ## Construct PyHarkSaaS Object
    obj = pyhark.saas.PyHarkSaaS(conf["apikey"], conf["apisec"])
 
    ## Authentication
    obj.login()

    ## print all sessions
    pprint.pprint(obj.getSessions(keyword=key))
