# Short-lived response storage for one EIA client. This cache avoids repeated
# identical retrievals; it is neither a historical data store nor shared storage.
from collections import OrderedDict
from copy import deepcopy
from time import monotonic


class Cache:
    # Per-client, in-memory LRU cache. Monotonic time avoids wall-clock changes;
    # copies prevent a caller from mutating a response held for the next request.
    def __init__(self, capacity=64, ttl=300):
        self.capacity, self.ttl = capacity, ttl
        self.entries = OrderedDict()

    def get(self, key):
        # Return an isolated copy of a fresh entry and mark it recently used.
        # Missing and expired entries both tell the caller to retrieve again.
        item = self.entries.get(key)
        if item is None:
            return None
        if monotonic() - item[0] >= self.ttl:
            del self.entries[key]
            return None
        self.entries.move_to_end(key)
        return deepcopy(item[1])

    def put(self, key, value):
        # Save the response with its insertion time and evict the least recently
        # used entries until the configured capacity is respected.
        self.entries[key] = (monotonic(), deepcopy(value))
        self.entries.move_to_end(key)
        while len(self.entries) > self.capacity:
            self.entries.popitem(last=False)
