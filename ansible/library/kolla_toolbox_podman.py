from podman import ApiConnection, system, images, containers
from podman.domain import volumes
import json
import six
# Provide a URI path for the libpod service.  In libpod, the URI can be a unix
# domain socket(UDS) or TCP.  The TCP connection has not been implemented in this
# package yet.


    
from ansible.module_utils.basic import AnsibleModule

''' NOT WORKING version '''


def get_podman_client():
    uri = "unix://localhost/var/run/podman/podman.sock"
    return ApiConnection(uri)


def main():
    specs = dict(
        module_name=dict(required=True, type='str'),
        module_args=dict(type='str'),
        module_extra_vars=dict(type='json'),
        api_version=dict(required=False, type='str', default='auto'),
        timeout=dict(required=False, type='int', default=180),
        user=dict(required=False, type='str'),
    )

    module = AnsibleModule(argument_spec=specs)
    client = get_podman_client()
    cmd = gen_commandline(module.params)
    #print(module.params)
    environment = {"ANSIBLE_STDOUT_CALLBACK": "json",
                    "ANSIBLE_LOAD_CALLBACK_PLUGINS": "True"}
    results = exec_create(client,cmd,environment=environment)
    # #print('RESULTS:',results)
    module.exit_json(False)
    

def gen_commandline(params):
    command = ['ansible', 'localhost']
    if params.get('module_name'):
        command.extend(['-m', params.get('module_name')])
    if params.get('module_args'):
        module_args = params.get('module_args')
        module_args = eval(module_args)
        if isinstance(module_args, dict):
            module_args = ' '.join("{}='{}'".format(key, value)
                                   for key, value in module_args.items())
        command.extend(['-a', module_args])
    if params.get('module_extra_vars'):
        extra_vars = params.get('module_extra_vars')
        if isinstance(extra_vars, dict):
            extra_vars = json.dumps(extra_vars)
        command.extend(['--extra-vars', extra_vars])
    return command


def exec_create(client, cmd, container="kolla_toolbox", stdout=True, stderr=True,
                    stdin=False, tty=False, privileged=False, user='',
                    environment=None, workdir=None, detach_keys=None):
 
        #print("AAAAAAAAAAAAAAAAAAAAAAAAAAA")
        #print(cmd)
        #print("AAAAAAAAAAAAAAAAAAAAAAAAAAA")
        if isinstance(cmd, six.string_types):
            cmd = split_command(cmd)
        #print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
        #print(cmd)
        #print("AAAAAAAAAAAAAAAAAAAAAAAAAAA")
        if isinstance(environment, dict):
            environment = format_environment(environment)

        data = {
            'Container': container,
            # 'User': user,
            'Privileged': privileged,
            'Tty': tty,
            'AttachStdin': stdin,
            'AttachStdout': stdout,
            'AttachStderr': stderr,
            'Cmd': ['touch /tmp/test'],
            'Env': environment,
        }

        if workdir is not None:
            data['WorkingDir'] = workdir

        name='kolla_toolbox'
        url = '/containers/{}/exec'.format(client.quote(name))
        #data = data.encode('utf-8')
        print("#########")
        print(data)
        
        #data = json.dumps(data).encode('utf-8')
        # data2 = {}
        # if data is not None and isinstance(data, dict):
        #     for k, v in iter(data.items()):
        #         if v is not None:
        #             data2[k] = v
        # elif data is not None:
        #     data2 = data
        response = client.post(path=url, params=json.dumps(data), headers={'content-type': 'application/json'})
        print("LOOOOOOOOOG{}, {}".format(
            response.__dict__, cmd))
        return True

def dict_iter(d):
    for i in d.items():
        yield(str(i).encode())

def split_command(command):
    if six.PY2 and not isinstance(command, six.binary_type):
        command = command.encode('utf-8')
    return shlex.split(command)

def format_environment(environment):
    def format_env(key, value):
        if value is None:
            return key
        if isinstance(value, six.binary_type):
            value = value.decode('utf-8')

        return u'{key}={value}'.format(key=key, value=value)
    return [format_env(*var) for var in six.iteritems(environment)]

if __name__ == "__main__":
    main()

