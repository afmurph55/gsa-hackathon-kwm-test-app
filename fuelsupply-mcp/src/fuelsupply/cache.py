from collections import OrderedDict
from copy import deepcopy
from time import monotonic


class Cache:
    def __init__(self, capacity=64, ttl=300):
        self.capacity, self.ttl = capacity, ttl
        self.entries = OrderedDict()

    def get(self, key):
        item = self.entries.get(key)
        if item is None:
            return None
        if monotonic() - item[0] >= self.ttl:
            del self.entries[key]
            return None
        self.entries.move_to_end(key)
        return deepcopy(item[1])

    def put(self, key, value):
        self.entries[key] = (monotonic(), deepcopy(value))
        self.entries.move_to_end(key)
        while len(self.entries) > self.capacity:
            self.entries.popitem(last=False)
