import os
from os import listdir

from Classes.Configuration import Configuration
from Classes.Registry import Registry
from Drivers.BrowserBot import BrowserBot

registry = Registry()

extensionLib: dict = {
    "chrome":
    [
         "https://chrome.google.com/webstore/detail/lastpass-free-password-ma/hdokiejnpimakedhajhdlcegeplioahd?hl=en"
         "https://chrome.google.com/webstore/detail/adblock-plus-free-ad-bloc/cfhdojbkjhnklbpkdaibdccddilifddb?hl=en",
         "https://chrome.google.com/webstore/detail/pop-up-blocker-for-chrome/bkkbcggnhapdmkeljlodobbkopceiche?hl=en",
        "https://chrome.google.com/webstore/detail/darkify/lchabmjccahchaflojonfbepjbbnipfc"
    ],
    "firefox":
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

        browser.installAddonsOnMainExecutable()

        browser.release()

def test():
    binary_location = registry.getInstallLocation("chrome")
    browser = BrowserBot(binary_location)

    browser.installAddonsOnMainExecutable()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Configuration()
    print()
    test()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
