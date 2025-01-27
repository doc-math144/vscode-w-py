import logging
import time
import numpy as np
from typing import Optional
from flask import Blueprint, render_template, Response
from capture import capture_dolphin_window_dynamic as capture_dolphin_window
import cv2
import win32gui
import win32ui
import win32con

DOLPHIN_WINDOW_TITLES = [
    "Dolphin 2412",
    "Dolphin.exe",
    "Dolphin Emulator",
    "Dolphin - NTSC",
    "Dolphin - PAL"
]

# Create blueprint for routes
main = Blueprint('main', __name__)

# URL patterns
routes = {
    '/': 'index',                    # Main page
    '/video_feed': 'video_feed',     # Video streaming endpoint
    '/static/<path:filename>': 'static' # Static files
}

# Function to register routes with Flask app
def register_routes(app):
    app.register_blueprint(main)

# Error handlers
def handle_404(e):
    return 'Page not found', 404

def handle_500(e):
    return 'Internal server error', 500

# Register error handlers
def register_error_handlers(app):
    app.register_error_handler(404, handle_404)
    app.register_error_handler(500, handle_500)

@main.route('/')
def index():
    return render_template('index.html')

def capture_dolphin_window(window_titles: list = DOLPHIN_WINDOW_TITLES) -> Optional[np.ndarray]:
    for title in window_titles:
        hwnd = win32gui.FindWindow(None, title)
        if hwnd:
            logging.info(f"Found Dolphin window with title: {title}")
            try:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top

                wDC = win32gui.GetWindowDC(hwnd)
                dcObj = win32ui.CreateDCFromHandle(wDC)
                cDC = dcObj.CreateCompatibleDC()
                
                dataBitMap = win32ui.CreateBitmap()
                dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
                cDC.SelectObject(dataBitMap)
                cDC.BitBlt((0, 0), (width, height), dcObj, (0, 0), win32con.SRCCOPY)

                bmpstr = dataBitMap.GetBitmapBits(True)
                img = np.frombuffer(bmpstr, dtype='uint8')
                img.shape = (height, width, 4)

                dcObj.DeleteDC()
                cDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, wDC)
                win32gui.DeleteObject(dataBitMap.GetHandle())

                return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            except Exception as e:
                logging.error(f"Failed to capture window: {e}")
                return None
    
    return None

@main.route('/video_feed')
def video_feed():
    def gen_frames():
        retry_delay = 1.0  # seconds
        while True:
            frame = capture_dolphin_window()
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                logging.warning("No Dolphin window found, retrying...")
                time.sleep(retry_delay)

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
