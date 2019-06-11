#! /usr/bin/python

"""Perform libvirt checks and package the data for zabbix server."""


import sys
import json
from libvirt_checks import LibvirtConnection
from pyzabbix import ZabbixMetric, ZabbixSender


def main():
    """main I guess"""
    zabbix_server = "zabbix.massopen.cloud"
    zabbix_host = "hostname-in-zabbix"

    libvirtconnection = LibvirtConnection()
    zbx = ZabbixSender(zabbix_server)


    # Main should discover all domains first, and then get all statistics for all domains,
    # create a list of all metrics [(zabbix_host, key, value)...] and then send them.
    if len(sys.argv) >= 2:
        ret = getattr(libvirtconnection, sys.argv[1])(*sys.argv[2:])
        sys.stdout.write(ret)
    else:
        ret = libvirtconnection.discover_domains()
        sys.stdout.write(ret)

def zabbix_key():
    """Return the zabbix key for an item"""


if __name__ == "__main__":
    main()

