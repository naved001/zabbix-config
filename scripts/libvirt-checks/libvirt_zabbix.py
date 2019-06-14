#! /usr/bin/python

"""Perform libvirt checks and package the data for zabbix server."""


import sys
import json
import pprint
from libvirt_checks import LibvirtConnection
from pyzabbix import ZabbixMetric, ZabbixSender


class ZabbixLibvirt(object):
    """This class uses LibvirtConnection to gather information and then uses
    ZabbixSender to send it to our zabbix server
    """
    DOMAIN_KEY = "libvirt.domain.discover"
    VNICS_KEY = "libvirt.nic.discover"

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

        domains = self.libvirt_connection.discover_domains()

        metric_to_send = ZabbixMetric(
            self.zabbix_host, self.DOMAIN_KEY, json.dumps(domains))

        self.zabbix_sender.send([metric_to_send])

        domains = domains["data"]

        # Discover vnics
        all_vnics = []
        for domain in domains:
            domain_uuid = domain["{#DOMAINUUID}"]
            all_vnics.extend(self.libvirt_connection.discover_vnics(domain_uuid)["data"])

        metric_to_send = ZabbixMetric(self.zabbix_host, self.VNICS_KEY, json.dumps({"data": all_vnics}))
        pprint.pprint(metric_to_send)
        self.zabbix_sender.send([metric_to_send])
        print("END OF DISCOVERY")


    def _cpu_usage_metric(self):
        """Get CPU usage and create ZabbixMetric to send"""
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
                "cpu", domain_uuid, "user_time"), user_time)

            metrics.extend([cpu_time, system_time, user_time])

        return metrics

    def _memory_usage_metric(self):
        """Get memory usage and create ZabbixMetric to send"""
        domains = self.libvirt_connection.discover_domains()["data"]
        metrics = []

        for domain in domains:

            domain_uuid = domain["{#DOMAINUUID}"]

            free = self.libvirt_connection.get_memory(domain_uuid, "free")
            available = self.libvirt_connection.get_memory(
                domain_uuid, "available")
            current_allocation = self.libvirt_connection.get_memory(
                domain_uuid, "current_allocation")

            free = ZabbixMetric(self.zabbix_host, self.zabbix_key(
                "memory", domain_uuid, "free"), free)
            available = ZabbixMetric(self.zabbix_host, self.zabbix_key(
                "memory", domain_uuid, "available"), available)
            current_allocation = ZabbixMetric(self.zabbix_host, self.zabbix_key(
                "memory", domain_uuid, "current_allocation"), current_allocation)

            metrics.extend([free, available, current_allocation])

        return metrics

    def _ifaceio_metric(self):
        """Get interface usage metrics"""
        domains = self.libvirt_connection.discover_domains()["data"]
        interfaces = []
        for domain in domains:
            interfaces.extend(self.libvirt_connection.discover_vnics(domain["{#DOMAINUUID}"])["data"])

        metrics = []
        for interface in interfaces:
            domain_uuid = interface["{#DOMAINUUID}"]
            iface = interface["{#VNIC}"]

            read = self.libvirt_connection.get_ifaceio(domain_uuid, iface, "read")
            write = self.libvirt_connection.get_ifaceio(domain_uuid, iface, "write")

            read_key = "libvirt.nic[{},{},{}]".format(domain_uuid, iface, "read")
            write_key = "libvirt.nic[{},{},{}]".format(domain_uuid, iface, "write")

            read = ZabbixMetric(self.zabbix_host, read_key, read)
            write = ZabbixMetric(self.zabbix_host, write_key, write)

            metrics.extend([read, write])
        print("METRICS FROM IFACEIO")
        print(metrics)
        return metrics



    def _all_metrics(self):
        """Send all metrics"""
        metrics = self._cpu_usage_metric()
        metrics.extend(self._memory_usage_metric())
        metrics.extend(self._ifaceio_metric())
        pprint.pprint(metrics)

        self.zabbix_sender.send(metrics)


def main():
    """main I guess"""
    zabbix_server = "zabbix.massopen.cloud"
    zabbix_host = "naved-ThinkCentre-M92p"

    zbxlibvirt = ZabbixLibvirt(zabbix_server, zabbix_host)
    zbxlibvirt.send_discoverd_domains()
    zbxlibvirt._all_metrics()


if __name__ == "__main__":
    main()
