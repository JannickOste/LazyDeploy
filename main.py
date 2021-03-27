import os
from os import listdir

from Classes.Configuration import Configuration
from Classes.Registry import Registry
from Drivers.BrowserBot import BrowserBot

registry = Registry()

extensionLib: dict = {
    "firefox":
    [
        "https://addons.mozilla.org/en-US/firefox/addon/lastpass-password-manager/",
        "https://addons.mozilla.org/en-US/firefox/addon/adblock-plus/",
        "https://addons.mozilla.org/en-US/firefox/addon/popup-blocker-ultimate/"
    ],
    "chrome":
    [
            "https://addons.mozilla.org/en-US/firefox/addon/lastpass-password-manager/",
            "https://addons.mozilla.org/en-US/firefox/addon/adblock-plus/",
            "https://addons.mozilla.org/en-US/firefox/addon/popup-blocker-ultimate/"
    ]
}


def downloadExtensions():
    xpi_files = []

    for agent in extensionLib.keys():
        binary_location = registry.getInstallLocation(agent)
        browser = BrowserBot(binary_location)

        for link in extensionLib[agent]:
            xpi_files.append(browser.getAddonFileURI(link))

        for link in xpi_files:
            browser.downloadFile(link)

        for file in [file for file in listdir(Configuration.getAssetPath()) if file.endswith(".xpi")]:
            os.system(f'start "{binary_location}" '
                      f'"{os.path.join(os.path.dirname(os.path.abspath(__file__)), "Assets", "Downloads", file)}"')

        browser.release()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Configuration()
    print()
    downloadExtensions()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
