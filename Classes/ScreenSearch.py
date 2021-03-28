import cv2
import numpy
from PIL import Image
from pyautogui import screenshot


class ScreenSearch:

    @staticmethod
    def locateBoxOnScreen(self, rgb_color, min_area):
        search_box = numpy.asarray(Image.new("RGB", min_area, color=rgb_color))
        desktop_image = numpy.asarray(screenshot())

        result = cv2.matchTemplate(desktop_image, search_box, cv2.TM_SQDIFF_NORMED)

        return cv2.minMaxLoc(result)[2]

