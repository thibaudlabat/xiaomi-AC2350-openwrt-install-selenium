# Python native imports
import hashlib
import socket
import time



# External dependencies
import paramiko
import re
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
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("[ssh] Connection à la box en ssh ")
    ssh.connect(hostname=ROUTER_IP, port=22, username='root', password=password)

    with SCPClient(ssh.get_transport()) as scp_client:
        scp_client.put(FLASH_SCRIPT, "/tmp/flash_firmware.sh")
        scp_client.put(OPENWRT_PATH, "/tmp/openwrt.bin")


    channel = ssh.invoke_shell()
    stdin_f = channel.makefile('wb')
    stdout_f = channel.makefile('r')
    def execute(cmd) :
        cmd = cmd.strip('\n')
        stdin_f.write(cmd + '\n')
        finish = 'end of stdOUT buffer. finished with exit status'
        echo_cmd = 'echo {} $?'.format(finish)
        stdin_f.write(echo_cmd + '\n')
        shin = stdin_f
        stdin_f.flush()

        shout = []
        sherr = []
        exit_status = 0
        for line in stdout_f:
            if str(line).startswith(cmd) or str(line).startswith(echo_cmd):
                # up for now filled with shell junk from stdin
                shout = []
            elif str(line).startswith(finish):
                # our finish command ends with the exit status
                exit_status = int(str(line).rsplit(maxsplit=1)[1])
                if exit_status:
                    # stderr is combined with stdout.
                    # thus, swap sherr with shout in a case of failure.
                    sherr = shout
                    shout = []
                break
            else:
                # get rid of 'coloring and formatting' special characters
                shout.append(re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]').sub('', line).
                             replace('\b', '').replace('\r', ''))

        # first and last lines of shout/sherr contain a prompt
        if shout and echo_cmd in shout[-1]:
            shout.pop()
        if shout and cmd in shout[0]:
            shout.pop(0)
        if sherr and echo_cmd in sherr[-1]:
            sherr.pop()
        if sherr and cmd in sherr[0]:
            sherr.pop(0)

        return shin, shout, sherr

    print("[ssh] Changement des permissions sur flash_firmware.sh :")
    shin, shout, sherr = execute("chmod +x /tmp/flash_firmware.sh")
    if DEBUG :
        print(shin, shout, sherr)
    
    print("[ssh] Lance le script flash_firmware.sh")
    shin, shout, sherr = execute("/bin/ash /tmp/flash_firmware.sh &")
    if DEBUG :
        print(shin, shout, sherr)

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
