export KOLLA_CONFIG_STRATEGY=COPY_ALWAYS;
sudo -E kolla_set_configs && nova-manage cell_v2 list_cells --verbose;