from typing import List, Tuple

import json
import os
import random

import logging

from coinhunt import ROOT_DIR

logger = logging.getLogger()

class State(object):
    def __init__(self):
        self.searched = []
        self.max_length = 500
        self.ranges_being_searched = []
        self.filename = os.path.join(ROOT_DIR, 'searched.json')
        self.minimum = 2**65
        self.maximum = 2**66
        if len(self.searched) == 0 and os.path.exists(self.filename):
            self.unmarshall()

        self.start = None
        self.end = None
        self.current = None

        self.compressing = False

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
        self.searched = self.merge_searched_ranges(self.searched)
        with open(self.filename, "w") as f:
            json.dump(self.searched, f, indent=2)

    def unmarshall(self):
        with open(self.filename, "r") as f:
            self.searched = json.load(f)

    def update_searched_ranges(self, start, end):
        self.searched.append((start, end))
        self.marshall()

    def compress_if_needed(self):
        if len(self.searched) > self.max_length and not self.compressing:
            self.compressing = True
        if len(self.searched) < self.max_length * 0.75 and self.compressing:
            self.compressing = False

    def combined_ranges(self):
        ranges = self.searched + self.ranges_being_searched
        ranges = self.merge_searched_ranges(ranges)
        return ranges
    
    def ranges_to_search(self):
        ranges = self.combined_ranges()
        if len(ranges) == 0:
            return [(self.minimum, self.maximum)]
        if ranges[0][0] > self.minimum:
            ranges.insert(0, (self.minimum, ranges[0][0]-1))
        if ranges[-1][1] < self.maximum:
            ranges.append((ranges[-1][1]+1, self.maximum))
        return ranges
    
    # create weights with smallest gap having the highest weight
    def get_weights(self, direction):
        # If direction is "increment" then we want to prioritize the smallest gap
        if direction == 'increment':
            weights = []
            for r in self.ranges_to_search():
                weights.append(r[1] - r[0])
            return weights

        # If direction is "decrement" then we want to prioritize the largest gap
        if direction == 'decrement':
            weights = []
            for r in self.ranges_to_search():
                weights.append(self.maximum - (r[1] - r[0]))
            return weights
    
    # ensure searched ranges are removed from ranges_being_searched
    def remove_searched_ranges(self):
        for searched in self.searched:
            for i in range(len(self.ranges_being_searched)):
                left_matches = self.ranges_being_searched[i][0] == searched[0]
                right_matches = self.ranges_being_searched[i][1] == searched[1]
                if left_matches and right_matches:
                    self.ranges_being_searched.pop(i)
                    break

    def get_random_range(self):
        self.compress_if_needed()
        searched = self.combined_ranges()
        # Get values between 0 and smallest range if first range is not 0
        if len(searched) > 0 and searched[0][0] > self.minimum:
            logger.debug('Getting values between 0 and smallest range')
            start = self.minimum
            end = start + 60000
            return self.limit_range(start, end)
        # Get values between largest range and maximum if last range is not maximum
        if len(searched) > 0 and searched[-1][1] < self.maximum:
            logger.debug('Getting values between largest range and maximum')
            start = self.maximum - 60000
            end = self.maximum
            return self.limit_range(start, end)          
        # Get values between two ranges with the smallest gap if compressing
        if len(searched) > 2:
            logger.debug('Getting values between two ranges with the smallest gap')
            smallest = None
            for i in range(len(searched)-1):
                gap = searched[i+1][0] - searched[i][1]
                if smallest is None or gap < smallest[0]:
                    smallest = (gap, i)
            # Return the full range if gap is less than 60k
            if smallest[0] < 60000 * 2:
                start = searched[smallest[1]][1]
                end = searched[smallest[1]+1][0]
                return (start, end)
            range_start = searched[smallest[1]][1]
            range_end = searched[smallest[1]+1][0]
            range_size = range_end - range_start
            logger.info('Compressing range betwen {} to {} with size {}'.format(
                range_start,
                range_end,
                range_size
            ))
            start = random.randint(range_start, range_end)
            end = random.randint(start, range_end)
            return self.limit_range(start, end)

        start = random.randint(self.minimum, self.maximum)
        end = random.randint(start, start + 60000)
        return self.limit_range(start, end)
    
    def limit_range(self, start, end):
        if start < self.minimum:
            start = self.minimum
        if end > self.maximum:
            end = self.maximum
        if end - start > 60000:
            end = start + 60000
        return (start, end)
