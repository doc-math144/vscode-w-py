from flask import Flask, Response, render_template
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

from gamecube import GameCubeConfig, GameCubeEmulator
from urls import register_routes, register_error_handlers
from capture import capture_dolphin_window  # Import the function from capture.py

app = Flask(__name__)

register_routes(app)
register_error_handlers(app)

def find_dolphin_path():
    for process in psutil.process_iter(attrs=['pid', 'name', 'exe']):
        if process.info['name'].lower() == 'dolphin.exe':
            return process.info['exe']
    return None

def generate_output():
    # Get necessary paths and configurations from environment variables
    dolphin_path = os.environ.get('DOLPHIN_PATH')
    iso_path = os.environ.get('ISO_PATH')
    memcard_directory = os.environ.get('MEMCARD_DIRECTORY')

    if not all([dolphin_path, iso_path, memcard_directory]):
        logging.error("Missing environment variables for Dolphin setup.")
        return

    config = GameCubeConfig(
        dolphin_path=dolphin_path,
        rom_directory=os.path.dirname(iso_path),  # Extract directory from ISO path
        memcard_directory=memcard_directory,
        controller_config={
            0: {"type": "GCPad", "device": 0}
        }
    )

    emulator = GameCubeEmulator(config)
    
    if os.path.exists(config.dolphin_path):
        logging.info(f"Starting Dolphin at: {config.dolphin_path}")
        emulator.start_game(iso_path)
        
        # Wait for Dolphin window to appear
        max_attempts = 30
        for attempt in range(max_attempts):
            if win32gui.FindWindow(None, "Dolphin 2412"):
                logging.info("Dolphin window found!")
                break
            logging.info(f"Waiting for Dolphin window... ({attempt + 1}/{max_attempts})")
            time.sleep(1)
    else:
        logging.error(f"Dolphin executable not found at: {config.dolphin_path}")
        return

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    directories = {
        'dolphin_setup': os.path.join(os.getcwd(), 'dolphin_setup')
    }
    
    def gen_frames():
        if not os.path.exists(os.path.join(directories['dolphin_setup'], "Dolphin-x64", "Dolphin.exe")):
            logging.error("Dolphin executable not found!")
            return

        # Give Dolphin more time to initialize
        time.sleep(10)  # Increased delay
        
        frame_interval = 1/30
        frames_without_window = 0
        
        while True:
            try:
                frame = capture_dolphin_window()
                if frame is None:
                    frames_without_window += 1
                    if frames_without_window > 30:  # 3 seconds without finding window
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

# Make sure to start the game before starting the web server
if __name__ == '__main__':
    # Start Dolphin and game in a separate thread
    def start_emulator():
        generate_output()
    
    emulator_thread = threading.Thread(target=start_emulator)
    emulator_thread.daemon = True
    emulator_thread.start()
    
    # Give the emulator time to start
    time.sleep(5)
    
    # Start the web server
    app.run(debug=True, host='127.0.0.1', port=8000)