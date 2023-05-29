
from coinhunt.cloud.aws import delete_record, get_hosted_zone_name
from . import client

import argparse

def delete_linode(linode):
    delete_record(f'{linode.label}.{get_hosted_zone_name()}', linode.ipv4[0])
    print(linode.label, linode.ipv4, linode.status)
    linode.delete()

def main(args=None):
    current_instances = list(filter(
            lambda x: x.label.startswith('coinhunt'),
            client.linode.instances()
        ))
    if args.n > len(current_instances):
        raise ValueError(f'Cannot delete {args.n} instances, only {len(current_instances)} exist')
    for i in range(args.n):
        linode = current_instances[(len(current_instances) - i) - 1]
        delete_linode(linode)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Delete N linode instance')
    parser.add_argument('n', type=int, help='number of instances to delete', default=1)
    args = parser.parse_args()
    main(args=args)