#! /bin/bash

echo "________________________________________________________________________________"
lscpu |grep -E 'CPU|Thread|Socket|Core|Model name' |grep -vE 'NUMA|grep|On-line|op-mode'
echo "________________________________________________________________________________"
lsblk --nodeps |grep -viE 'loop|name'
echo "________________________________________________________________________________"
echo "Total Memory (including GPU, if available):" `lsmem |grep "Total online" |cut -d : -f 2`
echo "________________________________________________________________________________"
lspci |grep -iE 'ethernet|infiniband' |cut -d ' ' -f 2-20
echo "________________________________________________________________________________"
lspci |grep -iE 'nvidia|amd'|cut -d ' ' -f 2-20
echo "________________________________________________________________________________"