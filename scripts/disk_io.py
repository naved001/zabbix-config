#! /bin/python

"""
This script finds drive using snmpwalk and collect disk statistics.
"""

import subprocess
import json
import sys
import re

blacklist = re.compile(r'[a-z]+\d+|dm-\d+')

# Constants
COMMUNITY_STRING = ""
BASE_OID  = ".1.3.6.1.4.1.2021.13.15.1.1"
DRIVE_INDICES = BASE_OID + ".1"
DRIVE_LIST = BASE_OID + ".2"
SOME_COUNTER = BASE_OID + ".3"

# Other stuff
test_host = "192.168.47.21"


def _snmpwalk(oid, host=None):
    """runs snmpwalk for you and then returns the output.
    The caller should know what data to expect and cast it as such"""

    if host is None:
        host = "127.0.0.1"

    command = ["snmpwalk", "-v", "2c", "-c", COMMUNITY_STRING, host, oid]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    return output

def get_value(oid, host=None):
    output = _snmpwalk(oid, host).split(":")
    return output[-1].strip()

def discover(oid, host=None):
    output = _snmpwalk(oid, host).splitlines()
    output = [i.split(":", 1)[1].strip().replace('"','') for i in output]
    return output

indices = discover(DRIVE_INDICES, test_host)
drive_names = discover(DRIVE_LIST, test_host)
drives = []

for index, name in zip(indices, drive_names):
    # check drive[1] against a blacklist
    if blacklist.match(name) is not None:
        continue
    drives.append({"{#DRIVEINDEX}": index, "{#DRIVENAME}": name})

zabbix_output = {}
zabbix_output["data"] = drives
# the discovery stuff
print(json.dumps(zabbix_output))

