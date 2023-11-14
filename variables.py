import os

DEBUG = False
HEADLESS_MODE = False  #pour rendre la simulation du navigateur headless


MAX_WAIT = 120
ROUTER_IP = "192.168.31.1"
ROUTER_URL = f"http://{ROUTER_IP}/cgi-bin/luci"

SCRIPT_PATH = os.path.dirname(__file__)
rel_path = lambda filename: os.path.join(SCRIPT_PATH, filename)


MI_FIRMWARE = os.path.abspath(rel_path('bin/miwifi_firmware.bin'))
OPENWRT_PATH = os.path.abspath(rel_path('bin/openwrt.bin'))
FLASH_SCRIPT = os.path.abspath(rel_path('flash_firmware.sh'))
WIFI_SCRIPT = os.path.abspath(rel_path('default-wifi.sh'))


WIFI_SSID = "FBI"
WIFI_PASSWORD = "jesaispas"

DRIVER_PATH="./bin/geckodriver-v0.33.0-linux64"