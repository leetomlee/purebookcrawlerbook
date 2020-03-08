#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""A script to process items from a redis queue."""
from __future__ import print_function, unicode_literals

import json
import logging
import pprint
import sys
import time

import pymongo
from redis import StrictRedis

redis = StrictRedis(host='120.27.244.128', port=6379, db=0, password='zx222lx')
logger = logging.getLogger('process_items')

client = pymongo.MongoClient(host='120.27.244.128')
db = client['book']
chapterDB = db['chapter']
bookDB = db['book']


def process_items(keys, limit=0, log_every=1000, wait=.1):
    """Process items from a redis queue.

    Parameters
    ----------
    r : Redis
        Redis connection instance.
    keys : list
        List of keys to read the items from.
    timeout: int
        Read timeout.

    """
    limit = limit or float('inf')
    processed = 0
    while processed < limit:
        # Change ``blpop`` to ``brpop`` to process as LIFO.
        ret = redis.blpop(keys)
        # If data is found before the timeout then we consider we are done.
        if ret is None:
            time.sleep(wait)
            continue

        source, data = ret
        try:
            item = json.loads(data)
        except Exception:
            logger.exception("Failed to load item:\n%r", pprint.pformat(data))
            continue

        try:

            chapterDB.insert_one(item)

        except KeyError:
            logger.exception("[%s] Failed to process item:\n%r",
                             source, pprint.pformat(item))
            continue

        processed += 1
        if processed % log_every == 0:
            logger.info("Processed %s items", processed)


def main():
    try:
        process_items(keys='yb:items')
        retcode = 0  # ok
    except KeyboardInterrupt:
        retcode = 0  # ok
    except Exception:
        logger.exception("Unhandled exception")
        retcode = 2

    return retcode


if __name__ == '__main__':
    sys.exit(main())
