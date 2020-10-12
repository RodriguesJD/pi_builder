from base_bot import __version__
from base_bot.base_bot.base_bot import BaseBot
from base_bot.base_bot.base_bot import Bas

def test_version():
    assert __version__ == '0.1.0'

def test_disk_number():
    # Will only pass if a sd card is plugged in.
    assert (BaseBot().erase_disk())

