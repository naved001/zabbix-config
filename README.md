# zabbix-config
Repository for zabbix configuration file and deployment tools.

## How to run the playbook


1. Create a host group called [zabbix-hosts] in your ansible hosts file at `/etc/ansible/hosts` and put
the list of hosts (or host groups) you want to run this playbook against.

2. Create`zabbix_agent.psk` in this git repo with the Pre shared key for your zabbix server.

https://www.zabbix.com/documentation/3.0/manual/encryption/using_pre_shared_keys#generating_psk

3. Run `ansible-playbook install_agent.yaml -u username` to deploy zabbix agent in passive mode (default, preffered).

4. You can specify `--extra-vars "agent_type=active"` to deploy an active zabbix agent, useful when the hosts are behind a NAT.

5. If you choose active agent, make sure to put the preshared at `/etc/zabbix/zabbix_agentd.psk`and make it accesible to zabbix user.

