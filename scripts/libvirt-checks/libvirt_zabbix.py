#! /usr/bin/python

"""Perform libvirt checks and package the data for zabbix server."""
import sys
import json
from libvirt_checks import LibvirtConnection

def main():
    """main I guess"""
        libvirtconnection = LibvirtConnection()
    if len(sys.argv) >= 2:
        ret = getattr(libvirtconnection, sys.argv[1])(*sys.argv[2:])
        sys.stdout.write(ret)
    else:
        ret = libvirtconnection.discover_domains()
        sys.stdout.write(ret)


if __name__ == "__main__":
    main()

