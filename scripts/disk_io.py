#! /bin/python

"""This script will return io stats for drives."""
import sys
import os
import re
import json


# See the field description here: https://www.kernel.org/doc/Documentation/iostats.txt
IOREADS = 0
SECTORS_READ = 2
MS_SPENT_READING = 3
IOWRITES = 4
SECTORS_WRITTEN = 6
MS_SPENT_WRITING = 3
BLACKLIST = re.compile(r'md\d+|dm-\d+|sr\d+')


def _get_stats(drive):
    """Gets all stats about a drive"""
    stat_file = "/sys/block/" + drive + "/stat"
    with open(stat_file) as file:
        data = file.read()
    data = [item.strip() for item in data.split()]
    return data


def get_logical_drives():
    """Get all logical drives"""
    block_devices = os.listdir("/sys/block")
    drives = filter(lambda i: not BLACKLIST.match(i), block_devices)
    drives = [{"{#LDRIVE}": drive} for drive in drives]
    sys.stdout.write(json.dumps({"data": drives}))


def get_ioreads(drive):
    """Return ioreads completed"""
    data = _get_stats(drive)
    sys.stdout.write(data[IOREADS])


def get_iowrites(drive):
    """Return iowrites completed"""
    data = _get_stats(drive)
    sys.stdout.write(data[IOWRITES])


def get_bytes_read(drive):
    """Return bytes read"""
    data = _get_stats(drive)
    sys.stdout.write(str(int(data[SECTORS_READ]) * 512))


def get_bytes_written(drive):
    """Return bytes written"""
    data = _get_stats(drive)
    sys.stdout.write(str(int(data[SECTORS_WRITTEN]) * 512))


def get_time_reading(drive):
    """Return miliseconds spent reading"""
    data = _get_stats(drive)
    sys.stdout.write(data[MS_SPENT_READING])


def get_time_writing(drive):
    """Return miliseconds spent writing"""
    data = _get_stats(drive)
    sys.stdout.write(data[MS_SPENT_WRITING])


cmd_dict = {
    "get_ioreads": get_ioreads,
    "get_iowrites": get_iowrites,
    "get_bytes_read": get_bytes_read,
    "get_bytes_written": get_bytes_written,
    "get_time_reading": get_time_reading,
    "get_time_writing": get_time_writing
}

if len(sys.argv) == 3:
    try:
        cmd_dict[sys.argv[1]](sys.argv[2])
    except IOError:
        sys.stdout.write("Device not found: " + sys.argv[2])
    except KeyError:
        sys.stdout.write("Function not found: " + sys.argv[1])
else:
    get_logical_drives()
