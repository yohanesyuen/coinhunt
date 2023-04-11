from linode_api4 import LinodeClient

import os

LINODE_TOKEN = os.environ.get('LINODE_TOKEN')
client = LinodeClient(LINODE_TOKEN)

