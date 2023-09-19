from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()
from tools import *

def pp_ok() :
    print(f"  {Fore.GREEN}OK{Style.RESET_ALL}")
if False:
    print(f"Test de connectivité sur {ROUTER_IP}:80", end="")

    while not check_port_open(ROUTER_IP, 80):
        time.sleep(3)

    pp_ok()
    router_info = requests.get(f"{ROUTER_URL}/api/misystem/router_info").json()
    mac = router_info['mac']
    print(mac)
    instance = Scraper()

    print(f"Accepter conditions utilisations, continuer sans internet :", end="")
    instance.initial_setup_eu()
    pp_ok()

    print(f"Setup DHCP, name and password :", end="")
    instance.fill_forms()
    pp_ok()

    print("Etape 3 : ", end='')
    input("waiting input")
    stok = instance.auth_to_webadmin()
    pp_ok()

    print("Etape 4 : ", end='')
    input("waiting input")
    instance.sysupgrage(stok)
    pp_ok()

    print("Sleep(120)")
    time.sleep(120)

if False :
    #pour reprendre à l'étape 5
    router_info = requests.get(f"{ROUTER_URL}/api/misystem/router_info").json()
    mac = router_info['mac']
    print(mac)
    instance = Scraper()
    #fin de "pour reprendre à l'étape 5"

    print("Etape 5 : ", end='')
    instance.initial_setup_cn()
    pp_ok()

    print("Etape 6 : ", end='')
    instance.fill_forms()
    pp_ok()

    print("Etape 7 : ", end='')
    time.sleep(3.0)
    input("waiting input")
    stok = instance.auth_to_webadmin()
    pp_ok()

    print("Etape 8 (serial number): ", end='')
    input("waiting input")
    sn = instance.get_serial()
    print(f'{sn=}')
    pp_ok()

    print("Etape 9 (enable ssh) : ", end='')
    input("waiting input")
    enable_ssh = requests.get(
        f"{ROUTER_URL}/;stok={stok}/api/misystem/set_config_iotdev?bssid=any&user_id=any&ssid=-h%0Anvram%20set%20ssh_en%3D1%0Anvram%20commit%0Ased%20-i%20%27s%2Fchannel%3D.%2A%2Fchannel%3D%5C%5C%22debug%5C%5C%22%2Fg%27%20%2Fetc%2Finit.d%2Fdropbear%0A%2Fetc%2Finit.d%2Fdropbear%20start%0A")
    pp_ok()

    print("enabling ssh:" + enable_ssh.text)

    print("Etape 10 : Attendre ouverture port 22 :")
    input("waiting input")
    while not check_port_open(ROUTER_IP, 22):
        print("Attend ouverture port 22", flush=True)
        time.sleep(3)
    pp_ok()


    password = compute_passwd(sn)
    print(f'{password=}')#caa32873

print("Etape 11 : install openwrt :")
input("waiting input")
ssh_install_openwrt("aze")
# pp_ok()

# while not check_port_open("192.168.31.1", 22):
#     print("Waiting for port 22 to open", flush=True)
#     time.sleep(3)



# print("Etape 12 : set openwrt passwords")
# input("waiting input")
# ssh_openwrt_set_passwd("aze", password)

# print("Etape 13 : configure openwrt ")
# input("waiting input")
# ssh_openwrt_configure("aze")

