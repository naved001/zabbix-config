#! /bin/python

"""
This script finds all drives on a system including drives that are behind a raid controller.
It will ignore drives that are not SMART capable.
"""

import subprocess
import json
import sys


def multi_pipe_command(command):
    """Uses subprocess.Popen to run a command with multiple pipes since using
    Shell=true is discouraged.
    """
    # Notes:
    # Do not put spaces around the pipe.
    # Won't work if you are using pipe for OR in grep.
    commands = command.split("|")
    proc = []
    for x in range(len(commands)):
        cmd_args = commands[x].split(' ')
        if cmd_args[0] == 'cut' and cmd_args[2] == "'" and cmd_args[3] == "'":
            # Becuase I really want to pass a space as a delimiter in cut command.
            cmd_args[2] = ' '
            del(cmd_args[3])
        if x == 0:
            proc.append(subprocess.Popen(cmd_args, stdout=subprocess.PIPE))
        else:
            proc.append(subprocess.Popen(
                cmd_args, stdin=proc[x - 1].stdout, stdout=subprocess.PIPE))
    output = proc[-1].communicate()[0]
    return output


def get_drives():
    """
    This method collects drives in a tuple of the format
    (raid-controller-number, drive-name-on-raid-controller)
    eg; ("/dev/bus/0", "megaraid,3")

    if the drive is directly attached i.e. not behind a raid controller then it's reported as
    ("no-raid", "/dev/sda")

    A list of such tuples is formed and a JSON is returned that zabbix requires for LLD.
    """
    drives = multi_pipe_command(
        "sudo smartctl --scan-open|cut -d ' ' -f 1,3|grep -v scsi|grep -v sat")

    # Do some cleanup.
    drives = drives.split('\n')
    raid_drives_tmp = [drive for drive in drives if drive]
    raid_drives = []
    for drive in raid_drives_tmp:
        raid_drives.append(tuple(drive.split(' ')))

    # This finds block devices that aren't behind a raid controller.
    drives = multi_pipe_command("lsblk -d|cut -d ' ' -f 1")

    # Cleanup, split the output into an array and remove rados block devices and the headers.
    # Also append '/dev/' in front of the device name
    drives = drives.split('\n')
    other_drives_tmp = [
        '/dev/' + drive for drive in drives if drive and drive != "NAME" and "rbd" not in drive]
    other_drives = []
    for drive in other_drives_tmp:
        other_drives.append(('no-raid', drive))

    # With this filter, we get drives that aren't a part of the raid controller.
    drives_not_in_raid = []
    for drive in other_drives:
        try:
            process_smartctl = subprocess.check_output(
                ['sudo', 'smartctl', '-i', drive[1]], shell=False)
            if "device lacks SMART" in process_smartctl:
                continue
            drives_not_in_raid.append(drive)
        except subprocess.CalledProcessError:
            pass

    all_drives = []
    for drive in raid_drives + drives_not_in_raid:
        if '/dev/' in drive[1]:
            serial = multi_pipe_command(
                "sudo smartctl -i " + drive[1] + "|grep -i serial|cut -d : -f 2")
        else:
            serial = multi_pipe_command(
                "sudo smartctl -i " + drive[0] + " -d " + drive[1] + "|grep -i serial|cut -d : -f 2")
        all_drives.append({"{#DRIVENAME}": drive[1], "{#DRIVESERIAL}": serial.strip(
        ), "{#RAIDCONTROLLER}": drive[0]})

    zabbix_output = {}
    zabbix_output["data"] = all_drives

    # print(json.dumps(zabbix_output, sort_keys=True, indent=4, separators=(',', ': ')))
    sys.stdout.write(json.dumps(zabbix_output))
    return


def test_health(drive):
    if '/dev/' in drive[1]:
        health = multi_pipe_command(
            "sudo smartctl -H " + drive[1] + "|grep -i health|cut -d : -f 2")
    else:
        health = multi_pipe_command(
            "sudo smartctl -H " + drive[0] + " -d " + drive[1] + "|grep -i health|cut -d : -f 2")
    sys.stdout.write(health.strip())
    return


if len(sys.argv) == 3:
    test_health((sys.argv[1], sys.argv[2]))
elif len(sys.argv) == 4:
    test_health((sys.argv[1], sys.argv[2] + "," + sys.argv[3]))
else:
    get_drives()
