#!/usr/bin/env python3

__author__ = "Rodrigo H Padilla"
__email__ = "rod.hpadilla@gmail.com"


import csv
import time
from netmiko import ConnectHandler
from devices import device_list


DATE = str(time.strftime("%Y-%d-%m"))
OUTPUT_FILENAME = f"inventor_{DATE}.csv"
REPORT_FIELDS = [
    "DEVICE",
    "HOSTNAME",
    "SN",
    "UPTIME",
    "INTF",
    "INTF_IPADDR",
]


def get_intf_and_ipddr(parse_sh_ip_int_br):
    try:
        for line in parse_sh_ip_int_br:
            if "up" in line["status"] and "up" in line["proto"]:
                intf = line["intf"]
                ipaddr = line["ipaddr"]
                return intf, ipaddr
        return "unknown", "unknown"

    except Exception:
        return "unknown-E", "unknown-E"


def get_hostname_model_sn(parse_sh_ver):
    try:
        for line in parse_sh_ver:
            hostname = line["hostname"]
            sn = line["serial"]
            uptime = line["uptime"]

        return hostname, sn, uptime
    except Exception as e1:
        print(e1)
        return "unknown-E", "unknown-E", "unknown-E"


def inventor():

    with open(OUTPUT_FILENAME, "w", newline="") as f1:
        writer = csv.DictWriter(f1, REPORT_FIELDS)
        writer.writeheader()

        for device in device_list:
            host = device["host"].upper()
            with ConnectHandler(**device) as net_connect:
                # SHOW IP INT BR
                parse_show_ip_int_br = net_connect.send_command(
                    "show ip interface brief", expect_string=r"#", use_textfsm=True
                )
                intf, ipaddr = get_intf_and_ipddr(parse_show_ip_int_br)
                # SHOW VERSION
                parse_sh_ver = net_connect.send_command(
                    "show version", expect_string=r"#", use_textfsm=True
                )
                hostname, sn, uptime = get_hostname_model_sn(parse_sh_ver)

            writer.writerow(
                {
                    "DEVICE": host,
                    "HOSTNAME": hostname,
                    "SN": sn,
                    "UPTIME": uptime,
                    "INTF": intf,
                    "INTF_IPADDR": ipaddr,
                }
            )
            print(f"SUCCESS --> {host}")


if __name__ == "__main__":
    inventor()
