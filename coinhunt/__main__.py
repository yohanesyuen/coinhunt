#%%
from bitcoinutils.setup import setup

import celery
import logging
import signal
import time

import dotenv

from celery.result import AsyncResult

from coinhunt.tasks import search_range

from coinhunt.state import State
from coinhunt.util import print_progress

logger = logging.getLogger(__name__)


#%%
dotenv.load_dotenv()
target = '13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so'

state = State()

def execute():
    pass

def get_workers():
    return celery.current_app.control.inspect().ping()

def main():
    # always remember to setup the network
    setup('mainnet')
    possibilities = state.maximum - state.minimum
    logger.info(f'Starting search from {state.minimum} to {state.maximum}...')
    logger.info(f'Possibilities: {possibilities}')
    results = []

    while state.running:
        if len(results) < len(get_workers().keys()):    
            start, end = state.get_random_range()
            count = end - start
            print(f"Searching {count} keys from {start} to {end}...")
            results.append(search_range.apply_async(args=(start, end)))
            state.ranges_being_searched.append((start, end))
        new_results = []
        for result in results:
            print(result.get())
        time.sleep(1)
        continue

def signal_handler(sig, frame):
    logger.info('You pressed Ctrl+C!')
    state.running = False
    state.update_searched_ranges(state.start, state.end)
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    # Setup logging to output timestamp and funcname with log level
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(funcName)s: %(message)s',
        level=logging.DEBUG
    )
    main()
# %%
