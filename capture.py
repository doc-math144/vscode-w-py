import win32gui
import win32ui
import win32con
import numpy as np
import cv2
import logging
import time
from typing import Optional

# Function to find any Dolphin emulator window
def find_dolphin_window() -> Optional[int]:
    """Find Dolphin emulator window by pattern matching"""
    def enum_windows_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if window_title.startswith("Dolphin 2412") and " | " in window_title:
                results.append(hwnd)
        return True
    
    window_handles = []
    win32gui.EnumWindows(enum_windows_callback, window_handles)
    
    if window_handles:
        return window_handles[0]
    return None

# Get the current Dolphin window title if it exists, otherwise use a default
DOLPHIN_SPECIFIC_TITLE = ""
hwnd = find_dolphin_window()
if hwnd:
    DOLPHIN_SPECIFIC_TITLE = win32gui.GetWindowText(hwnd)
else:
    DOLPHIN_SPECIFIC_TITLE = "Dolphin 2412 | JIT64 DC "  # Fallback value

def capture_dolphin_window():
    # Manual adjustment values - modify these as needed
    CAPTURE_X = 147        # X position to start capture from
    CAPTURE_Y = -10        # Y position to start capture from
    CAPTURE_WIDTH = 3840  # Width of capture region
    CAPTURE_HEIGHT = 2160 # Height of capture region

    TARGET_WIDTH = 1280   # 720p width
    TARGET_HEIGHT = 720  # 720p height

    # Manual crop adjustments (override automatic cropping)
    CROP_X1 = 190 # Adjust as needed
    CROP_X2 = TARGET_WIDTH - 190 # Adjust as needed
    CROP_Y1 = 45 # Adjust as needed
    CROP_Y2 = TARGET_HEIGHT - 45 # Adjust as needed

    hwnd = win32gui.FindWindow(None, DOLPHIN_SPECIFIC_TITLE)
    if not hwnd:
        logging.error("Dolphin window not found")
        return None

    wDC = None
    dcObj = None
    cDC = None
    dataBitMap = None

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
        
        # Resize image to 720p
        resized_img = cv2.resize(img, (TARGET_WIDTH, TARGET_HEIGHT), interpolation=cv2.INTER_AREA)

        # Apply manual crop
        cropped_img = resized_img[CROP_Y1:CROP_Y2, CROP_X1:CROP_X2]

        return cropped_img[..., :3]  # Return without alpha channel

    except Exception as e:
        logging.error(f"Capture failed: {str(e)}")
        return None

    finally:
        # Always clean up resources
        if dcObj: dcObj.DeleteDC()
        if cDC: cDC.DeleteDC()
        if wDC: win32gui.ReleaseDC(hwnd, wDC)
        if dataBitMap: win32gui.DeleteObject(dataBitMap.GetHandle())
