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
    CAPTURE_X = 147        # X position to start capture from
    CAPTURE_Y = 0        # Y position to start capture from
    CAPTURE_WIDTH = 3840  # Width of capture region
    CAPTURE_HEIGHT = 2160 # Height of capture region

    TARGET_WIDTH = 1280   # 720p width
    TARGET_HEIGHT = 720  # 720p height

    # Enforce 4:3 aspect ratio
    aspect_ratio = 4 / 3
    current_aspect_ratio = TARGET_WIDTH / TARGET_HEIGHT

    if current_aspect_ratio > aspect_ratio:
        # Wider than 4:3, crop width
        new_width = int(TARGET_HEIGHT * aspect_ratio)
        crop_x1 = (TARGET_WIDTH - new_width) // 2
        crop_x2 = crop_x1 + new_width
        CROP_X1 = crop_x1
        CROP_X2 = crop_x2
        CROP_Y1 = 0
        CROP_Y2 = TARGET_HEIGHT
    elif current_aspect_ratio < aspect_ratio:
        # Taller than 4:3, crop height (not common, but handled)
        new_height = int(TARGET_WIDTH / aspect_ratio)
        crop_y1 = (TARGET_HEIGHT - new_height) // 2
        crop_y2 = crop_y1 + new_height
        CROP_X1 = 0
        CROP_X2 = TARGET_WIDTH
        CROP_Y1 = crop_y1
        CROP_Y2 = crop_y2
    else:
        # Already 4:3, no crop needed
        CROP_X1 = 0
        CROP_X2 = TARGET_WIDTH - 0
        CROP_Y1 = 0
        CROP_Y2 = TARGET_HEIGHT - 0

    # Manual crop adjustments (override automatic cropping)
    CROP_X1 = 190 # Adjust as needed
    CROP_X2 = TARGET_WIDTH - 190 # Adjust as needed
    CROP_Y1 = 30 # Adjust as needed
    CROP_Y2 = TARGET_HEIGHT - 30 # Adjust as needed

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

        # Resize image to 720p
        resized_img = cv2.resize(img, (TARGET_WIDTH, TARGET_HEIGHT), interpolation=cv2.INTER_AREA)

        # Apply manual crop
        cropped_img = resized_img[CROP_Y1:CROP_Y2, CROP_X1:CROP_X2]

        return cropped_img[..., :3]  # Return without alpha channel

    except Exception as e:
        logging.error(f"Capture failed: {str(e)}")
        return None
