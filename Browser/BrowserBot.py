from os.path import exists
from sys import platform

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

from Browser.Actions.ChromeActions import ChromeActions
from Browser.Actions.FirefoxActions import FirefoxActions
from Browser.Actions.IActions import IActions

from Classes.Configuration import Configuration


class BrowserBot:
    action: IActions = None
    driver: webdriver = None

    __driver_conf: dict = {}
    __browser_drivers = \
        {
            "firefox": webdriver.Firefox,
            "chrome" if platform == "win32" else "chromium": webdriver.Chrome,
            "edge": webdriver.Edge,
            "iexplore": webdriver.Ie
        }

    __downloads: dict = {}

    def __init__(self, browser_exec: str):
        if platform == "win32":
            assert browser_exec is None or exists(browser_exec)

        driver_name = browser_exec.split("\\" if platform == "win32" else "/")[-1]
        self.__driver_conf = {
            "selenium_driver": self.__browser_drivers.get(driver_name),
            "binary": browser_exec,
            "executable_name": driver_name.split(".")[0],
            "executable_file": driver_name,
            "executable_path": Configuration.getDriverPath(driver_name="chrome" if platform != "win32" and driver_name == "chromium" else driver_name.split(".")[0]),
            **Configuration.getBrowserConfiguration("")
        }

    """
        Public methods.
    """

    def start(self):
        driver = self.__browser_drivers.get(self.__driver_conf.get("executable_name"))
        print("path", self.__driver_conf["executable_path"])
        self.driver = driver(**self.__getProfile(driver), executable_path=self.__driver_conf["executable_path"])

        self.driver.maximize_window()

        print(f"[{self.driver.name}]: Launching agent")
        self.action = self.__getActions(self.driver)

    def getConfig(self, config_name):
        return self.__driver_conf.get(config_name)

    def release(self, clear_downloads: bool = False):
        if self.driver is not None:
            self.driver.quit()
        if clear_downloads:
            self.__downloads.clear()

    def __getActions(self, driver: webdriver) -> IActions:
        if isinstance(driver, webdriver.Firefox):
            return FirefoxActions(self)
        elif isinstance(driver, webdriver.Chrome):
            return ChromeActions(self)

    """
        Properties
    """

    @property
    def downloads(self):
        """
        Fetch downloaded files in session.
        :return:
        """
        return self.__downloads

    @downloads.setter
    def downloads(self, val):
        self.__downloads = dict(**self.__downloads, **val)

    def __getProfile(self, driver: webdriver):
        """
        Fetch driver specific profile
        :param driver:
        :return:
        """
        profile: dict = {}
        if isinstance(driver, webdriver.Firefox):
            profile = {"firefox_options": webdriver.FirefoxProfile()}
            profile["firefox_options"].set_preference("browser.download.folderList", 2)
            profile["firefox_options"].set_preference("browser.download.dir", self.getConfig("download_path"))
            profile["firefox_options"].set_preference("browser.download.manager.showWhenStarting", False)
            profile["firefox_options"].set_preference("browser.helperApps.neverAsk.saveToDisk", "*")
        elif isinstance(driver, webdriver.Chrome):
            profile = {"chrome_options": webdriver.ChromeOptions()}
            profile["chrome_options"].add_experimental_option("prefs", {
                'safebrowsing.enabled': True,
                "profile.default_content_settings.popups": 0,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "download.default_directory": Configuration.getBrowserConfiguration("download_path")
            })
        elif isinstance(driver, webdriver.Ie):
            profile = {"ie_options": webdriver.IeOptions()}

        return profile

    def __getCapabilities(self, driver: webdriver):
        # Suppressor for method may be static
        _ = self

        capabilities = DesiredCapabilities()
        if isinstance(driver, webdriver.Firefox):
            capabilities = capabilities.FIREFOX.copy()
        elif isinstance(driver, webdriver.Chrome):
            capabilities = capabilities.CHROME.copy()
        elif isinstance(driver, webdriver.Ie):
            capabilities = capabilities.INTERNETEXPLORER.copy()
        elif isinstance(driver, webdriver.Edge):
            capabilities = capabilities.EDGE.copy()

        return capabilities
