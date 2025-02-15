from flask import Flask, Response, render_template, Blueprint
import subprocess
import os
import sys
import logging
import cv2
import numpy as np
import threading
import win32gui
import win32ui
import win32con
import time
import psutil

DOLPHIN_SPECIFIC_TITLE = "Dolphin 2412 | JIT64 DC | OpenGL | HLE | Super Mario Sunburn (GMSE03)"

def capture_dolphin_window():
    CAPTURE_X = 147
    CAPTURE_Y = -10
    CAPTURE_WIDTH = 3840
    CAPTURE_HEIGHT = 2160

    TARGET_WIDTH = 1280
    TARGET_HEIGHT = 720

    aspect_ratio = 4 / 3
    current_aspect_ratio = TARGET_WIDTH / TARGET_HEIGHT

    if (current_aspect_ratio > aspect_ratio):
        new_width = int(TARGET_HEIGHT * aspect_ratio)
        crop_x1 = (TARGET_WIDTH - new_width) // 2
        crop_x2 = crop_x1 + new_width
        CROP_X1 = crop_x1
        CROP_X2 = crop_x2
        CROP_Y1 = 0
        CROP_Y2 = TARGET_HEIGHT
    elif (current_aspect_ratio < aspect_ratio):
        new_height = int(TARGET_WIDTH / aspect_ratio)
        crop_y1 = (TARGET_HEIGHT - new_height) // 2
        crop_y2 = crop_y1 + new_height
        CROP_X1 = 0
        CROP_X2 = TARGET_WIDTH
        CROP_Y1 = crop_y1
        CROP_Y2 = crop_y2
    else:
        CROP_X1 = 0
        CROP_X2 = TARGET_WIDTH - 0
        CROP_Y1 = 0
        CROP_Y2 = TARGET_HEIGHT - 0

    CROP_X1 = 190
    CROP_X2 = TARGET_WIDTH - 190
    CROP_Y1 = 45
    CROP_Y2 = TARGET_HEIGHT - 45

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
        
        cDC.BitBlt((0, 0), (CAPTURE_WIDTH, CAPTURE_HEIGHT), 
                   dcObj, (CAPTURE_X, CAPTURE_Y), win32con.SRCCOPY)

        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')
        img.shape = (CAPTURE_HEIGHT, CAPTURE_WIDTH, 4)
        
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        resized_img = cv2.resize(img, (TARGET_WIDTH, TARGET_HEIGHT), interpolation=cv2.INTER_AREA)

        cropped_img = resized_img[CROP_Y1:CROP_Y2, CROP_X1:CROP_X2]

        return cropped_img[..., :3]

    except Exception as e:
        logging.error(f"Capture failed: {str(e)}")
        return None

app = Flask(__name__)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/video_feed')
def video_feed():
    directories = {
        'dolphin_setup': os.path.join(os.getcwd(), 'dolphin_setup')
    }
    
    def gen_frames():
        if not os.path.exists(os.path.join(directories['dolphin_setup'], "Dolphin-x64", "Dolphin.exe")):
            logging.error("Dolphin executable not found!")
            return

        time.sleep(3)
        
        frame_interval = 1/60
        frames_without_window = 0
        
        while True:
            try:
                frame = capture_dolphin_window()
                if frame is None:
                    frames_without_window += 1
                    if frames_without_window > 30:
                        logging.warning("Cannot find Dolphin window for 3 seconds")
                        frames_without_window = 0
                    time.sleep(0.1)
                    continue
                
                frames_without_window = 0
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if not ret:
                    continue
                
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(frame_interval)
                
            except Exception as e:
                logging.error(f"Stream error: {e}")
                time.sleep(0.1)
                continue
    
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

routes = {
    '/': 'index',
    '/video_feed': 'video_feed',
    '/static/<path:filename>': 'static'
}

def register_routes(app):
    app.register_blueprint(main)

def handle_404(e):
    return 'Page not found', 404

def handle_500(e):
    return 'Internal server error', 500

def register_error_handlers(app):
    app.register_error_handler(404, handle_404)
    app.register_error_handler(500, handle_500)

register_routes(app)
register_error_handlers(app)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)
