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


def sub_proc(command):
    subprocess_call = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE).communicate()
    return subprocess_call[0].decode()


class MacosBaseBot:
    """Installs ubuntu on an sd card
    """
    def __init__(self, sd_card_name="system-boot"):
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
        diskutil_list = sub_proc("diskutil list").split("\n")
        external_disks = []

        for line in diskutil_list:
            external_disk = "(external, physical)"

            # Convert byte string to ascii <- I think its ascii
            if external_disk in line:
                disk_num = line.split(external_disk)[0].split("disk")[1]
                if int(disk_num):
                    external_disks.append(disk_num.replace(" ", ""))

        if not external_disks:
            logger.error("Can't find usb drive in diskutil, MacosBaseBot.disk_number")
            return False
        elif len(external_disks) > 1:
            raise Exception("There is more than 1 external disk. Fix this issue.")
        else:
            self.disk_number = external_disks[0]
            logger.info(f"Disk Number is {external_disks[0]}")
            return external_disks[0]

    def gather_disk_path(self):
        logger.debug("MacosBaseBot.gather_disk_path")
        path_to_disk = f"/dev/disk{self.disk_number}"
        logger.info(f"Path to disk {path_to_disk}")
        self.disk_path = path_to_disk

        return path_to_disk

    def erase_disk(self):
        logger.debug("MacosBaseBot.erase_disk")
        command = f"diskutil eraseDisk ExFAT {self.sd_card_name} MBRFormat {self.disk_path}"
        sub_proc(command)

    def unmount_disk(self):
        logger.debug("MacosBaseBot.unmount_disk")
        command = f"diskutil unmountDisk {self.disk_path}"
        sub_proc(command)

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
        command = f"sudo dd bs=1m if={path_to_image} of={self.disk_path} conv=sync"
        command_output = sub_proc(command)
        logger.debug(f"MacosBaseBot.install_os time to write to sd card {command_output}.")

    def mount_disk(self):
        logger.debug("MacosBaseBot.mount_disk")
        try_command = True
        attempts = 0
        max_attempts = 3
        while try_command:
            command = f"diskutil mountDisk {self.disk_path}"
            command_output = sub_proc(command)
            if "Volume(s) mounted successfully" in command_output:
                try_command = False
            else:
                attempts += 1
                if attempts == 3:
                    raise Exception("3 attempts failed to mount disk")


    def enable_ssh(self):
        # TODO the ssh_path is wrong
        logger.debug("MacosBaseBot.enable_ssh")
        ssh_path = Path("/Volumes/system-boot/ssh")
        if not os.path.isfile(ssh_path):
            command = f"touch {ssh_path}"
            sub_proc(command)

    @staticmethod
    def configure_wifi():
        # TODO use yaml https://ubuntu.com/tutorials/how-to-install-ubuntu-on-your-raspberry-pi#3-wifi-or-ethernet
        logger.debug("MacosBaseBot.configure_wifi")
        # TODO network config path is wrong
        network_config_path = Path("/Volumes/system-boot/network-config")
        if not os.path.isfile(network_config_path):
            command =f"touch {network_config_path}"
            sub_proc(command)
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



