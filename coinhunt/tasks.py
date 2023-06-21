from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from celery import Celery

from celery.utils.log import get_task_logger

from coinhunt import (
    REDIS_URL,
)

from redis import StrictRedis

from typing import Any

import platform
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
        'result_expires': 300,
        'prefetch_multiplier': 1,
    }
)

platform_name = platform.system().lower()

def can_ice():
    if platform_name.startswith('win'):
        return True
    if platform_name.startswith('lin'):
        return True
    return False

if can_ice():
    def get_address(exp=1, target='13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so'):
        import coinhunt.secp256k1.secp256k1 as ice
        s_address = ice.privatekey_to_address(
            0, True, exp
        )
        if s_address == target:
            return (
                PrivateKey(secret_exponent = exp)
                    .to_wif(compressed=True),
                s_address
            )
        else:
            return (None, None)
else:
    def get_address(exp=1, target='13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so'):
        priv = PrivateKey(secret_exponent = exp)
        pub = priv.get_public_key()
        address = pub.get_address()
        s_address = address.to_string()
        if s_address == target:
            return (priv.to_wif(compressed=True), s_address)
        else:
            return (None, None)

@app.task
def search_range(start, end, target='13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so'):
    setup('mainnet')
    for i in range(start, end+1):
        wif, pub = get_address(i)
        if wif is not None and pub == target:
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