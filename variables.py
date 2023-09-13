import os

MAX_WAIT = 15
ROUTER_IP = "192.168.31.1"
ROUTER_URL = f"http://{ROUTER_IP}/cgi-bin/luci"

SCRIPT_PATH = os.path.dirname(__file__)
rel_path = lambda filename: os.path.join(SCRIPT_PATH, filename)
MI_FIRMWARE = rel_path('miwifi_firmware.bin')
OPENWRT_PATH = rel_path('openwrt.bin')
FLASH_SCRIPT = rel_path('flash_firmware.sh')
WIFI_SCRIPT = rel_path('default-wifi.sh')
WIFI_SSID = "FBI"
WIFI_PASSWORD = "jesaispas"

DRIVER_PATH="./bin/geckodriver-v0.33.0-linux64"