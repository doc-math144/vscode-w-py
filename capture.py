import win32gui
import win32ui
import win32con
import numpy as np
import cv2
import logging
import time
from typing import Optional

DOLPHIN_SPECIFIC_TITLE = "Dolphin 2412 | JIT64 DC | OpenGL | HLE | Super Mario Sunburn (GMSE03)"

def capture_dolphin_window():
    # Manual adjustment values - modify these as needed
    CAPTURE_X = 0        # X position to start capture from
    CAPTURE_Y = 0        # Y position to start capture from
    CAPTURE_WIDTH = 3840  # Width of capture region
    CAPTURE_HEIGHT = 2160 # Height of capture region

    hwnd = win32gui.FindWindow(None, DOLPHIN_SPECIFIC_TITLE)
    if not hwnd:
        logging.error("Dolphin window not found")
        return None

    try:
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, CAPTURE_WIDTH, CAPTURE_HEIGHT)
        cDC.SelectObject(dataBitMap)
        
        # Capture the specified region using manual values
        cDC.BitBlt((0, 0), (CAPTURE_WIDTH, CAPTURE_HEIGHT), 
                   dcObj, (CAPTURE_X, CAPTURE_Y), win32con.SRCCOPY)

        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')
        img.shape = (CAPTURE_HEIGHT, CAPTURE_WIDTH, 4)
        
        # Cleanup
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        return img[..., :3]  # Return without alpha channel

    except Exception as e:
        logging.error(f"Capture failed: {str(e)}")
        return None
