#!/bin/bash
export KOLLA_CONFIG_STRATEGY='COPY_ALWAYS'
sudo -E kolla_set_configs && keystone-manage --config-file /etc/keystone/keystone.conf fernet_setup --keystone-user keystone --keystone-group keystone