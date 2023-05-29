import time

from coinhunt import ENV_FILE
from . import client
from coinhunt.cloud.aws import add_record, get_hosted_zone_name
from fabric import Connection
from linode_api4.objects import StackScript
from linode_api4 import Instance
import os

def get_ssh_public_key():
    with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as f:
        return f.read().strip()
    
threads = []

def main():
    auto_id_base = 0
    current_instances = list(filter(
        lambda x: x.label.startswith('coinhunt'),
        client.linode.instances()
    ))
    
    for linode in current_instances:
        print(linode.label, linode.ipv4, linode.status)
        if int(linode.label.split('-')[1]) > auto_id_base:
            auto_id_base = int(linode.label.split('-')[1])

    new_label = 'coinhunter-{}'.format(auto_id_base + 1)

    stackscript = StackScript(client, 1157618)

    new_linode, password = client.linode.instance_create(
        'g6-nanode-1',
        'ap-south',
        'linode/ubuntu22.04',
        authorized_keys=[get_ssh_public_key()],
        label=new_label,
        stackscript=stackscript,
        stackscript_data={"hostname": new_label},
        tags=['coinhunt']
    )
    add_record(f'{new_label}.{get_hosted_zone_name()}', new_linode.ipv4[0])
    while new_linode.status != 'running':
        new_linode = client.linode.instances(Instance.id == new_linode.id)[0]
        print(new_linode)
        print(new_linode.status)
        time.sleep(5)
    time.sleep(60)
    c = Connection(
        host=new_linode.ipv4[0],
        user='root'
    )
    c.run('curl https://raw.githubusercontent.com/yohanesyuen/coinhunt/main/install.sh | bash')
    c.put(ENV_FILE, '/app/coinhunt/.env')
    c.run('curl https://raw.githubusercontent.com/yohanesyuen/coinhunt/main/install.sh | bash')
    print("ssh root@{}".format(new_linode.ipv4[0]))

if __name__ == '__main__':
    main()