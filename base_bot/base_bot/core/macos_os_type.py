import os
import subprocess
from pathlib import Path
import logging

import yaml


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


class MacosBaseBot:
    """Installs raspbain on an sd card
    """
    def __init__(self, sd_card_name="RASPBIAN"):
        self.sd_card_name = sd_card_name

        self.disk_number = False
        self.disk_path = False

    def gather_disk_number(self):
        """Find the most likey place the sd card is mounted.

        Returns
        -------

        """
        logger.debug("MacosBaseBot.gather_disk_number")

        # create subprocess to run terminal command
        diskutil_list = subprocess.Popen("diskutil list", shell=True, stdout=subprocess.PIPE)
        outp = diskutil_list.stdout
        external_disks = []

        for line in outp:
            external_disk = "(external, physical)"

            # Convert byte string to ascii <- I think its ascii
            decoded_line = line.decode()

            if external_disk in decoded_line:
                disk_num = decoded_line.split(external_disk)[0].split("disk")[1]
                if int(disk_num):
                    external_disks.append(disk_num.replace(" ", ""))

        if not external_disks:
            logger.error("Can't find usb drive in diskutil, MacosBaseBot.disk_number")
            return False
        elif len(external_disks) > 1:
            raise Exception("There is more than 1 external disk. Fix this issue.")
        else:
            self.disk_number = external_disks[0]
            return external_disks[0]

    def gather_disk_path(self):
        logger.debug("MacosBaseBot.gather_disk_path")
        path_to_disk = f"/dev/disk{self.disk_number}"
        self.disk_path = path_to_disk

        return path_to_disk

    def erase_disk(self):
        logger.debug("MacosBaseBot.erase_disk")
        subprocess.Popen([f"diskutil eraseDisk ExFAT {self.sd_card_name} MBRFormat {self.disk_path}"],
                         shell=True, stdout=subprocess.PIPE).communicate()

    def unmount_disk(self):
        logger.debug("MacosBaseBot.unmount_disk")
        subprocess.Popen([f"diskutil unmountDisk {self.disk_path}"],
                         shell=True, stdout=subprocess.PIPE).communicate()

    def install_os(self):
        logger.debug("MacosBaseBot.install_os")
        pi_img = False
        for file in os.listdir(os.getcwd()):
            if "ubuntu" in file and ".img" in file:
                pi_img = file

        if not pi_img:
            raise Exception("Cant find the pi img. "
                            "This usually means you're not in the same directory as the python file.")

        path_to_image = Path(os.getcwd(), pi_img)

        subprocess.Popen([f"sudo dd bs=1m if={path_to_image} of={self.disk_path} conv=sync"],
                         shell=True, stdout=subprocess.PIPE).communicate()

    def mount_disk(self):
        logger.debug("MacosBaseBot.mount_disk")
        subprocess.Popen([f"diskutil mountDisk {self.disk_path}"],
                         shell=True, stdout=subprocess.PIPE).communicate()

    def enable_ssh(self):
        # TODO the ssh_path is wrong
        logger.debug("MacosBaseBot.enable_ssh")
        ssh_path = Path("/Volumes/system-boot/ssh")
        if not os.path.isfile(ssh_path):
            subprocess.Popen(["touch {}".format(ssh_path)], shell=True, stdout=subprocess.PIPE).communicate()

    @staticmethod
    def configure_wifi():
        # TODO use yaml https://ubuntu.com/tutorials/how-to-install-ubuntu-on-your-raspberry-pi#3-wifi-or-ethernet
        logger.debug("MacosBaseBot.configure_wifi")
        # TODO network config path is wrong
        network_config_path = Path("/Volumes/system-boot/network-config")
        if not os.path.isfile(network_config_path):
            subprocess.Popen([f"touch {network_config_path}".format(network_config_path)], shell=True, stdout=subprocess.PIPE).communicate()

        ssid = input("What is the ssid\n")
        wifi_password = input("What is the wifi password\n")
        wifi_dict = {
            "version": 2,
            "ethernets": {
                "eth0": {
                    "dhcp4": True,
                    "optional": True
                }
            },
            "wifis": {
                "wlan0": {
                    "dhcp4": True,
                    "optional": True,
                    "access-points": {
                        ssid: {
                            "password": f'{str(wifi_password)}'
                        }
                    }
                }
            }
        }
        with open(network_config_path, 'w') as file:
            yaml.dump(wifi_dict, file)

    def assistant(self):
        logger.debug("MacosBaseBot.assistant")

        if not self.gather_disk_number():
            # TODO change this to wait for the sd card to be mounted.
            raise Exception("Cant find the sd card's mounted disk number")

        # Generate the disk path
        self.gather_disk_path()

        disk_erased = input("Have you erased the disk yet\n")
        if "y" in disk_erased:
            disk_unmounted = input("Is the disk unmounted?\n")
            if "y" in disk_unmounted:
                self.install_os()
            else:
                self.unmount_disk()
                self.install_os()

        else:
            self.erase_disk()
            self.unmount_disk()
            self.install_os()

        self.mount_disk()
        self.enable_ssh()
        self.configure_wifi()
        self.unmount_disk()



