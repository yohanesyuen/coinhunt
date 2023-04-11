from . import client

def main():
    new_linode, password = client.linode.instance_create(
        'g6-nanode-1',
        'ap-south',
        'linode/ubuntu22.04',
        root_pass='***REMOVED***'
    )

    print("ssh root@{} - {}".format(new_linode.ipv4[0], password))

if __name__ == '__main__':
    main()