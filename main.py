from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()
from tools import *

def pp_ok() :
    print(f"\t {Fore.GREEN}OK{Style.RESET_ALL}")



FLASH_ALL = True #pour démarrer l'installation au tout début
FLASH_CHINESE = False #pour démarrer l'installation à partir de l'os chinois vierge



if FLASH_ALL:
    print(f"Test de connectivité sur {ROUTER_IP}:80", end="")
    while not check_port_open(ROUTER_IP, 80):
        time.sleep(3)
    pp_ok()

    router_info = requests.get(f"{ROUTER_URL}/api/misystem/router_info").json()
    mac = router_info['mac']
    print(mac)
    instance = Scraper()


    print(f"Etape 1 : Accepter conditions utilisations, continuer sans internet :", end="")
    instance.initial_setup_eu()
    pp_ok()

    print(f"Etape 2 : Setup DHCP, name and password :", end="")
    instance.fill_forms()
    pp_ok()

    print("Sleep(5)", flush=True)
    time.sleep(5.0)
    print("Etape 3 : ", end='', flush=True)
    stok = instance.auth_to_webadmin()
    pp_ok()

    print("Etape 4 : ", end='')
    instance.sysupgrage(stok)
    pp_ok()

    print("Sleep(120)")
    time.sleep(120)
    while not check_port_open(ROUTER_IP, 80):
        print("En attente de l'ouverture du port 80 ", flush=True)
        time.sleep(3)

if FLASH_CHINESE :
    # pour reprendre à l'étape 5 en ayant sauté les étapes
    router_info = requests.get(f"{ROUTER_URL}/api/misystem/router_info").json()
    mac = router_info['mac']
    print(mac)
    instance = Scraper()

if (FLASH_CHINESE or FLASH_ALL) :
    print("Etape 5 (sleep 10) : continue without internet, setup dhcp ", end='', flush=True)
    time.sleep(10.)
    instance.initial_setup_cn()

    print("Etape 6 (sleep 3) : ", end='', flush=True)
    time.sleep(3.)
    instance.fill_forms_ch()

    print("Etape 7 (sleep 20): ", end='', flush=True)
    time.sleep(20.)
    stok = instance.auth_to_webadmin_ch()

    print("Etape 8 (serial number): ", end='', flush=True)
    sn = instance.get_serial()
    print(f'{sn=}')

    print("Etape 9 (enable ssh via requests) : ", end='', flush=True)
    enable_ssh = requests.get(f"http://{ROUTER_IP}/cgi-bin/luci/;stok={stok}/api/misystem/set_config_iotdev?bssid=any&user_id=any&ssid=-h%0Anvram%20set%20ssh_en%3D1%0Anvram%20commit%0Ased%20-i%20%27s%2Fchannel%3D.%2A%2Fchannel%3D%5C%5C%22debug%5C%5C%22%2Fg%27%20%2Fetc%2Finit.d%2Fdropbear%0A%2Fetc%2Finit.d%2Fdropbear%20start%0A")
    pp_ok()

    print("\tenabling ssh:" + enable_ssh.text, flush=True)

    print("Etape 10 : Attendre ouverture port 22 (peut être long) :", flush=True)
    while not check_port_open(ROUTER_IP, 22):
        print("En attente de l'ouverture du port 22", flush=True)
        time.sleep(3)

    password = compute_passwd(sn)
    print(f'{password=}')

print("Etape 11 : install openwrt :", flush=True)
ssh_install_openwrt(password)