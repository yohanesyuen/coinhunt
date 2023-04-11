import redis

import json

from coinhunt import REDIS_URL
from coinhunt.state import State

red = redis.from_url(REDIS_URL)

state = State()

def sync():
    for r in state.get_unsearched_ranges():
        red.zadd('coinhunt:unsearched', json.dumps(r))

if __name__ == '__main__':
    sync()
