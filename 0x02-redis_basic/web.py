#!/usr/bin/env python3
""" implements a get_page function (prototype: def get_page(url: str) -> str:)
    The core of the function is very simple. It uses the requests module to
    obtain the HTML content of a particular URL and returns it.

    get_page tracks how many times a particular URL was accessed in the key
    "count:{url}" and cache the result with an expiration time of 10 seconds.

    Bonus: implement this use case with decorators.
"""
import redis
import requests

count = 0
cache = redis.Redis()


def get_page(url: str) -> str:
    """Obtains the HTML content of a particular URL and returns it.
    Tracks how many times the URL was accessed and stores this
    count in a Redis cache.
    """
    count = cache.get(f"count:{url}")
    if count is None:
        count = 0
    else:
        count = int(count)

    resp = requests.get(url)

    count += 1
    cache.setex(f"count:{url}", 10, count)

    return resp.text