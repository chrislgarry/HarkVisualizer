"""
HARK SaaS Sample Script
(c) 2015 Honda Research Institute Japan, Co., Ltd.

Batch Processing:
  This script sends a given audio file (ogg/flac/wav)
  to HARK SaaS, waits for a processing to be done, 
  and gets the results.

Author: Takeshi Mizumoto
"""

import sys
import time
import json
import pprint

import pyhark.saas

if __name__ == "__main__":
    ## filename to send. ogg, wav and flac are acceptable.
    filename = sys.argv[1]
    print("File Name:" + filename)

    ## load authorization info.
    conf = json.load(open("auth.json"))

    ## construct PyHarkSaaS object 
    obj = pyhark.saas.PyHarkSaaS(conf["apikey"], conf["apisec"])

    ## authentiation
    obj.login()

    ## create a new session with metadata
    metadata = {
        "processType": "batch",
        "params": {
            "numSounds": 2,
            "roomName": "sample room",
            "micName": "dome",
            "thresh": 21
        },
        "sources": [
            {"from": -180, "to": 0},
            {"from": 0, "to": 180},
        ]
    }
    obj.createSession(metadata)
    print("Created session ID: " + obj.getSessionID())

    ## upload a file
    print("Uploading file...")
    obj.uploadFile(open(filename, 'rb'))
    print("Waiting for the process...")
    obj.wait(debug=True)

    ## show results
    ret = obj.getResults()
    pprint.pprint(ret)

