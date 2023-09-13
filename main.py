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
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()

# Internal imports
from scraper import Scraper
from variables import *

print(f"{Fore.RED}BEGIN{Style.RESET_ALL}")

def compute_passwd(serial: str) -> str:
    return hashlib.md5(serial.encode() + b"6d2df50a-250f-4a30-a5e6-d44fb0960aa0").hexdigest()[:8]


def check_port_open(address: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((address, port)) == 0


def ssh_install_openwrt(password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ROUTER_IP, port=22, username='root', password=password)
    with SCPClient(ssh.get_transport()) as scp_client:
        scp_client.put(FLASH_SCRIPT, "/tmp/flash_firmware.sh")
        scp_client.put(OPENWRT_PATH, "/tmp/openwrt.bin")
    stdin, stdout, stderr = ssh.exec_command("chmod +x /tmp/flash_firmware.sh")
    print("".join(stdout.readlines()))
    stdin, stdout, stderr = ssh.exec_command("/bin/ash /tmp/flash_firmware.sh &")
    print("".join(stdout.readlines()))


def ssh_openwrt_set_passwd(admin_passwd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname="192.168.1.1", port=22, username='root')
    except SSHException as e:  # Force login without password
        ssh.get_transport().auth_none('root')
    with SSHClientInteraction(ssh, timeout=10, display=True) as interact:
        interact.expect('.*root.*')  # expecting root@host1:~
        interact.send('passwd')
        interact.expect(
            ['.*password.*', '.*password.*'])  # expect multiline output both containing the phrase 'password'
        interact.send(admin_passwd)
        interact.expect('.*password.*')  # expect 'Retype password: '
        interact.send(admin_passwd)
        interact.expect('passwd: password for root changed by root')
    ssh.close()


def ssh_openwrt_configure(admin_passwd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname="192.168.1.1", port=22, username='root', password=admin_passwd)
    with SCPClient(ssh.get_transport()) as scp_client:
        scp_client.put(WIFI_SCRIPT, "/tmp/default-wifi.sh")
    stdin, stdout, stderr = ssh.exec_command("chmod +x /tmp/default-wifi.sh")
    print("".join(stdout.readlines()) + "".join(stderr.readlines()))
    print(f"Executing /bin/ash /tmp/default-wifi.sh {WIFI_SSID} {WIFI_PASSWORD} &")
    stdin, stdout, stderr = ssh.exec_command(f"/bin/ash /tmp/default-wifi.sh {WIFI_SSID} {WIFI_PASSWORD} &")
    print("".join(stdout.readlines()) + "".join(stderr.readlines()))
    ssh.close()


def main():
    while not check_port_open(ROUTER_IP, 80):
        time.sleep(3)
    router_info = requests.get(f"{ROUTER_URL}/api/misystem/router_info").json()
    mac = router_info['mac']
    print(mac)
    with Scraper() as instance:
        instance.initial_setup_eu()
        instance.fill_forms()
        stok = instance.auth_to_webadmin()
        instance.sysupgrage(stok)
        time.sleep(120)
        instance.initial_setup_cn()
        instance.fill_forms()
        stok = instance.auth_to_webadmin()
        sn = instance.get_serial()
        print(f'{sn=}')
        enable_ssh = requests.get(
            f"{ROUTER_URL}/;stok={stok}/api/misystem/set_config_iotdev?bssid=any&user_id=any&ssid=-h%0Anvram%20set%20ssh_en%3D1%0Anvram%20commit%0Ased%20-i%20%27s%2Fchannel%3D.%2A%2Fchannel%3D%5C%5C%22debug%5C%5C%22%2Fg%27%20%2Fetc%2Finit.d%2Fdropbear%0A%2Fetc%2Finit.d%2Fdropbear%20start%0A")
        print("enabling ssh:" + enable_ssh.text)
        while not check_port_open(ROUTER_IP, 22):
            time.sleep(3)
        password = compute_passwd(sn)
        print(f'{password=}')
        ssh_install_openwrt(password)
    while not check_port_open("192.168.1.1", 22):
        time.sleep(3)
    #ssh_openwrt_set_passwd("aze")
    #ssh_openwrt_configure("aze")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
