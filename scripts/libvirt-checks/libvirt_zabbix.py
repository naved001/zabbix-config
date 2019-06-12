#! /usr/bin/python

"""Perform libvirt checks and package the data for zabbix server."""


import sys
import json
from libvirt_checks import LibvirtConnection
from pyzabbix import ZabbixMetric, ZabbixSender


class ZabbixLibvirt(object):
    """This class uses LibvirtConnection to gather information and then uses
    ZabbixSender to send it to our zabbix server
    """
    DISCOVER_KEY = "libvirt.domain.discover"

    def __init__(self, zabbix_server, zabbix_host, libvirt_uri=None):
        """main I guess"""
        self.zabbix_server = zabbix_server
        self.zabbix_host = zabbix_host
        self.libvirt_connection = LibvirtConnection(libvirt_uri)
        self.zabbix_sender = ZabbixSender(zabbix_server)

    @staticmethod
    def zabbix_key(item_type, domain_uuid, parameter_type):
        """Return the zabbix key for an item"""
        return "libvirt.{}[{},{}]".format(item_type, domain_uuid, parameter_type)

    def send_discoverd_domains(self):
        """Send discoverd items"""
        discovered = self.libvirt_connection.discover_domains()

        metric_to_send = ZabbixMetric(
            self.zabbix_host, self.DISCOVER_KEY, json.dumps(discovered))

        self.zabbix_sender.send([metric_to_send])

    def send_cpu_usage(self):
        """Send the rest of the stuff"""
        domains = self.libvirt_connection.discover_domains()["data"]
        metrics = []

        for domain in domains:

            domain_uuid = domain["{#DOMAINUUID}"]
            cpu_time = self.libvirt_connection.get_cpu(domain_uuid, "cpu_time")
            system_time = self.libvirt_connection.get_cpu(
                domain_uuid, "system_time")
            user_time = self.libvirt_connection.get_cpu(
                domain_uuid, "user_time")

            cpu_time = ZabbixMetric(self.zabbix_host, self.zabbix_key(
                "cpu", domain_uuid, "cpu_time"), cpu_time)
            system_time = ZabbixMetric(self.zabbix_host, self.zabbix_key(
                "cpu", domain_uuid, "system_time"), system_time)
            user_time = ZabbixMetric(self.zabbix_host, self.zabbix_key(
                "cpu", domain_uuid, "system_time"), user_time)

            metrics.extend([cpu_time, system_time, user_time])
        print(metrics)
        self.zabbix_sender.send(metrics)


def main():
    """main I guess"""
    zabbix_server = "zabbix.massopen.cloud"
    zabbix_host = "naved-ThinkCentre-M92p"

    zbxlibvirt = ZabbixLibvirt(zabbix_server, zabbix_host)
    zbxlibvirt.send_discoverd_domains()
    zbxlibvirt.send_cpu_usage()


if __name__ == "__main__":
    main()
