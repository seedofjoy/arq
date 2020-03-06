import functools
import os

import msgpack
import pytest
from aioredis import create_redis_pool

from darq.connections import ArqRedis, RedisSettings
from darq.worker import Worker

TEST_REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'


@pytest.fixture
def redis_host():
    return TEST_REDIS_HOST


@pytest.fixture
def test_redis_settings(redis_host):
    return RedisSettings(host=redis_host)


@pytest.yield_fixture
async def arq_redis(loop, redis_host):
    redis_ = await create_redis_pool(
        (redis_host, 6379), encoding='utf8', loop=loop, commands_factory=ArqRedis, minsize=5
    )
    await redis_.flushall()
    yield redis_
    redis_.close()
    await redis_.wait_closed()


@pytest.yield_fixture
async def arq_redis_msgpack(loop, redis_host):
    redis_ = await create_redis_pool(
        (redis_host, 6379),
        encoding='utf8',
        loop=loop,
        commands_factory=functools.partial(
            ArqRedis, job_serializer=msgpack.packb, job_deserializer=functools.partial(msgpack.unpackb, raw=False)
        ),
    )
    await redis_.flushall()
    yield redis_
    redis_.close()
    await redis_.wait_closed()


@pytest.yield_fixture
async def worker(arq_redis):
    worker_: Worker = None

    def create(functions=[], burst=True, poll_delay=0, max_jobs=10, **kwargs):
        nonlocal worker_
        worker_ = Worker(
            functions=functions, redis_pool=arq_redis, burst=burst, poll_delay=poll_delay, max_jobs=max_jobs, **kwargs
        )
        return worker_

    yield create

    if worker_:
        await worker_.close()
