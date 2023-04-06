from bitcoinutils.keys import PrivateKey

from coinhunt.state import State

def get_address(exp=1):
    priv = PrivateKey(secret_exponent = exp)
    pub = priv.get_public_key()
    address = pub.get_address()
    return (priv.to_wif(compressed=True), address.to_string())

def print_progress(state: State):
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
    completed = 0
    for r in state.searched:
        completed += r[1] - r[0]
    s_completed = '{:,}'.format(completed)
    completed_pct = completed / search_space
    s_remaining = '{:,}'.format(search_space - completed)
    s_completed = ' ' * (len(s_remaining) - len(s_completed)) + s_completed
    print("Completed: {} ({:.20f}%)".format(s_completed, completed_pct * 100))
    print("Remaining: {}".format(s_remaining))
    print("=====================================")

def get_unsearched_ranges(state: State):
    searched = state.searched
    unsearched = list()
    for i in range(len(searched)-1):
        gap = searched[i+1][0] - searched[i][1]
        unsearched.append((gap, (searched[i][1], searched[i+1][0])))
    return unsearched