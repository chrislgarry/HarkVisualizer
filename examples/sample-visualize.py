"""
HARK SaaS Sample Script
(c) 2015 Honda Research Institute Japan, Co., Ltd.

Visualize HARK results:
  This script receives the HARK resulsts,
  and visualizes them using matplotlib.

Author: Takeshi Mizumoto
"""

import sys
import time
import json
import pprint

import matplotlib.pyplot as plt

import pyhark.saas

if __name__ == "__main__":
    ## load authorization info.
    conf = json.load(open("auth.json"))

    ## session ID to be visualized.
    sid = sys.argv[1]

    ## construct PyHarkSaaS object
    obj = pyhark.saas.PyHarkSaaS(conf["apikey"], conf["apisec"])

    ## authentiation
    obj.login()

    ## get results
    obj.setSessionID(sid)
    ret = obj.getResults()

    ## plot results
    guids = dict([(g, i) for i, g in enumerate(ret["scene"]["guids"])])
    legended = {}
    colors = "rgbmyk"
    for c in ret["context"]:
        legend = None
        if not c["guid"] in legended.keys():
            legended[c["guid"]] = True
            legend = c["guid"]
        plt.plot([c["startTimeMs"], c["endTimeMs"]],
                   [c["azimuth"], c["azimuth"]],
                   "-" + colors[guids[c["guid"]]],
                   linewidth=3, label=legend)

    plt.ylim([-180, 180])
    plt.yticks(range(-180, 181, 30), range(-180, 181, 30))
    plt.xlabel("Time [ms]")
    plt.ylabel("Azimuth [degree]")
    plt.title(sid)
    plt.legend()
    plt.show()
