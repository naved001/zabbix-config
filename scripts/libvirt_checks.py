#! /usr/bin/python

import libvirt
import sys
import json
import time
from xml.etree import ElementTree


SLEEP_TIME = 1


class LibvirtConnection(object):
    """This class opens a connection to libvirt and provides with methods
    to get useuful information about domains.
    """

    @staticmethod
    def libvirt_callback(userdata, err):
        pass

    def __init__(self, uri=None):
        """Creates a read only connection to libvirt"""
        self.conn = libvirt.openReadOnly(uri)
        if self.conn == None:
            sys.stdout.write("Failed to open connection to the hypervisor")
            sys.exit(1)

        # We set this because when libvirt errors are raised, they are still
        # printed to console (stderr) even if you catch them.
        # This is a problem with libvirt API.
        # See https://stackoverflow.com/questions/45541725/avoiding-console-prints-by-libvirt-qemu-python-apis
        libvirt.registerErrorHandler(f=self.libvirt_callback, ctx=None)

    def _get_domain(self, domain_uuid_string):
        """Find the domain by uuid and return domain object"""
        domain = self.conn.lookupByUUIDString(domain_uuid_string)
        if domain == None:
            sys.stdout.write("Failed to find domain: " + domain_uuid_string)
            sys.exit(1)
        return domain

    def discover_domains(self):
        """Return all domains"""
        domains = self.conn.listAllDomains()
        domains = [{"{#DOMAINNAME}": domain.name(), "{#DOMAINUUID}": domain.UUIDString()}
                   for domain in domains if domain.isActive()]
        return json.dumps({"data": domains})

    def discover_vnics(self, domain_uuid_string):
        """Discover all virtual networks"""
        domain = self._get_domain(domain_uuid_string)
        tree = ElementTree.fromstring(domain.XMLDesc())
        elements = tree.findall('devices/interface/target')
        interfaces = [{"{#VNIC}": element.get('dev')} for element in elements]
        return json.dumps({"data": interfaces})

    def discover_vdisks(self, domain_uuid_string):
        """Discover all virtual networks"""
        domain = self._get_domain(domain_uuid_string)
        tree = ElementTree.fromstring(domain.XMLDesc())
        elements = tree.findall('devices/disk/target')
        disks = [{"{#VDISKS}": element.get('dev')} for element in elements]
        return json.dumps({"data": disks})

    def get_memory(self, domain_uuid_string, memtype):
        """Get memorystats for domain.

        Here's a mapping of what the output from
        virsh / libvirt means to what is displayed by linux's `free` command.

        available = total
        unused = free
        usable = available
        actual = Current memory allocated to the VM(it's not the same as total in `free` command).

        The API returns the output in KiB, so we multiply by 1024 to return bytes for zabbix.
        """
        domain = self._get_domain(domain_uuid_string)

        try:
            stats = domain.memoryStats()
        except libvirt.libvirtError:
            # If the domain is not running, then the memory usage is 0.
            # If the error is due to other reasons, then re-raise the error.
            if domain.isActive():
                raise
            else:
                return "0"

        try:
            memtype_dict = {"free": stats["unused"] * 1024,
                            "available": stats["usable"] * 1024,
                            "current_allocation": stats["actual"] * 1024}
        except KeyError:
            # If the machine does not have an OS (or booted up), then stats may not contain what
            # we are looking for and a key error will be raised which will make the item
            # unsupported in zabbix. For those cases, we mark memory usage as zero.
            return "0"

        return str(memtype_dict[memtype])

    def get_cpu(self, domain_uuid_string, cputype):
        """Get CPU statistics. Libvirt returns the stats in nanoseconds.
        Returns the overall percent usage.
        """
        domain = self._get_domain(domain_uuid_string)

        try:
            cpustats_1 = domain.getCPUStats(True)
            time.sleep(SLEEP_TIME)
            cpustats_2 = domain.getCPUStats(True)
        except libvirt.libvirtError:
            # If the domain is not running, then the cpu usage is 0.
            # If the error is due to other reasons, then re-raise the error.
            if domain.isActive():
                raise
            else:
                return "0"

        number_of_cpus = domain.info()[3]

        cpustats = {"cpu_time": (cpustats_2[0]['cpu_time'] -
                                 cpustats_1[0]['cpu_time']) / (number_of_cpus * SLEEP_TIME * 10**7),
                    "system_time": (cpustats_2[0]['system_time'] -
                                    cpustats_1[0]['system_time']) / (number_of_cpus * SLEEP_TIME * 10**7),
                    "user_time": (cpustats_2[0]['user_time'] -
                                  cpustats_1[0]['user_time']) / (number_of_cpus * SLEEP_TIME * 10**7)}

        return str(cpustats[cputype])

    def get_ifaceio(self, domain_uuid_string, iface, stat_type):
        """Get Network I / O"""
        domain = self._get_domain(domain_uuid_string)

        try:
            stats = domain.interfaceStats(iface)
        except libvirt.libvirtError:
            if domain.isActive():
                raise
            else:
                return "0"

        if stat_type.lower() == "read":
            return str(stats[0])
        elif stat_type.lower() == "write":
            return str(stats[4])
        else:
            return("Invalid stat_type.")

    def get_diskio(self, domain_uuid_string, disk, stat_type):
        """Get Network I / O"""
        domain = self._get_domain(domain_uuid_string)

        try:
            stats = domain.blockStatsFlags(disk)
        except libvirt.libvirtError:
            if domain.isActive():
                raise
            else:
                return "0"

        return str(stats.get(stat_type, "Invalid stat_type"))

    def is_active(self, domain_uuid_string):
        """Returns 1 if domain is active, 0 otherwise."""
        domain = self._get_domain(domain_uuid_string)
        sys.stdout.write(str(domain.isActive()))


def main():
    """main I guess"""

    libvirtconnection = LibvirtConnection()
    if len(sys.argv) >= 2:
        ret = getattr(libvirtconnection, sys.argv[1])(*sys.argv[2:])
        sys.stdout.write(ret)
    else:
        libvirtconnection.discover_domains()


if __name__ == "__main__":
    main()
