# zabbix-config
Repository for zabbix configuration file and deployment tools.

## How to run the playbook


0. Create a host group called [zabbix-hosts] in your ansible hosts file at `/etc/ansible/hosts` and put
the list of hosts (or host groups) you want to run this playbook against.

1. Run `ansible-playbook install_agent.yaml -u username` to deploy zabbix agent in passive mode (default, preffered).

2. You can specify `--extra-vars "agent_type=active"` to deploy an active zabbix agent, useful when the hosts are behind a NAT.

3. If you choose active agent, make sure to put the preshared at `/etc/zabbix/zabbix_agentd.psk`and make it accesible to zabbix user.

