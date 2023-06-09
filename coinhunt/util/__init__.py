from bitcoinutils.keys import PrivateKey

from coinhunt.state import State

from cachetools import TTLCache, cached
import celery

@cached(cache=TTLCache(maxsize=1, ttl=60))
def get_workers():
    return celery.current_app.control.inspect().ping()

prev_hit_chance = 0

def get_address(exp=1):
    priv = PrivateKey(secret_exponent = exp)
    pub = priv.get_public_key()
    address = pub.get_address()
    return (priv.to_wif(compressed=True), address.to_string())

def print_progress(state: State):
    global prev_hit_chance
    # print progress
    search_space = state.maximum - state.minimum
    print("Searched: {}".format(len(state.searched)))
    ranges_being_searched = state.ranges_being_searched
    print('Ranges being searched: {}'.format(len(ranges_being_searched)))
    trolled = state.trolled
    compressing = state.compressing
    print("Trolled: {}".format(trolled))
    print("Compressing: {}".format(compressing))
    print("Search space: {:,}".format(search_space))
    print("Chunk size: {:,}".format(state.chunk_size))
    completed = 0
    for r in state.searched:
        completed += r[1] - r[0]
    s_completed = '{:,}'.format(completed)
    completed_pct = completed / search_space
    s_remaining = '{:,}'.format(search_space - completed)
    s_completed = ' ' * (len(s_remaining) - len(s_completed)) + s_completed
    print("Completed: {} ({:.20f}%)".format(s_completed, completed_pct * 100))
    print("Remaining: {}".format(s_remaining))
    chunks_left = (search_space - completed) // state.chunk_size
    print("Chunks left: {:,}".format(chunks_left))
    hit_chance = 1 / chunks_left
    print("Hit chance: {:.30f}%".format(hit_chance * 100))
    if prev_hit_chance > 0:
        print("Hit chance multiplier: {:.30f}%".format(hit_chance / prev_hit_chance * 100))
    prev_hit_chance = hit_chance
    gaps = [r[0] for r in state.get_unsearched_ranges(filtered=False)[:20]]
    print("Chunks: {}".format(gaps))
    print("Range Queue: {}".format(
        [r[0] for r in list(state.ranges_queue.queue)]
    ))
    time_left = chunks_left * 60 // 20
    time_left_s = time_left % 60
    time_left_m = int(time_left // 60) % 60
    time_left_h = int(time_left // 3600) % 24
    time_left_d = int(time_left // 86400)
    time_left = "{:,}d {:02d}h {:02d}m {:02d}s".format(
        time_left_d, time_left_h, time_left_m, time_left_s)
    print("Time left: {}".format(time_left))
    print("=====================================")

def get_unsearched_ranges(state: State):
    searched = state.searched
    unsearched = list()
    for i in range(len(searched)-1):
        gap = searched[i+1][0] - searched[i][1]
        unsearched.append((gap, (searched[i][1], searched[i+1][0])))
    return unsearched


