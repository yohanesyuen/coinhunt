
from . import client


def main():
    current_instances = list(filter(
            lambda x: x.label.startswith('coinhunt'),
            client.linode.instances()
        ))

    for linode in current_instances:
        if linode.status == 'running':
            linode.reboot()

if __name__ == '__main__':
    main()