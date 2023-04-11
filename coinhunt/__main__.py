#%%
import sys
from bitcoinutils.setup import setup

import celery
import logging
import signal

import dotenv

from celery.result import AsyncResult

from coinhunt.tasks import search_range, purge

from coinhunt.state import State
from coinhunt.util import print_progress

import time

logger = logging.getLogger(__name__)


#%%
dotenv.load_dotenv()
state = State()

def execute():
    pass

def get_workers():
    return celery.current_app.control.inspect().ping()

def main():
    # always remember to setup the network
    setup('mainnet')
    possibilities = state.maximum - state.minimum
    results = state.results
    logger.info(f'Starting search from {state.minimum} to {state.maximum}...')
    logger.info(f'Possibilities: {possibilities}')


    while state.running or len(results) > 0:
        if len(results) < len(get_workers().keys()) * 4 and state.running:
            start, end = state.get_random_range()
            count = end - start
            logger.info(f"Searching {count} keys from {start} to {end}...")
            res: AsyncResult = search_range.apply_async(args=(start, end))
            results.append(res)
            state.ranges_being_searched[res.id] = (start, end)
        new_results = []
        while len(results) > 0:
            res = results.pop()
            if res.status != 'SUCCESS':
                # print(res.status)
                new_results.append(res)
                continue
            rid = res.id
            res = res.get()
            if res['status'] == 'Found':
                logger.info(f"Found! WIF: {res['wif']}")
                state.running = False
                break
            elif res['status'] == 'Not found':
                state.update_searched_ranges(res['start'], res['end'])
                state.ranges_being_searched.pop(rid)
                print_progress(state)
        results = new_results

def signal_handler(sig, frame):
    logger.info('You pressed Ctrl+C!')
    if state.running:
        logger.info('Stopping search...')
        state.running = False
    else:
        logger.info('Purging state...')
        purge()
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    # Setup logging to output timestamp and funcname with log level
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(funcName)s: %(message)s',
        level=logging.DEBUG
    )
    main()
# %%
