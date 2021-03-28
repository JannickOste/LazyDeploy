from cv2 import matchTemplate, minMaxLoc, TM_SQDIFF_NORMED
import numpy
from PIL import Image
from pyautogui import screenshot
from pyrect import Box
from pytesseract import pytesseract


class ScreenSearch:
    @staticmethod
    def locateBoxOnScreen(rgb_color, min_area):
        search_box = numpy.asarray(Image.new("RGB", min_area, color=rgb_color))
        desktop_image = numpy.asarray(screenshot())

        result = matchTemplate(desktop_image, search_box, TM_SQDIFF_NORMED)

        return minMaxLoc(result)[2]


