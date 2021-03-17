#!/usr/bin/env python3
from ansible.module_utils.basic import AnsibleModule
from podman import ApiConnection, containers
''' Replacement for kolla_container_facts.py, while building openstack on podman.
    Using podman-py pip module from https://github.com/containers/podman-py '''

def get_podman_client():
    uri = "unix://localhost/var/run/podman/podman.sock"
    return ApiConnection(uri)


def main():
    argument_spec = dict(
        name=dict(required=False, type='list', default=[]),
        api_version=dict(required=False, type='str', default='auto')
    )

    module = AnsibleModule(argument_spec=argument_spec)
    results = dict(changed=False, _containers=[])
    client = get_podman_client()
    containersList = containers.list_containers(client)
    names = module.params.get('name')
    if names and not isinstance(names, list):
        names = [names]
    for container in containersList:
        for container_name in container['Names']:
            if names and container_name not in names:
                continue
            results['_containers'].append(container)
            results[container_name] = container
    module.exit_json(**results)
    print(results)


if __name__ == "__main__":
    main()

