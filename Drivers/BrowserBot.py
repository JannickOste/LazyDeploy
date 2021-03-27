from datetime import datetime
from os import listdir
from os.path import join
from platform import platform
from time import sleep

import pyautogui as pyautogui
from selenium.webdriver import DesiredCapabilities, FirefoxProfile
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

    __binary_path = None

    __target_driver: selenium.webdriver = None
    __driver_name: str = None

    def __init__(self, browser_exec: str):
        assert browser_exec is None or os.path.exists(browser_exec)

        self.__binary_path = browser_exec
        self.__driver_name = browser_exec.split("\\")[-1].lower()
        driver = self.__browser_drivers.get(self.__driver_name)
        driver_kwargs = {
            "stripped_name": self.__driver_name.split(".")[0],
            "executable_path": Configuration.getDriverPath(driver_name=self.__driver_name.split(".")[0])
        }
        self.__target_driver = driver(executable_path=driver_kwargs["executable_path"], **self.__getProfile(driver))
        self.__target_driver.maximize_window()

    def __getProfile(self, driver: selenium.webdriver):
        """
        Fetch driver specific profile
        :param driver:
        :return:
        """
        profile: dict = {}
        if isinstance(driver, selenium.webdriver.Firefox):
            profile = {"firefox_options" : selenium.webdriver.FirefoxProfile()}
            profile["firefox_options"].set_preference("browser.download.folderList", 2)
            profile["firefox_options"].set_preference("browser.download.dir", Configuration.getBrowserConfiguration("download_path"))
            profile["firefox_options"].set_preference("browser.download.manager.showWhenStarting", False)
            profile["firefox_options"].set_preference("browser.helperApps.neverAsk.saveToDisk", "*")
        elif isinstance(driver, selenium.webdriver.Chrome):
            profile = {"chrome_options" : selenium.webdriver.ChromeOptions()}
            profile["chrome_options"].add_experimental_option("prefs", {
              "download.default_directory": Configuration.getBrowserConfiguration("download_path"),
              "download.prompt_for_download": False,
              "download.directory_upgrade": True,
              "safebrowsing.enabled": True
            })
        elif isinstance(driver, selenium.webdriver.Ie):
            profile =  {"ie_options" : selenium.webdriver.IeOptions()}

        return profile


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

    def __getExtensionPrefix(self) -> str:
        driver_name = self.__driver_name.split(".")[0]
        if driver_name == "chrome":
            return "crx"
        elif driver_name == "firefox":
            return "ipx"
        else:
            raise Exception("Browser not supported")

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
            if self.__driver_name == "firefox.exe":
                self.goto(addon_uri)
                return self.__target_driver.find_element(By.LINK_TEXT, "Add to Firefox").get_attribute("href")
            elif self.__driver_name == "chrome.exe":
                self.goto("https://crxextractor.com/")
                self.__target_driver.find_element(By.CLASS_NAME, "button-primary").click()
                sleep(1)
                self.__target_driver.find_element(By.CSS_SELECTOR, "#crx-download-input").send_keys(addon_uri)
                self.__target_driver.find_element(By.CSS_SELECTOR, ".download-crx-ok").click()
                return self.__target_driver.find_element(By.CSS_SELECTOR, ".download-crx").get_attribute("href")

    def downloadFile(self, uri: str):
        request = requests.get(uri, allow_redirects=True)
        if request.status_code == 200:
            file_name = uri.split('/')[-1]
            file_path = join(Configuration.getBrowserConfiguration("download_path"), file_name)

            try:
                open(file_path, "wb").write(request.content)
            except OSError:
                extension = self.__getExtensionPrefix()
                file_name = f"{len(listdir(Configuration.getBrowserConfiguration('download_path')))}.{extension}"

                open(join(Configuration.getBrowserConfiguration("download_path"), file_name), "wb").write(request.content)

            print(f"[Wrote file]: {file_name} to {file_path}")

    def installAddonsOnMainExecutable(self):
        driver_name = self.__driver_name.split(".")[0]
        for file in [file for file in listdir(Configuration.getBrowserConfiguration("download_path")) if file.lower().endswith(self.__getExtensionPrefix())]:
            print(file)
            extension_path = os.path.join(Configuration.getBrowserConfiguration("download_path"), file)
            if driver_name == "firefox":
                os.system(f'start "{self.__binary_path}" "{extension_path}"')
            elif driver_name == "chrome":
                self.goto("https://crxextractor.com/")

                self.__target_driver.find_element(By.CLASS_NAME, "button-primary").click()
                sleep(1)
                print(self.__target_driver.find_element(By.ID, "file").send_keys(extension_path))
                sleep(1)
                print(self.__target_driver.find_element(By.CLASS_NAME, "download").click())

            if platform == "win32":
                os.system(f"taskkill -f -im {self.__driver_name}")

    def release(self):
        self.__target_driver.quit()
