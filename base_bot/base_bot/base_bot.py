from sys import platform
import logging

import yaml

from core.raspbian_os_type import RaspianBaseBot
from core.macos_os_type import MacosBaseBot


# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('base_bot.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


logger.debug('==========Start=========')

if platform == "linux" or platform == "linux2":
    logger.debug("build host is linux")
    RaspianBaseBot().assistant()

elif platform == "darwin":
    logger.debug("build host is macOS")
    MacosBaseBot().assistant()

else:
    raise Exception("I dont recognize this |" + platform + "| as a platform I know")
