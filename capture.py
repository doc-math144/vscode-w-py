import win32gui
import win32ui
import win32con
import numpy 
import cv2
import logging
from typing import Optional

DOLPHIN_SPECIFIC_TITLE = "Dolphin 2412 | JIT64 DC | OpenGL | HLE | Super Mario Sunburn (GMSE03)"

def capture_dolphin_window_dynamic():
    found_windows = []
    def enum_window_callback(hwnd, results):
        window_text = win32gui.GetWindowText(hwnd)
        if window_text == DOLPHIN_SPECIFIC_TITLE and win32gui.IsWindowVisible(hwnd):
            results.append((hwnd, window_text))
        return True

    win32gui.EnumWindows(enum_window_callback, found_windows)
    
    if not found_windows:
        logging.warning("No visible Dolphin windows found")
        return None

    hwnd = found_windows[0][0]
    
    # Ensure window is not minimized
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    
    # Get window bounds with proper client area
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    point = win32gui.ClientToScreen(hwnd, (left, top))
    left, top = point
    point = win32gui.ClientToScreen(hwnd, (right, bottom))
    right, bottom = point
    
    width = right - left
    height = bottom - top
    
    if width <= 0 or height <= 0:
        logging.error(f"Invalid window dimensions: {width}x{height}")
        return None

    try:
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
        cDC.SelectObject(dataBitMap)
        
        # Add small delay before capture
        time.sleep(0.01)
        
        result = cDC.BitBlt((0, 0), (width, height), dcObj, (0, 0), win32con.SRCCOPY)
        if not result:
            logging.error("BitBlt failed")
            return None

        bmpstr = dataBitMap.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype='uint8')
        img.shape = (height, width, 4)
        
        # Check if image is all black
        if np.mean(img) < 1.0:
            logging.warning("Captured frame appears to be black")
            return None

        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
    except Exception as e:
        logging.error(f"Error capturing window: {e}")
        return None
    finally:
        # Cleanup
        if 'dcObj' in locals(): dcObj.DeleteDC()
        if 'cDC' in locals(): cDC.DeleteDC()
        if 'wDC' in locals(): win32gui.ReleaseDC(hwnd, wDC)
        if 'dataBitMap' in locals(): win32gui.DeleteObject(dataBitMap.GetHandle())
