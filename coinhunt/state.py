from queue import Queue
from typing import List, Tuple

import heapq
import json
import os
import random

import logging

import celery
from coinhunt import ROOT_DIR
from celery.result import AsyncResult

logger = logging.getLogger()

def get_workers():
    return celery.current_app.control.inspect().ping()

class State(object):
    def __init__(self):
        self.searched = []
        self.filename = os.path.join(ROOT_DIR, 'searched.json')
        if len(self.searched) == 0 and os.path.exists(self.filename):
            self.unmarshall()
        self.max_length = int(len(self.searched) * 1.5)
        self.ranges_being_searched = dict()
        self.ranges_queue = Queue()
        self.minimum = 2**65
        self.maximum = 2**66
        self.chunk_size = 60000
        self.writes = 0
        self.shrunken = False

        self.results: List[AsyncResult] = []

        self.compressing = False
        self.trolled = False

        self.running = True

    def merge_searched_ranges(self, ranges: List[Tuple[int, int]] = None):
        ranges = self.sort_searched_ranges(ranges)
        merged = []
        for searched in ranges:
            if len(merged) == 0:
                merged.append(searched)
            else:
                last = merged[-1]
                if last[1] >= searched[0]:
                    merged[-1] = (last[0], searched[1])
                else:
                    merged.append(searched)
        return merged

    def sort_searched_ranges(self, ranges: List[Tuple[int, int]] = None):
        return sorted(ranges, key=lambda x: x[0])

    def marshall(self):
        with open(self.filename, "w") as f:
            json.dump(self.searched, f, indent=2)

    def unmarshall(self):
        with open(self.filename, "r") as f:
            self.searched = json.load(f)

    def update_searched_ranges(self, start, end):
        self.searched.append((start, end))
        self.writes += 1
        self.searched = self.merge_searched_ranges(self.searched)
        if self.writes > 10:
            self.marshall()
            self.writes = 0

    def compress_if_needed(self):
        if len(self.searched) > self.max_length and not self.compressing:
            self.compressing = True
        if len(self.searched) < self.max_length * 0.75 and self.compressing:
            self.compressing = False

    def combined_ranges(self):
        ranges = self.searched + list(self.ranges_being_searched.values())
        ranges = self.merge_searched_ranges(ranges)
        return ranges

    def get_unsearched_ranges(self):
        searched = self.combined_ranges()
        unsearched = list()
        for i in range(len(searched)-1):
            gap = searched[i+1][0] - searched[i][1]
            unsearched.append((gap, (searched[i][1], searched[i+1][0])))
        res = sorted(unsearched, key=lambda x: x[0])
        # res = [x for x in res if x[1][1] < self.maximum]
        # res  = [x for x in res if x[1][0] > self.minimum]
        # if res is None:
        #     return []
        return res

    
    def shrink_space(self):
        unsearched = self.get_unsearched_ranges()

        for r in unsearched:
            if r[0] < self.chunk_size * 2:
                continue
            self.minimum = r[1][0]
            self.maximum = r[1][1]
        self.shrunken = True

    def get_random_range(self):
        self.compress_if_needed()
        searched = self.combined_ranges()
        # Get values between 0 and smallest range if first range is not 0
        if len(searched) > 0 and searched[0][0] > self.minimum:
            start = self.minimum
            end = start + self.chunk_size
            logger.debug('Getting values between minimum and minimum + 60k')
            return self.limit_range(start, end)
        # Get values between largest range and maximum if last range is not maximum
        if len(searched) > 0 and searched[-1][1] < self.maximum:
            logger.debug('Getting values between maximum - 60k and maximum')
            start = self.maximum - self.chunk_size
            end = self.maximum
            return self.limit_range(start, end)          
        # Get values between two ranges with the smallest gap if compressing
        if len(self.get_unsearched_ranges()) > 2:
            if not self.trolled:
                logger.debug('Getting values between two random ranges')
                search_range = random.choice(self.get_unsearched_ranges())
                if len(self.searched) > self.max_length:
                    self.trolled = True
            elif self.ranges_queue.qsize() > 0:
                search_range = self.ranges_queue.get()
            elif self.ranges_queue.qsize() == 0:
                ranges = self.get_unsearched_ranges()
                for i in range(20):
                    self.ranges_queue.put(
                        ranges[i]
                    )
                search_range = self.ranges_queue.get()
            elif self.compressing:
                logger.debug('Get smallest gap between two ranges')
                search_range = self.get_unsearched_ranges()[0]
            else:
                logger.debug(
                    'Getting values between two random ranges'
                )
                # search_range = random.choices(
                #     self.get_unsearched_ranges(),
                #     weights=[1/x[0] for x in self.get_unsearched_ranges()]
                # )[0]
                search_range = random.choice(self.get_unsearched_ranges())
            logger.debug(search_range)
            # Return the full range if gap is less than 60k
            if search_range[0] < self.chunk_size * 2:
                start = search_range[1][0]
                end = search_range[1][1]
                return (start, end)
            elif search_range[0] < self.chunk_size * 100:
                # Get the value at middle - self.chunk_size
                range_start = int(max(
                    search_range[1][0] + (search_range[0] // 2) - (self.chunk_size // 2),
                    search_range[1][0]
                ))
                range_end = int(min(
                    range_start + self.chunk_size,
                    search_range[1][1]
                ))
                return self.limit_range(range_start, range_end)
            range_start = search_range[1][0]
            range_end = search_range[1][1]
            range_size = range_end - range_start
            logger.info('Compressing range betwen {} to {} with size {}'.format(
                range_start,
                range_end,
                range_size
            ))
            start = random.randint(range_start, range_end)
            return self.limit_range(start, range_end)

        start = random.randint(self.minimum, self.maximum)
        end = random.randint(start, start + self.chunk_size)
        return self.limit_range(start, end)
    
    def limit_range(self, start, end):
        if start < self.minimum:
            start = self.minimum
        if end > self.maximum:
            end = self.maximum
        if end - start > self.chunk_size:
            end = start + self.chunk_size
        return (start, end)
