# zabbix-config
Repository for zabbix configuration file and deployment tools.

## How to run the playbook


1. Run `ansible-playbook -s install_agent.yaml -u username --extra-vars "hostgroup=<some group> agent_type=<agent-config>"`

Extra vars are:

hostgroup: to specify the hosts via the command line to run the playbook against.
agent_type: So if you want to deploy `generic_passive.conf` configuration file, then specify `agent_type=generic_passive`
