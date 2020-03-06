from click.testing import CliRunner

from darq.cli import cli
from darq.connections import RedisSettings

from .conftest import TEST_REDIS_HOST


async def foobar(ctx):
    return 42


class WorkerSettings:
    burst = True
    functions = [foobar]
    redis_settings = RedisSettings(host=TEST_REDIS_HOST)


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert result.output.startswith('Usage: darq [OPTIONS] WORKER_SETTINGS\n')


def test_run():
    runner = CliRunner()
    result = runner.invoke(cli, ['tests.test_cli.WorkerSettings'])
    assert result.exit_code == 0
    assert 'Starting worker for 1 functions: foobar' in result.output


def test_check():
    runner = CliRunner()
    result = runner.invoke(cli, ['tests.test_cli.WorkerSettings', '--check'])
    assert result.exit_code == 1
    assert 'Health check failed: no health check sentinel value found' in result.output


async def mock_awatch():
    yield [1]


def test_run_watch(mocker):
    mocker.patch('watchgod.awatch', return_value=mock_awatch())
    runner = CliRunner()
    result = runner.invoke(cli, ['tests.test_cli.WorkerSettings', '--watch', 'tests'])
    assert result.exit_code == 0
    assert '1 files changes, reloading darq worker...'
