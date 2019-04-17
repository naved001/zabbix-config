#! /bin/python

"""This script finds all drives on a system including drives that are behind a raid controller.
It will ignore drives that are not SMART capable
"""

import subprocess
import json
import sys


def multi_pipe_command(command):
    """Uses subprocess.Popen to run a command with multiple pipes since using
    Shell=true is discouraged.
    """
    # Notes:
    # Do not put spaces around the pipe.the
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
            proc.append(subprocess.Popen(cmd_args, stdin=proc[x-1].stdout, stdout=subprocess.PIPE))
    output = proc[-1].communicate()[0]
    return output

def get_drives():
	drives = multi_pipe_command("sudo smartctl --scan-open|cut -d ' ' -f 1-3|grep -v #|cut -d ' ' -f 3")

	# Do some cleanup. Get rid of the words scsi and sat, since drives attached that way
	# will be discovered separately.
	drives = drives.split('\n')
	raid_drives = [drive for drive in drives if drive and drive!="scsi" and drive!="sat"]

	# This finds block devices that aren't behind a raid controller.
	drives = multi_pipe_command("lsblk -d|cut -d ' ' -f 1")

	# Cleanup, split the output into an array and remove rados block devices and the headers.
	# Also append '/dev/' in front of the device name
	drives=drives.split('\n')
	other_drives = ['/dev/'+drive for drive in drives if drive and drive!="NAME" and "rbd" not in drive]


	# With this filter, we get drives that aren't a part of the raid controller.
	drives_not_in_raid = []
	for drive in other_drives:
	    try:
	        process_smartctl = subprocess.check_output(['sudo', 'smartctl', '-i', drive],shell=False)
	        if "device lacks SMART" in process_smartctl:
	            continue
	        drives_not_in_raid.append(drive)
	    except subprocess.CalledProcessError:
	        pass

	all_drives = []
	for drive in raid_drives + drives_not_in_raid:
	    if '/dev/' in drive:
	        serial = multi_pipe_command("sudo smartctl -i " + drive + "|grep -i serial|cut -d : -f 2")
	    else:
	        serial = multi_pipe_command("sudo smartctl -i /dev/bus/0 -d " + drive + "|grep -i serial|cut -d : -f 2")
	    all_drives.append({"{#DRIVENAME}": drive, "{#DRIVESERIAL}": serial.strip()})

	zabbix_output = {}
	zabbix_output["data"] = all_drives

	#print(json.dumps(zabbix_output, sort_keys=True, indent=4, separators=(',', ': ')))
	sys.stdout.write(json.dumps(zabbix_output))
	return

def test_health(drive):
	health = multi_pipe_command("sudo smartctl -H " + drive + "|grep -i health|cut -d : -f 2")
	sys.stdout.write(health.strip())
	return

if len(sys.argv) > 1:
	test_health(sys.argv[1])
else:
	get_drives()
