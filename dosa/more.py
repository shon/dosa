import glob
import socket
from os.path import basename


def sync_keys(client):
    local_keys = dict((basename(path), open(path).read())
                      for path in glob.glob('keys/*'))
    registered_keys = dict((key['name'], key)
                           for key in client.keys.list().result['ssh_keys'])
    local_key_names = set(local_keys.keys())
    registered_key_names = set(registered_keys.keys())
    new_key_names = local_key_names.difference(registered_key_names)
    keynames_to_discard = registered_key_names.difference(local_keys)
    for name in new_key_names:
        client.keys.create(name=name, public_key=local_keys[name])
    for name in keynames_to_discard:
        client.keys.delete(registered_keys[name]['id'])
    return {'new': new_key_names, 'deleted': keynames_to_discard,
            'all_ids': [key['id'] for key in registered_keys.values()]}


def test_ssh(host, throw=False):
    """
    test ssh connection to specified `host`
    Useful utility to ensure if newly created instance is sshable
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(1)
        sock.connect((host, 22))
        return True
    except socket.timeout:
        if throw:
            raise
    except socket.error as e:
        if throw or e.errno != 111:
            raise
    finally:
        sock.close()
    return False
