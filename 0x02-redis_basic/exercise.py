#!/usr/bin/env python3
"""
Redis module
"""

import sys
from functools import wraps
from typing import Union, Optional, Callable
from uuid import uuid4

import redis

UnionOfTypes = Union[str, bytes, int, float]


def replay(method: Callable) -> None:
    """display the history of calls of a particular function
    """
    key = method.__qualname__
    data = redis.Redis()
    hist = data.get(key).decode("utf-8")
    print("{} was called {} times:".format(key, hist))
    inputs = data.lrange(key + ":inputs", 0, -1)
    outputs = data.lrange(key + ":outputs", 0, -1)
    for k, v in zip(inputs, outputs):
        print(f"{key}(*{k.decode('utf-8')}) -> {v.decode('utf-8')}")


def count_calls(method: Callable) -> Callable:
    """Increments a counter in Redis each time
    the method is called.
    """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Records the input parameters and output of
    the method in Redis.
    """
    key = method.__qualname__
    i = "{}{}".format(key, ":inputs")
    o = "{}{}".format(key, ":outputs")

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.rpush(i, str(args))
        res = method(self, *args, **kwargs)
        self._redis.rpush(o, str(res))
        return res
    return wrapper


class Cache:
    def __init__(self):
        """Initializes a Redis client and clears the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: UnionOfTypes) -> str:
        """Generates a random key, stores the input data in Redis,
        and returns the key.
        """
        key = str(uuid4())
        self._redis.mset({key: data})
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> UnionOfTypes:
        """Retrieves data from Redis given a key and applies a
        function to it if provided.
        """
        if fn:
            return fn(self._redis.get(key))
        data = self._redis.get(key)
        return data

    def get_int(self, key: str) -> int:
        """Retrieves data from Redis and converts it to an integer."""
        return int.from_bytes(self.get(key), sys.byteorder)

    def get_str(self, key: str) -> str:
        """Retrieves data from Redis and decodes it as a UTF-8 string."""
        return self.get(key).decode("utf-8")
