# -*- coding:utf-8 -*-
"""
this part is used to achieve the power on/off on DUT in hardware
the method is to control the USB power on/off control by PC
"""
import subprocess
import re
import os
import shutil
import elevate


driver_path = "/sys/bus/usb/drivers/"


def parse_usb_info():
    p = subprocess.Popen("dmesg | grep  \"attached to ttyUSB\"", shell=True, stdout=subprocess.PIPE)
    meg = p.stdout.read()
    pattern = re.compile(r"(usb \d+-\d+: [\w\d\s]+)")
    all_match = re.findall(pattern, meg)
    p.kill()
    return all_match[::-1]


def get_target_usb_id(usb_info, target_usb):
    target_info = ''
    for info in usb_info:
        if target_usb in info:
            target_info = info
            break

    id_head = re.findall(re.compile(r"(\d+-\d+)"), target_info)[0]
    driver_name = re.findall(re.compile(r"\d+-\d+: ([\w\d\s]+) USB"), target_info)[0]
    driver_name = driver_name.lower()

    id_list = []
    driver_info_path = ""
    for path in os.listdir(driver_path):
        if driver_name in path.lower():
            for id in os.listdir(os.path.join(driver_path, path)):
                driver_info_path = os.path.join(driver_path, path)
                if id_head in id[0: len(id_head)]:
                    id_list.append(id)
            break
    return id_list, driver_info_path


def bind_or_unbind_usb(id_list, driver_info_path, action="unbind"):
    assert action in ["bind", "unbind"]
    elevate.elevate(graphical=False)
    path = os.path.join("/tmp", action)
    for id in id_list:
        with open(path, "wb+") as f:
            f.write(id)
        shutil.copy(path, driver_info_path)


def power_off_usb(id_list, driver_info_path):
    bind_or_unbind_usb(id_list, driver_info_path, "unbind")


def power_on_usb(id_list, driver_info_path):
    bind_or_unbind_usb(id_list, driver_info_path, "bind")


if __name__ == '__main__':
    info = parse_usb_info()
    id_list, driver_info_path = get_target_usb_id(info, "ttyUSB1")
    print id_list, driver_info_path
    power_off_usb(id_list, driver_info_path)

    power_on_usb(id_list, driver_info_path)
