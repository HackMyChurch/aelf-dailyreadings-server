'''
Simple caching module. Each cache entry has an associated checksum to easily
invalidate cache entries / test cache validity.
'''

import cPickle as pickle
import hashlib
from collections import namedtuple

CacheEntry = namedtuple('CacheEntry', ['checksum', 'value'])

class Cache(object):
    def __init__(self):
        self.__CACHE = {}

    def set(self, key, value):
        '''
        Compute the checksum of value and store it in the cache
        '''
        data = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        checksum = hashlib.sha256(data).hexdigest()
        entry = CacheEntry(value=value, checksum=checksum)
        self.__CACHE[key] = entry
        return entry.checksum

    def get(self, key, checksum=None):
        '''
        Return value associated with ``key``.If checksum is not ``checksum``,
        consider inexistent but do not remove from the cache.
        '''
        entry = self.__CACHE.get(key, None)
        if entry is None:
            return None

        if checksum is not None and entry.checksum != checksum:
            return None

        return entry

