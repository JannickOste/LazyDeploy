import os
from time import sleep

import requests
from os import listdir
from os.path import join, exists

from Browser.Exceptions import BrowserNotSupported
from Classes.Configuration import Configuration


class IActions:
    """
    The default interface for actions.
    """
    _bot = None

    def __init__(self, bot):
        self._bot = bot

    """
        Override methods
    """

    def downloadAddons(self, addon_uris: list) -> None:
        raise NotImplementedError

    def installAddons(self, on_bot: bool = False, addon_paths: list = None) -> None:
        raise NotImplementedError

    """
        Default methods
    """

    def goto(self, uri):
        self._bot.driver.get(uri)

    def download(self, uri: str) -> str:
        request = requests.get(uri, allow_redirects=True)
        download_path = self._bot.getConfig("download_path")
        if request.status_code == 200:
            if not os.path.exists(download_path):
                os.mkdir(download_path)

            file_name = uri.split('/')[-1]
            file_path = join(download_path, file_name)

            try:
                open(file_path, "wb").write(request.content)
            except OSError:
                extension = self._getExtensionPrefix()
                file_name = f"{len(listdir(Configuration.getBrowserConfiguration('download_path')))}.{extension}"
                file_path = join(Configuration.getBrowserConfiguration("download_path"), file_name)

                open(file_path, "wb").write(request.content)
            finally:
                if exists(file_path):
                    print(f"[Wrote file]: {file_name} to {file_path}")

                    self._bot.downloads[file_name] = file_path
                else:
                    print(f"[Failed to write file]: {file_name} to {file_path}")

                return file_path

    def downloadExecutables(self, exec_uris) -> None:
        for uri, target in exec_uris:
            self.goto(uri)
            if target is None:
                sleep(2)

    def _getExtensionPrefix(self, extracted: bool = False):
        from Browser.Actions.FirefoxActions import FirefoxActions
        from Browser.Actions.ChromeActions import ChromeActions

        if issubclass(self.__class__, FirefoxActions):
            return "xpi"
        elif issubclass(self.__class__, ChromeActions):
            return "zip" if extracted else "crx"
        else:
            raise BrowserNotSupported.BrowerNotSupported(f"No prefix found for "
                                                         f"{self.__class__.__name__.replace('Actions', '')}")
