# Python native imports
import hashlib
import socket
import time

# External dependencies
import paramiko
import requests
from paramiko.ssh_exception import SSHException
from scp import SCPClient
from paramiko_expect import SSHClientInteraction


# Internal imports
from scraper import Scraper
from variables import *

def compute_passwd(serial: str) -> str:
    return hashlib.md5(serial.encode() + b"6d2df50a-250f-4a30-a5e6-d44fb0960aa0").hexdigest()[:8]


def check_port_open(address: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((address, port)) == 0


def ssh_install_openwrt(password):
    print("etape a")
    ssh = paramiko.SSHClient()
    print("etape b")
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("etape c")
    ssh.connect(hostname=ROUTER_IP, port=22, username='root', password=password)
    print("etape d")
    with SCPClient(ssh.get_transport()) as scp_client:
        print("etape e")
        scp_client.put(FLASH_SCRIPT, "/tmp/flash_firmware.sh")
        print("etape f")

        scp_client.put(OPENWRT_PATH, "/tmp/openwrt.bin")
    print("etape g")
    stdin, stdout, stderr = ssh.exec_command("chmod +x /tmp/flash_firmware.sh")
    print("etape h")
    print("".join(stdout.readlines()))
    print("etape i")
    stdin, stdout, stderr = ssh.exec_command("/bin/ash /tmp/flash_firmware.sh &")
    print("etape j")
    input("waiting input")
    print("stderr :")
    print("".join(stderr.readlines()))
    print("stdout :")
    print("".join(stdout.readlines()))



def ssh_openwrt_set_passwd(admin_passwd, pwd):
    print("etape a")
    ssh = paramiko.SSHClient()
    print("etape b")
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("etape c")
        ssh.connect(hostname="192.168.31.1", port=22, username='root', password=pwd)
    except SSHException as e:  # Force login without password
        print("etape d (except)")
        ssh.get_transport().auth_none('root')

    with SSHClientInteraction(ssh, timeout=10, display=True) as interact:
        print("etape e")
        interact.expect('.*root.*')  # expecting root@host1:~
        interact.send('passwd')
        interact.expect(['.*password.*', '.*password.*'])  # expect multiline output both containing the phrase 'password'
        interact.send(admin_passwd)
        interact.expect('.*password.*')  # expect 'Retype password: '
        interact.send(admin_passwd)
        interact.expect('passwd: password for root changed by root')
    ssh.close()


def ssh_openwrt_configure(admin_passwd) :
    print("etape a")
    ssh = paramiko.SSHClient()
    print("etape b")
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("etape c")
    ssh.connect(hostname="192.168.31.1", port=22, username='root', password=admin_passwd)
    print("etape d")
    with SCPClient(ssh.get_transport()) as scp_client:
        print("etape e")
        scp_client.put(WIFI_SCRIPT, "/tmp/default-wifi.sh")
    print("etape f")
    stdin, stdout, stderr = ssh.exec_command("chmod +x /tmp/default-wifi.sh")
    print("etape g")
    print("".join(stdout.readlines()) + "".join(stderr.readlines()))
    print("etape h")
    print(f"Executing /bin/ash /tmp/default-wifi.sh {WIFI_SSID} {WIFI_PASSWORD} &")
    print("etape i")
    stdin, stdout, stderr = ssh.exec_command(f"/bin/ash /tmp/default-wifi.sh {WIFI_SSID} {WIFI_PASSWORD} &")
    print("etape j")
    print("".join(stdout.readlines()) + "".join(stderr.readlines()))
    print("etape k (ssh close)")
    ssh.close()
