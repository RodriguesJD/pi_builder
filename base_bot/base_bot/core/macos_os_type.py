import os
import subprocess
from pathlib import Path


class MacosBaseBot:
    """Installs raspbain on an sd card
    """
    def __init__(self, sd_card_name="RASPBIAN"):
        self.sd_card_name = sd_card_name

    def disk_number(self):
        """Find the most likey place the sd card is mounted.

        Returns
        -------

        """
        diskutil_list = subprocess.Popen("diskutil list", shell=True, stdout=subprocess.PIPE)
        outp = diskutil_list.stdout
        external_disks = []
        for line in outp:
            external_disk = "(external, physical)"
            decoded_line = line.decode()
            if external_disk in decoded_line:
                disk_num = decoded_line.split(external_disk)[0].split("disk")[1]
                if int(disk_num):
                    external_disks.append(disk_num.replace(" ", ""))

        if not external_disks:
            raise Exception("Can't find usb drive in diskutil")

        return external_disks[0]

    def disk_path(self):
        disk_path = f"/dev/disk{self.disk_number()}"

        return disk_path

    def erase_disk(self):
        print("Wipe sd card and format to MS-DOS (FAT16)\n")
        subprocess.Popen(["diskutil eraseDisk ExFAT {} MBRFormat {}".format(self.sd_card_name, self.disk_path())],
                         shell=True, stdout=subprocess.PIPE).communicate()

    def unmount_disk(self):
        subprocess.Popen([f"diskutil unmountDisk {self.disk_path()}"],
                         shell=True, stdout=subprocess.PIPE).communicate()

    def install_os(self):
        pi_img = []
        for file in os.listdir(os.getcwd()):
            if "ubuntu" in file and ".img" in file:
                pi_img.append(file)

        if not pi_img:
            raise Exception("Cant find the pi img. "
                            "This usually means you're not in the same directory as the python file.")

        file = pi_img[0]
        path_to_image = Path(os.getcwd(), file)
        subprocess.Popen([f"sudo dd bs=1m if={path_to_image} of=/dev/rdisk{self.disk_path()} conv=sync"],
                         shell=True, stdout=subprocess.PIPE).communicate()

    def enable_ssh(self):
        ssh_path = Path("/Volumes/boot/ssh")
        if not os.path.isfile(ssh_path):
            subprocess.Popen(["touch {}".format(ssh_path)],shell=True, stdout=subprocess.PIPE).communicate()

    @staticmethod
    def configure_wifi():
        wpa_supplicant_path = Path("/Volumes/boot/wpa_supplicant.conf")
        if not os.path.isfile(wpa_supplicant_path):
            subprocess.Popen(["touch {}".format(wpa_supplicant_path)],shell=True, stdout=subprocess.PIPE).communicate()

        ssid = input("What is the ssid\n")
        wifi_password = input("What is the wifi password\n")
        wifi_type = input("Enter 1 if your using WPA-PSK\n Enter 2 if your using WPA2-PSK\n")
        if wifi_type == "1":
            network_configuration = 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n' \
                                    'network={\n    ssid=' + '"{}”\n    psk=“{}”\n' \
                '    key_mgmt=WPA-PSK\n'.format(ssid,wifi_password) + '}'

        else:
            network_configuration = 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n' \
                                    'network={\n    ssid=' + '"{}”\n    psk=“{}”\n' \
                                                             '    proto=RSN\n    key_mgmt=WPA-PSK\n' \
                                                             '    pairwise=CCMP\n    group=CCMP\n'.format(ssid,wifi_password) + '}'

        with open(wpa_supplicant_path, "w") as writer:
            writer.write(network_configuration)

    def assistant(self):
        if not self.disk_number():
            raise Exception("Cant find the sd card's mounted disk number")

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

        self.enable_ssh()
        self.configure_wifi()
        self.unmount_disk()



