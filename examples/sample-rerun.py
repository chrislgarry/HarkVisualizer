"""
HARK SaaS Sample Script
(c) 2015 Honda Research Institute Japan, Co., Ltd.

Resun Session:
  This script reruns a given session.

Author: Takeshi Mizumoto
"""

import sys
import time
import json
import pprint
import pyhark.saas

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("usage: python sample-rerun.py [SESSION_ID]")
        sys.exit(1)
    sid = sys.argv[1]

    ## load authorization info.
    conf = json.load(open("auth.json"))

    ## construct PyHarkSaaS object 
    obj = pyhark.saas.PyHarkSaaS(conf["apikey"], conf["apisec"])

    ## authentiation
    obj.login()

    ## create a new session with metadata
    metadata = {
        "processType": "rerun_POST",
        "sources": [
            {"from": -150, "to": 0},
            {"from": 0, "to": 180},
        ]
    }

    obj.setSessionID(sid)

    ## update metadata
    obj.updateMetadata(metadata)


    ## waiting for process finish
    obj.wait(debug=True)

    ## show results
    ret = obj.getResults()
    pprint.pprint(ret)
