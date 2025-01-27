import win32gui
import win32ui
import win32con
import numpy as np
import cv2
import logging
from typing import Optional

DOLPHIN_WINDOW_TITLES = ["Dolphin", "Dolphin Emulator"]

def capture_dolphin_window_dynamic(window_title=None) -> Optional[np.ndarray]:
    # Try different possible window titles and log what we find
    possible_titles = [
        "Dolphin 2412",  # Add common Dolphin window titles
        "Dolphin 5.0",  # Version specific title
        "Dolphin - {iso_name}",  # Game specific title
        "Dolphin Emulator",
    ] + ([window_title] if window_title else [])
    
    found_windows = []
    for title in possible_titles:
        try:
            # List all windows with similar titles
            def enum_window_callback(hwnd, results):
                window_text = win32gui.GetWindowText(hwnd)
                if any(t.lower() in window_text.lower() for t in possible_titles):
                    results.append((hwnd, window_text))
                return True

            windows = []
            win32gui.EnumWindows(enum_window_callback, windows)
            found_windows.extend(windows)
            
            # Log what we found
            if windows:
                logging.info(f"Found Dolphin windows: {[w[1] for w in windows]}")
                hwnd = windows[0][0]  # Use the first matching window
                break
        except Exception as e:
            logging.error(f"Error finding window with title {title}: {e}")
            continue
    else:
        if found_windows:
            logging.warning(f"Available windows: {[w[1] for w in found_windows]}")
        else:
            logging.warning("No Dolphin windows found")
        return None

    # Get window bounds accounting for borders
    try:
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        point = win32gui.ClientToScreen(hwnd, (left, top))
        left, top = point
        point = win32gui.ClientToScreen(hwnd, (right, bottom))
        right, bottom = point
        
        width = right - left
        height = bottom - top
        
        if width <= 0 or height <= 0:
            return None

        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (width, height), dcObj, (left, top), win32con.SRCCOPY)

        bmpstr = dataBitMap.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype='uint8')
        img.shape = (height, width, 4)

        # Cleanup
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # Convert and return only if we have valid image data
        if img.size > 0:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return None
        
    except Exception as e:
        logging.error(f"Error capturing window: {e}")
        return None
