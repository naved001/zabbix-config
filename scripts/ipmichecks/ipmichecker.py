
#! /bin/python

"""
This script runs ipmitool to get sensor information, and will return a list of
tuples (IPMI_ADDRESS, SENSOR_NAME) if there's a problem with a sensor otherwise
it will simply return 'OK'.

This is written because zabbix's ipmi checks can only get the Sensor value and
not the status. With this script, we don't have to worry about creating custom
triggers for everything.
"""

import subprocess
import json
import sys
import re

from multiprocessing import Pool

# Name of file with list of IPMI ips
IP_LIST = "/etc/zabbix/iplist.txt"

# Statuses to ignore regardless of the sensor type
good_statuses = ['ok', 'na', 'ns']

user = "user"
password = "password"

def get_status(hostip):
    """
    Run the ipmitool command to get sensor outputs
    """

    command = 'ipmitool -I lanplus sdr -H ' + hostip + ' -U ' + user + ' -P ' + password
    proc = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    output = filter(None, output.split("\n"))
    problems = []

    for row in output:
        temp = row.split("|")
        sensor = temp[0].strip()
        status = temp[2].strip()

        if status in good_statuses:
            continue
        problems.append(sensor)

    if problems != []:
        return {hostip: problems}

with open(IP_LIST) as file:
    raw_ipmi_ip_list = filter(None, file.read().split("\n"))
    ipmi_ip_list = [ip for ip in raw_ipmi_ip_list if not ip.startswith("#")]

p = Pool(5)
output = filter(None, p.map(get_status, ipmi_ip_list))
allproblems = {}
for item in output:
    allproblems.update(item)
sys.stdout.write(json.dumps(allproblems, indent=4))
