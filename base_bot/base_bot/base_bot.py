from sys import platform
import logging

from core.raspbian_os_type import RaspianBaseBot
from core.macos_os_type import MacosBaseBot

logging.basicConfig(
    filename="trash_problem.log",
    filemode='w',
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


if platform == "linux" or platform == "linux2":
    logging.debug("linux")
    RaspianBaseBot().assistant()

elif platform == "darwin":
    logging.debug("MacOS")
    MacosBaseBot().assistant()

else:
    raise Exception("I dont recognize this |" + platform + "| as a platform I know")
