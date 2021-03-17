# Kolla ansible podman installation guide

***

### Install instructions
The whole kolla-ansible install process is described [here](https://docs.openstack.org/kolla-ansible/latest/user/quickstart.html), but in these steps below you should be able to install it aswell.

##### Install dependencies:
```
> sudo dnf install python3-devel libffi-devel gcc openssl-devel python3-libselinux
> sudo dnf install python3-pip, ansible
```

##### Download repositories:
```
> git clone https://github.com/openstack/kolla
> git clone https://github.com/openstack/kolla_ansible_podman EDIT ❗
```

##### Install for kolla and kolla_ansible development
```
> pip install ./kolla
> pip install ./kolla_ansible_podman ❗
```

##### Create config files
```
> sudo mkdir -p /etc/kolla
> sudo chown $USER:$USER /etc/kolla
> cp -r kolla_ansible_podman/etc/kolla/* /etc/kolla
```
in `/etc/kolla/globals.yml` is switch `kolla_container_engine: "podman"` where you can switch between these docker engine

##### Generate passwords
```
> cd kolla-ansible/tools
> ./generate_passwords.py
```
file `/etc/kolla/passwords.yml` with passwords will be created

##### Set network
In `/etc/kolla/globals.yml`:
* uncomment line `# kolla_internal_vip_address: "XXX.XXX.XXX.XX"` and set ip address
* set `network_interface: "XXX"`
* set `neutron_external_interface: "ens4"`
* set `neutron_plugin_agent: "linuxbridge"`

##### Pull and deploy openstack
Pulling images may take a while (aprox. 30min).

```
> kolla-ansible -i ./all-in-one bootstrap-servers
> kolla-ansible -i ./all-in-one prechecks
> kolla-ansible -i ./all-in-one pull
> kolla-ansible -i ./all-in-one deploy 
```

***

### Podman engine


##### Kolla ansible structure
In structure is an overview of kolla-ansible structure with main parts.
The idea of adding podman functionality is in finding a switch task, where based on **kolla_container_engine** variable, will be used either docker or podman task

```
📦kolla_ansible_podman
 ┣ 📂ansible
 ┃ ┣ 📂action_plugins
 ┃ ┣ 📂filter_plugins
 ┃ ┣ 📂group_vars
 ┃ ┣ 📂inventory
 ┃ ┣ 📂library
 ┃ ┃ ┣ 📜kolla_container_facts.py
 ┃ ┃ ┣ 📜kolla_container_facts_podman.py ⚠️**ADDED**
 ┃ ┃ ┣ 📜kolla_toolbox.py
 ┃ ┃ ┣ 📜kolla_toolbox_podman.py ⚠️ **ADDED**
 ┃ ┃ ┣ 📜kolla_docker.py
 ┃ ┃ ┗ 📜...
 ┃ ┣ 📂roles
 ┃ ┃ ┃ ┣ 📂chrony ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┃ ┣ 📂defaults
 ┃ ┃ ┃ ┃ ┣ 📂handlers
 ┃ ┃ ┃ ┃ ┣ 📂tasks
 ┃ ┃ ┃ ┃ ┃ ┣ 📜check-containers-podman.yml -> new Podman task 
 ┃ ┃ ┃ ┃ ┃ ┣ 📜check-containers.yml -> original Docker task
 ┃ ┃ ┃ ┃ ┃ ┣ 📜deploy.yml - based on **kolla_container_engine** is importing `check-containers.yml` or `check-containers-podman.yml`
 ┃ ┃ ┃ ┃ ┃ ┗ ...
 ┃ ┃ ┃ ┣ 📂common ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂glance⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂haproxy ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂heat ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂horizon ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂keystone ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂mariadb ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂memcached ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂neutron ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂nova-cell ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂nova ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂placement ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂[podman-container-systemd](https://github.com/ikke-t/podman-container-systemd) ⚠️ **ADDED** 
 ┃ ┃ ┃ ┣ 📂prechecks ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂rabbitmq ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂service-ks-register-podman ⚠️ **ADDED**
 ┃ ┃ ┃ ┣ 📂service-ks-register ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┣ 📂service-rabbitmq-podman⚠️ **ADDED**
 ┃ ┃ ┃ ┣ 📂destroy ⚠️ **MODIFIED**
 ┃ ┃ ┃ ┗ ... 
 ┣ 📂etc
 ┃ ┣ 📂kolla
 ┃ ┃ ┣ 📜globals.yml ⚠️ **MODIFIED** - added variable **kolla_container_engine**
 ┃ ┃ ┗ 📜passwords.yml
 ┣ 📂tools
 ┃ ┣ 📜cleanup-containers
 ┃ ┗ 📜cleanup-containers-podman ⚠️ **ADDED**
 ┗ ... 
 ```

##### Running containers
with `podman ps ` you can see all running container
| Container name | Status |
| ------------- |:-------------:|
| kolla_toolbox | ✔️
| mariadb_clustercheck |✔️
| mariadb | ✔️
| placement_api | ✔️
| glance_api |✔️
| keystone |✔️
| keystone_fernet |✔️
| keystone_ssh |✔️
| keepalived |✔️
| haproxy |  ✔️
| chrony |✔️
| cron |✔️
| fluentd |  ✔️
| rabbitmq |✔️
| memcached | ✔️
| horizon | ✔️
| heat_engine | ✔️
| heat_api_cfn | ✔️
| heat_api | ✔️
| neutron_metadata_agent | ✔️
| neutron_l3_agent |  ✔️
| neutron_dhcp_agent | ✔️
| neutron_linuxbridge_agent | ✔️
| neutron_server | ✔️
| nova_compute | ✔️
| nova_libvirt | ✔️
| nova_ssh | ✔️
| nova_novncproxy | ✔️
| nova_conductor | ✔️
| nova_api | ✔️
| nova_scheduler | ✔️

***

### Todo:
* ##### fix `ansible/library/kolla_toolbox_podman.py`
    * kolla_toolbox_podman module is not sending commands into kolla_toolbox container
        * -> fix and use kolla_toolbox_podman module
    * Original solution using **kolla_toolbox** module
        ```yaml
        - name: Creating Nova cell database
          become: true
          kolla_toolbox:
            module_name: mysql_db
            module_args:
              login_host: "{{ nova_cell_database_address }}"
              login_port: "{{ nova_cell_database_port }}"
              login_user: "{{ nova_cell_database_admin_user }}"
              login_password: "{{ nova_cell_database_admin_password }}"
          name: "{{ nova_cell_database_name }}"
      when:
        - not use_preconfigured_databases | bool
        - inventory_hostname == groups[nova_cell_conductor_group][0]
        ```
    * Our temporarily solution, with executing command on container manually
    (/ansible/roles/nova-cell/tasks/bootstrap_podman.yml)

        ```yaml
        - name: Creating Nova cell database
          become: true
          command: podman exec -t kolla_toolbox /opt/ansible/bin/ansible localhost 
            -m mysql_db
            -a "login_host='{{ nova_cell_database_address }}'
              login_port='{{ nova_cell_database_port }}'
              login_user='{{ nova_cell_database_admin_user }}'
              login_password='{{ nova_cell_database_admin_password }}'
              name='{{ nova_cell_database_name }}'"
          when:
            - not use_preconfigured_databases | bool
            - inventory_hostname == groups[nova_cell_conductor_group][0]
        ```
* ##### need to implement kolla_docker functionality for podman
    * containers.podman.podman_container module can be used 
        * but it is not creating servicefile corretly
        * 
    * write own module kolla_podman which will call podman API
    * Original solution using kolla_docker
    (/ansible/roles/glance/tasks/check-containers.yml)
        ```yaml
        - name: Check glance containers
          become: true
          kolla_docker:
            action: "compare_container"
            common_options: "{{ docker_common_options }}"
            name: "{{ item.value.container_name }}"
            image: "{{ item.value.image }}"
            privileged: "{{ item.value.privileged | default(omit) }}"
            environment: "{{ item.value.environment | default(omit) }}"
            volumes: "{{ item.value.volumes|reject('equalto', '')|list }}"
            dimensions: "{{ item.value.dimensions }}"
            healthcheck: "{{ item.value.healthcheck | default(omit) }}"
          when:
            - item.value.host_in_groups | bool
            - item.value.enabled | bool
          with_dict: "{{ glance_services }}"
          notify:
            - "Restart {{ item.key }} container"
        ```
    * Our temporarily solution, using podman-container-systemd module which is creating service files  (/ansible/roles/glance/tasks/check-containers-podman.yml)
        ```yaml
            - name: Create glance-api service
              vars:
                container_image_list: 
                - "{{ dict_item.value.image }}"
                container_name: "{{ dict_item.value.container_name }}"
                container_run_args: >-
                --label "io.containers.autoupdate=image"
                -v "{{ node_config_directory }}/glance-api/:{{ container_config_directory }}/:ro"
                -v "/etc/localtime:/etc/localtime:ro"
                -v "kolla_logs:/var/log/kolla"
                -v "{{ glance_file_datadir_volume }}:/var/lib/glance/"
                --env  no_proxy="localhost,127.0.0.1"
                --env  http_proxy=""
                --env  https_proxy=""
                --env KOLLA_CONFIG_STRATEGY=COPY_ALWAYS
                --privileged
                --network host
                container_state: running
              include_role:
                name: podman-container-systemd
              when:
                - inventory_hostname in groups[dict_item.value.group]
                - dict_item.value.enabled | bool
                - dict_item.key == "glance-api"
              with_dict: "{{ glance_services }}"
              loop_control:
                loop_var: dict_item
        ```
    * Solution with container.podman.podman_container module which is not creating service files yet.
        ```yaml
            - name: Check glance containers
              become: true
              containers.podman.podman_container:
                name: "{{ item.value.container_name }}"
                image: "{{ item.value.image }}"
                privileged: "{{ item.value.privileged | default(omit) }}"
                environment: 
                  "{{ item.value.environment | default(omit) }}"
                  KOLLA_CONFIG_STRATEGY: "{{ config_strategy }}"
                volumes: "{{ item.value.volumes|reject('equalto', '')|list }}"
                healthcheck: "{{ item.value.healthcheck | default(omit) }}"
                network: "host"
              when:
                - item.value.host_in_groups | bool
                - item.value.enabled | bool
              with_dict: "{{ glance_services }}"
              notify:
                - "Restart {{ item.key }} container"
        ```
* ##### health-checks are skipped

***

### Some useful links

* Podman api: [link](https://docs.podman.io/en/latest/_static/api.html)
    * Podman api documentation might be useful by implementing kolla_podman

* podman-container-systemd: [link](https://github.com/ikke-t/podman-container-systemd)
    * Role sets up the container(s) to be run on a host with help of the systemd, to keep containers enabled and running over reboots.
    
* Podman container Ansible modules: [link](https://galaxy.ansible.com/containers/podman?extIdCarryOver=true&sc_cid=701f2000001OH7YAAW)
    * Some useful ansible modules for podman 
