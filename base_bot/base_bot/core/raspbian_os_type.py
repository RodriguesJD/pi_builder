import os
import json
import subprocess
from pathlib import Path


class RaspianBaseBot:
    """Installs raspbain on an sd card
    """
    def __init__(self, sd_card_name="RASPBIAN"):
        self.sd_card_name = sd_card_name

    def mount_paths(self):
        """Find the most likey place the sd card is mounted.

        Returns
        -------

        """
        # umount /media/pi/boot
        # umount /media/pi/rootfs

        mount_point = []
        unmount_path = []
        sda = 'sda'
        sdb = 'sdb'
        diskutil_list = subprocess.Popen("lsblk", shell=True, stdout=subprocess.PIPE)
        for line in diskutil_list.stdout:
            line = line.decode()
            if sda in line:
                mount_point.append(sda)

            elif sdb in line:
                mount_point.append(sdb)

            if sda in line or sdb in line:
                path = line.split(" ")[-1]
                if len(path) == 1:
                    unmount_path.append(False)
                else:
                    raise Exception("Need to add a catch for this")

        return mount_point, unmount_path

    def install_os(self):
        raspbian_img = []
        for file in os.listdir(os.getcwd()):
            if "raspbian-stretch" in file:
                raspbian_img.append(file)

        if not raspbian_img:
            raise Exception("Cant find the raspbian img. "
                            "This usually means you're not in the same directory as the python file.")

        file = raspbian_img[0]
        path_to_image = Path(os.getcwd(), file)
        subprocess.Popen(["sudo dd bs=4M if=" + str(path_to_image) + " of=/dev/" + self.mount_paths()[0][0] + " conv=sync"],
                         shell=True, stdout=subprocess.PIPE).communicate()

    def assistant(self):
        if self.mount_paths()[1][0]:
            print("f1")
            raise Exception("Cant find the sd card's mounted disk number")

        else:
            print("else")
            print("installing OS")
            self.install_os()


