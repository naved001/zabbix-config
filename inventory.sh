#! /bin/bash

echo "________________________________________________________________________________________________________"
echo CPU info:
lscpu |grep -E 'CPU|Thread|Socket|Core|Model name' |grep -vE 'NUMA|grep|On-line|op-mode'
echo "________________________________________________________________________________________________________"
echo Storage info:
lsblk --nodeps |grep -viE 'loop|name'
echo "________________________________________________________________________________________________________"
echo RAM info:
echo "Total Memory (including GPU, if available):" `lsmem |grep "Total online" |cut -d : -f 2`
dmidecode 2>/dev/null | grep -A3 DDR |head -n3
echo "________________________________________________________________________________________________________"
echo NIC info:
lspci |grep -iE 'ethernet|infiniband' |cut -d ' ' -f 2-20
echo "________________________________________________________________________________________________________"
echo GPU info:
lspci |grep -iE 'nvidia|amd'|cut -d ' ' -f 2-20
echo "________________________________________________________________________________________________________"
