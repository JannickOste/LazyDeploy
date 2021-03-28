import shutil
import subprocess
import zipfile
from abc import ABC
from os import environ, remove, listdir
from os.path import exists, join
from time import sleep

from selenium.webdriver.common.by import By

from Browser.Actions.IActions import IActions


class ChromeActions(IActions, ABC):
    def __init__(self, bot):
        super().__init__(bot)

    def installAddons(self, on_bot: bool = False):
        download_path = self._bot.getConfig("download_path")
        downloads = listdir(download_path)

        if not on_bot:
            self._bot.release()

        for file in [file for file in downloads if file.lower().endswith(self._getExtensionPrefix(True))]:
            extension_path = join(download_path, file)
            file_name = extension_path.replace("\\", "/").split("/")[-1].split(".")[0]
            extract_path = join(download_path, file_name)
            if not exists(extract_path):
                with zipfile.ZipFile(extension_path, "r") as zip_obj:
                    zip_obj.extractall(extract_path)

            subprocess.call([self.__binary_path, f'--load-extension="{extract_path}"'])

        if self._bot.driver is not None:
            self._bot.start()

    def downloadAddons(self, addon_uris: list) -> None:
        for addon_uri in addon_uris:
            web: bool = any([addon_uri.startswith(prefix) for prefix in ["http", "https", "www"]])
            if not web:
                continue

            print(f"[Attempting download]: {addon_uri}")

            self.goto("https://crxextractor.com/")
            self._bot.driver.find_element(By.CLASS_NAME, "button-primary").click()

            sleep(1)

            self._bot.driver.find_element(By.CSS_SELECTOR, "#crx-download-input").send_keys(addon_uri)
            self._bot.driver.find_element(By.CSS_SELECTOR, ".download-crx-ok").click()

            addon_uri = self._bot.driver.find_element(By.CSS_SELECTOR, ".download-crx").get_attribute("href")
            self.__convertChromeExtension(self.download(addon_uri))

    def __convertChromeExtension(self, file_path):
        print(f"[Converting extension]: {file_path}")

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
