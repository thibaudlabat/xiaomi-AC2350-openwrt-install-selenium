import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from variables import *

class Scraper:
    def __init__(self):
        #os.environ['MOZ_HEADLESS'] = '1'
        service = Service(executable_path=DRIVER_PATH)
        options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox(service=service, options=options)
        self.wait = WebDriverWait(self.driver, MAX_WAIT)

    def __enter__(self):
        return self

    def click_button(self, xpath):
        print("Looking for button", flush=True)
        element = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, xpath)))
        print(f"clicking on button {element.text}")
        element.click()

    def click_buttons(self, buttons):
        for button in buttons:
            self.click_button(button)

    def fill_field(self, name, value):
        print(f"searching for field with name={name}, and filling it with {value}")
        element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"input[name={name}]")))
        element.send_keys(value)

    def initial_setup_eu(self):
        self.driver.get(f"http://{ROUTER_IP}/init.html#/home")
        print(self.driver.title)
        clicks = {
            "select_country": "/html/body/div/div/div[3]/div[1]/div[1]/a",
            "menu_deroulant": "/html/body/div/div/div[2]/div[2]/div[2]/li",
            "France": "/html/body/div/div/div[2]/div[2]/div[3]/ul[10]/li",
            "next": "/html/body/div/div/div[2]/div[2]/div[3]/button",
            "accept_checkbox": "/html/body/div/div/div[3]/div[1]/div[2]/input",
            "try_it_button": "/html/body/div/div/div[3]/div[2]/a",
            "continue_without_internet": "/html/body/div/div/div[2]/p[2]/a",
            "dhcp": "/html/body/div/div/div[2]/ul/li[2]",
            # "next2": "/html/body/div/div/div[3]"
        }
        self.click_buttons(clicks.values())

    def fill_forms(self):
        ##à décomenter si on choisit 'static id' dans initial_setup_cn
        # fields = {
        #     "ip": "10.42.0.10",
        #     "mask": "255.255.255.0",
        #     "gateway": "10.42.0.1",
        #     "dns1": "10.42.0.1"
        # }
        # for name, value in fields.items():
        #     self.fill_field(name, value)
        self.fill_field("name", "rez")
        #self.click_button("/html/body/div[1]/div/div[1]/form[2]/div/label[2]/div/input")
        self.fill_field("password", "jesaispas")
        self.click_button("/html/body/div/div/div[1]/form/div[2]/button")
                          # "/html/body/div/div/div[3]/div[2]/div[4]/p[1]"])
    
    def fill_forms_ch(self):
        ##à décomenter si on choisit 'static id' dans initial_setup_cn
        # fields = {
        #     "ip": "10.42.0.10",
        #     "mask": "255.255.255.0",
        #     "gateway": "10.42.0.1",
        #     "dns1": "10.42.0.1"
        # }
        # for name, value in fields.items():
        #     self.fill_field(name, value)
        self.fill_field("name", "rez")
        #self.click_button("/html/body/div[1]/div/div[1]/form[2]/div/label[2]/div/input")
        self.fill_field("password", "jesaispas")
        self.click_button("/html/body/div/div/div[1]/form/div[2]/button")
                          # "/html/body/div/div/div[3]/div[2]/div[4]/p[1]"])
        

    def auth_to_webadmin(self) -> str:
        # Second phase
        #print(f"aller à {ROUTER_URL}/web/")
        #self.driver.get(f"{ROUTER_URL}/web/")
        self.driver.get(f"http://miwifi.com/cgi-bin/luci/web")
        time.sleep(1.)
        print("accédé")
        self.fill_field("router_password", "jesaispas")
        self.click_buttons(['//*[@id="btnRtSubmit"]', "/html/body/div[1]/div[1]/div/div/h1/a/img"])
        return self.driver.current_url.split("=")[1].split("/")[0]

    def auth_to_webadmin_ch(self) -> str:
        # Second phase
        #print(f"aller à {ROUTER_URL}/web/")
        #self.driver.get(f"{ROUTER_URL}/web/")
        while (self.driver.current_url != "http://miwifi.com/cgi-bin/luci/web") :
            self.driver.get(f"http://miwifi.com/cgi-bin/luci/web")
            time.sleep(1.)
        self.fill_field("router_password", "jesaispas")
        self.click_buttons(['//*[@id="btnRtSubmit"]', "/html/body/div[1]/div[1]/div/div/h1/a/img"])
        return self.driver.current_url.split("=")[1].split("/")[0]

    def sysupgrage(self, stok: str):
        # Third phase
        self.driver.get(f"{ROUTER_URL}/;stok={stok}/web/setting/upgrade")
        self.click_button('//*[@id="btnUpload"]')
        self.fill_field("image", MI_FIRMWARE)
        self.click_button('//*[@id="uploadFormBtn"]')
        time.sleep(1)
        self.click_buttons(['//*[@id="isreset"]', '//*[@id="btnFlashrom"]'])

    def initial_setup_cn(self):
        #anciennement
        #self.driver.get(f"http://{ROUTER_IP}/init.html#/home")
        self.driver.get("http://miwifi.com/init.html#/home")
        clicks = {
            'Next': '/html/body/div/div/div[2]/div[2]/a',
            'continue_no_internet': '/html/body/div/div/div[2]/p[2]/a',
            #'static ip': '/html/body/div/div/div[2]/ul/li[3]' anciennement
            'dhcp' : '/html/body/div/div/div[2]/ul/li[2]'
        }
        self.click_buttons(clicks.values())

    def get_serial(self) -> str:
        serial_number = self.driver.find_element(By.ID, "routersn")
        while serial_number.text == "--":
            time.sleep(0.3)
        return serial_number.text

    def get_driver(self):
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()
        self.driver.quit()