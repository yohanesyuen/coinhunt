import threading

from . import client
from fabric import Connection
import os

def get_ssh_public_key():
    with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as f:
        return f.read().strip()
    
def execute(c: Connection):
    # c.run('echo "cd /app/coinhunt && git pull" | bash')
    c.run('service coinhunt reload')

def main():

    current_instances = list(filter(
        lambda x: x.label.startswith('coinhunt'),
        client.linode.instances()
    ))

    threads = list()
    for linode in current_instances:
        print(linode.label, linode.ipv4, linode.status)

        c = Connection(
            host=linode.ipv4[0],
            user='root'
        )

        threads.append(
            threading.Thread(
                target=execute,
                args=(c,)
            )
        )
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()