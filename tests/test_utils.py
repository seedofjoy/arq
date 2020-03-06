import logging
import re
from datetime import timedelta

import pytest

import darq.utils
from darq.connections import RedisSettings, create_pool, log_redis_info


def test_settings_changed():
    settings = RedisSettings(port=123)
    assert settings.port == 123
    assert (
        f'<RedisSettings host=localhost port=123 database=0 password=None ssl=None conn_timeout=1 conn_retries=5 '
        'conn_retry_delay=1 sentinel=False sentinel_master=mymaster>'
    ) == str(settings)


async def test_redis_timeout(mocker):
    mocker.spy(darq.utils.asyncio, 'sleep')
    with pytest.raises(OSError):
        await create_pool(RedisSettings(port=0, conn_retry_delay=0))
    assert darq.utils.asyncio.sleep.call_count == 5


async def test_redis_sentinel_failure(redis_host):
    settings = RedisSettings()
    settings.host = [(redis_host, 6379), (redis_host, 6379)]
    settings.sentinel = True
    try:
        pool = await create_pool(settings)
        await pool.ping('ping')
    except Exception as e:
        assert 'unknown command `SENTINEL`' in str(e)


async def test_redis_success_log(caplog, test_redis_settings):
    caplog.set_level(logging.INFO)
    pool = await create_pool(test_redis_settings)
    assert 'redis connection successful' not in [r.message for r in caplog.records]
    pool.close()
    await pool.wait_closed()

    pool = await create_pool(test_redis_settings, retry=1)
    assert 'redis connection successful' in [r.message for r in caplog.records]
    pool.close()
    await pool.wait_closed()


async def test_redis_log(test_redis_settings):
    redis = await create_pool(test_redis_settings)
    await redis.flushall()
    await redis.set(b'a', b'1')
    await redis.set(b'b', b'2')

    log_msgs = []

    def _log(s):
        log_msgs.append(s)

    await log_redis_info(redis, _log)
    assert len(log_msgs) == 1
    assert re.search(r'redis_version=\d\.', log_msgs[0]), log_msgs
    assert log_msgs[0].endswith(' db_keys=2')


def test_truncate():
    assert darq.utils.truncate('123456', 4) == '123…'


def test_args_to_string():
    assert darq.utils.args_to_string((), {'d': 4}) == 'd=4'
    assert darq.utils.args_to_string((1, 2, 3), {}) == '1, 2, 3'
    assert darq.utils.args_to_string((1, 2, 3), {'d': 4}) == '1, 2, 3, d=4'


@pytest.mark.parametrize(
    'input,output', [(timedelta(days=1), 86_400_000), (42, 42000), (42.123, 42123), (42.123_987, 42124), (None, None)]
)
def test_to_ms(input, output):
    assert darq.utils.to_ms(input) == output


@pytest.mark.parametrize('input,output', [(timedelta(days=1), 86400), (42, 42), (42.123, 42.123), (None, None)])
def test_to_seconds(input, output):
    assert darq.utils.to_seconds(input) == output
