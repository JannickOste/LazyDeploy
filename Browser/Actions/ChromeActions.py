import shutil
from abc import ABC
from os import environ, remove
from os.path import exists, join
from time import sleep

from selenium.webdriver.common.by import By

from Browser.Actions.IActions import IActions


class ChromeActions(IActions, ABC):
    def __init__(self, bot):
        super().__init__(bot)

    def installAddons(self, on_bot: bool = False):
        print("hi")

    def __convertChromeExtension(self, file_path):
        self.goto("https://crxextractor.com/")
        self._bot.driver.find_element(By.CLASS_NAME, "button-primary").click()
        sleep(1)
        self._bot.driver.find_element(By.ID, "file").send_keys(file_path)
        sleep(1)
        # cannot get href -> blob (browser specific data)
        self._bot.driver.find_element(By.CLASS_NAME, "download").click()

        # Temporary fix for chrome not setting download directory correctly
        # TODO: look into^
        file_name = file_path.replace("\\", "/").split("/")[-1].split('.')[0]
        while not exists(join(environ['USERPROFILE'], "Downloads", f"{file_name}.zip")):
            sleep(0.1)

        shutil.move(join(environ['USERPROFILE'], "Downloads", f"{file_name}.zip"),
                    join(self._bot.getConfig("download_path"), f"{file_name}.zip"))

        remove(file_path)
