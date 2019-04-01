# zabbix-config
Repository for zabbix configuration file and deployment tools.

## How to run the playbook


1. Create a host group called [zabbix-hosts] in your ansible hosts file at `/etc/ansible/hosts` and put
the list of hosts (or host groups) you want to run this playbook against.
 - You can override the host group by specifying `--extra-vars "targets=groupname"`

2. Create`zabbix_agent.psk` in this git repo with the Pre shared key for your zabbix server.

https://www.zabbix.com/documentation/4.0/manual/encryption/using_pre_shared_keys#generating_psk

3. Run `ansible-playbook install_agent.yaml -u username` to deploy zabbix agent.

