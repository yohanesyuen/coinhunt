#%%
from bitcoinutils.setup import setup

import logging
import os
import signal
import time

import dotenv

from typing import List

import redis
from rq import Queue, Worker
from rq.job import Job, JobStatus

from coinhunt.state import State
from coinhunt.util import print_progress

from coinhunt import tasks

logger = logging.getLogger(__name__)


#%%
dotenv.load_dotenv()
broker = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    password=os.getenv("REDIS_PASS"),
)
job_queue = Queue(connection=broker)
target = '13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so'

state = State()

def execute():
    pass

def main():
    # always remember to setup the network
    setup('mainnet')
    possibilities = state.maximum - state.minimum
    logger.info(f'Starting search from {state.minimum} to {state.maximum}...')
    logger.info(f'Possibilities: {possibilities}')
    jobs: List[Job] = []
    while state.running:
        if len(jobs) > len(Worker.all(queue=job_queue)):
            new_jobs = []
            while len(jobs) > 0:
                job = jobs.pop(0)
                if job.get_status() != JobStatus.FINISHED:
                    new_jobs.append(job)
                elif job.result is JobStatus.FAILED:
                    # requeue job
                    print('Job failed, requeuing...')
                    
                    # get job func
                    func = job.func

                    # get job args
                    args = job.args

                    job_queue.enqueue(func, *args)
                else:
                    if job.result['status'] == 'Found':
                        logger.info(f"Found private key: {job.result['wif']}")
                        logger.info(f"Address: {job.result['pub']}")
                        state.running = False
                    else:
                        state.update_searched_ranges(
                            job.result['start'],
                            job.result['end']
                        )
                        print_progress(state)
            jobs = new_jobs
            time.sleep(1)
            continue
        start, end = state.get_random_range()
        count = end - start
        print(f"Searching {count} keys from {start} to {end}...")
        jobs.append(job_queue.enqueue(tasks.search_range, start, end))
        state.ranges_being_searched.append((start, end))

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
