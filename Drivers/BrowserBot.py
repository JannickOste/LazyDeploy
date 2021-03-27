from datetime import datetime
from os.path import join

import pyautogui as pyautogui
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common import keys, by
import selenium
from PIL import Image
import os
import asyncio, requests

from selenium.webdriver.common.by import By

from Classes.Configuration import Configuration


class BrowserBot:
    __browser_drivers = \
        {
            "firefox.exe": selenium.webdriver.Firefox,
            "chrome.exe": selenium.webdriver.Chrome,
            "edge.exe": selenium.webdriver.Edge,
            "iexplore.exe": selenium.webdriver.Ie
        }

    __exec_path = None

    __target_driver: selenium.webdriver = None
    __driver_name: str = None

    def __init__(self, browser_exec: str):
        assert browser_exec is None or os.path.exists(browser_exec)

        self.__driver_name = browser_exec.split("\\")[-1].lower()
        driver = self.__browser_drivers.get(self.__driver_name)
        self.__target_driver = driver(

            executable_path=Configuration.getDriverPath(driver_name=self.__driver_name.split(".")[0])
        )

    def __getCapabilities(self, driver: selenium.webdriver):
        capabilities = DesiredCapabilities()
        if isinstance(driver, selenium.webdriver.Firefox):
            return capabilities.FIREFOX.copy()
        elif isinstance(driver, selenium.webdriver.Chrome):
            return capabilities.CHROME.copy()
        elif isinstance(driver, selenium.webdriver.Ie):
            return capabilities.INTERNETEXPLORER.copy()
        elif isinstance(driver, selenium.webdriver.Edge):
            return capabilities.EDGE.copy()


    def goto(self, uri):
        self.__target_driver.get(uri)

    def searchImage(self, image_path: str, click: bool = False, timeout: float = 0):
        start = datetime.now()

        # Weird issues with cv2 matchtemplates, gotta look into this due cv2 being faster.
        while True:
            if timeout != 0 and 0 < (datetime.now() - start).seconds < timeout:
                return None

            loc = pyautogui.locateOnScreen(Image.open(image_path), confidence=0.6)
            if loc is not None:
                if click:
                    pyautogui.click(loc.left, loc.top, 2, 0.1)

                return loc

    def getAddonFileURI(self, addon_uri: str) -> str:
        web: bool = any([addon_uri.startswith(prefix) for prefix in ["http", "https", "www"]])

        if not web:
            if os.path.exists(addon_uri):
                self.__target_driver.install_addon(addon_uri)
            else:
                raise Exception("Invalid extension filepath")
        else:
            self.goto(addon_uri)
            if self.__driver_name == "firefox.exe":
                return self.__target_driver.find_element(By.LINK_TEXT, "Add to Firefox").get_attribute("href")

    def downloadFile(self, uri: str):
        request = requests.get(uri, allow_redirects=True)
        if request.status_code == 200:
            file_name = uri.split('/')[-1]
            file_path = join(Configuration.getBrowserConfiguration("download_path"), file_name)
            print(f"[Writing file]: {file_name} to {file_path}")
            open(file_path, "wb").write(request.content)

    def release(self):
        self.__target_driver.quit()
