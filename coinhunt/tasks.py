from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from celery import Celery

from celery.utils.log import get_task_logger

from coinhunt import (
    REDIS_URL,
)

from redis import StrictRedis

from typing import Any

import logging

class RedisBaseHandler(logging.StreamHandler):
    def __init__(self, raw_logging: bool = False, **kwargs: Any):
        super().__init__()
        self.raw_logging = raw_logging
        if 'redis_url' in kwargs.keys():
            self.redis_client = StrictRedis.from_url(kwargs['redis_url'])
        else:
            self.redis_client = StrictRedis(**kwargs)

    def emit(self, message: logging.LogRecord):
        raise NotImplementedError("Emit functionality from base class not overridden.")


class RedisChannelHandler(RedisBaseHandler):
    def __init__(self, channel: str, **kwargs: Any):
        super().__init__(**kwargs)

        self.channel = channel

    def emit(self, message: logging.LogRecord):
        content = str(message.msg)
        if self.raw_logging:
            content += f"{message.lineno} - {message.pathname}"

        self.redis_client.publish(self.channel, content)

logger = get_task_logger(__name__)
logger.setLevel('INFO')
logger.addHandler(RedisChannelHandler('coinhunt:log', redis_url=REDIS_URL))


app = Celery(
    'tasks',
    broker=f'{REDIS_URL}',
    backend=f'{REDIS_URL}',
)

app.conf.update(
    {
        'result_expires': 30,
        'prefetch_multiplier': 1,
    }
)

target = '13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so'

def get_address(exp=1):
    priv = PrivateKey(secret_exponent = exp)
    pub = priv.get_public_key()
    address = pub.get_address()
    return (priv.to_wif(compressed=True), address.to_string())

@app.task
def search_range(start, end):
    setup('mainnet')
    for i in range(start, end):
        wif, pub = get_address(i)
        if pub == target:
            return {
                'status': 'Found',
                'wif': wif,
                'pub': pub,
            }
    return {
        'status': 'Not found',
        'start': start,
        'end': end
    }

def purge():
    app.control.purge()