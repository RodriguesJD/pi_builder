from sys import platform

from core.raspbian_os_type import RaspianBaseBot
from core.macos_os_type import MacosBaseBot

if platform == "linux" or platform == "linux2":
    RaspianBaseBot().assistant()

elif platform == "darwin":
    MacosBaseBot().assistant()

else:
    raise Exception("I dont recognize this |" + platform + "| as a platform I know")
