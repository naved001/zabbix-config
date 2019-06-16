#! /usr/bin/python

"""Perform libvirt checks and package the data for zabbix server."""


import sys
import json
from libvirt_checks import LibvirtConnection
from pyzabbix import ZabbixMetric, ZabbixSender


DOMAIN_KEY = "libvirt.domain.discover"
VNICS_KEY = "libvirt.nic.discover"
VDISKS_KEY = "libvirt.disk.discover"
ZABBIX_HOST =  "naved-ThinkCentre-M92p"


def make_metric(item_id, item_type, parameter, value):
        """returns zabbix metric"""
        key = "libvirt.{}[{},{}]".format(item_type, item_id, parameter)
        return ZabbixMetric(ZABBIX_HOST, key, value)


class ZabbixLibvirt(object):
    """This class uses LibvirtConnection to gather information and then uses
    ZabbixSender to send it to our zabbix server
    """

    def __init__(self, libvirt_uri=None):
        """main I guess"""
        self.conn = LibvirtConnection(libvirt_uri)

    def discover_domains(self):
        """
        Discover domains on the host and return the ZabbixMetric ready
        to be sent.
        """

        domains = self.conn.discover_domains()

        metric_to_send = ZabbixMetric(
            ZABBIX_HOST, DOMAIN_KEY, json.dumps({"data": domains}))

        return metric_to_send

    def discover_all_vnics(self):
        """Discover all nics and return the ZabbixMetric ready to be sent"""

        vnics = self.conn.discover_all_vnics()
        metric_to_send = ZabbixMetric(ZABBIX_HOST, VNICS_KEY, json.dumps({"data": vnics}))

        return metric_to_send

    def discover_all_vdisks(self):
        """Discover all nics and return the ZabbixMetric ready to be sent"""

        vdisks = self.conn.discover_all_vdisks()
        metric_to_send = ZabbixMetric(ZABBIX_HOST, VDISKS_KEY, json.dumps({"data": vdisks}))
        return metric_to_send


    def _cpu_usage_metric(self):
        """Get CPU usage and create ZabbixMetric to send"""
        domains = self.conn.discover_domains()
        metrics = []

        for domain in domains:
            domain_uuid = domain["{#DOMAINUUID}"]
            stats = self.conn.get_cpu(domain_uuid)

            cpu_time = make_metric(domain_uuid, "cpu", "cpu_time", stats["cpu_time"])
            system_time = make_metric(domain_uuid, "cpu", "system_time", stats["system_time"])
            user_time = make_metric(domain_uuid, "cpu", "user_time", stats["user_time"])

            metrics.extend([cpu_time, system_time, user_time])

        return metrics

    def _memory_usage_metric(self):
        """Get memory usage and create ZabbixMetric to send"""
        domains = self.conn.discover_domains()
        metrics = []

        for domain in domains:

            domain_uuid = domain["{#DOMAINUUID}"]
            stats = self.conn.get_memory(domain_uuid)

            free = make_metric(domain_uuid, "memory", "free", stats["free"])
            available = make_metric(domain_uuid, "memory", "available", stats["available"])
            current_allocation = make_metric(domain_uuid, "memory", "current_allocation", stats["current_allocation"])

            metrics.extend([free, available, current_allocation])

        return metrics

    def _ifaceio_metric(self):
        """Get interface usage metrics"""
        vnics = self.conn.discover_all_vnics()
        metrics = []

        for vnic in vnics:
            domain_uuid = vnic["{#DOMAINUUID}"]
            iface = vnic["{#VNIC}"]
            stats = self.conn.get_ifaceio(domain_uuid, iface)

            item_id = domain_uuid + "," + iface

            read = make_metric(item_id, "nic", "read", stats["read"])
            write = make_metric(item_id, "nic", "write", stats["write"])

            metrics.extend([read, write])
        return metrics

    def _diskio_metric(self):
        """Get interface usage metrics"""
        vdisks = self.conn.discover_all_vdisks()
        metrics = []

        for vdisk in vdisks:
            domain_uuid = vdisk["{#DOMAINUUID}"]
            vdrive = vdisk["{#VDISK}"]
            stats = self.conn.get_diskio(domain_uuid, vdrive)
            stat_types = stats.keys()

            item_id = domain_uuid + "," + vdrive

            for stat_type in stat_types:
                metric = make_metric(item_id, "disk", stat_type, stats[stat_type])
                metrics.append(metric)

        return metrics

    def _all_metrics(self):
        """Send all metrics"""
        metrics = []
        metrics = self._cpu_usage_metric()
        metrics.extend(self._memory_usage_metric())
        metrics.extend(self._ifaceio_metric())
        metrics.extend(self._diskio_metric())
        return metrics


def main():
    """main I guess"""

    zbxlibvirt = ZabbixLibvirt()

    zabbix_sender = ZabbixSender("zabbix.massopen.cloud")

    zabbix_sender.send([zbxlibvirt.discover_domains()])
    zabbix_sender.send([zbxlibvirt.discover_all_vnics()])
    zabbix_sender.send([zbxlibvirt.discover_all_vdisks()])
    zabbix_sender.send(zbxlibvirt._all_metrics())

if __name__ == "__main__":
    main()
