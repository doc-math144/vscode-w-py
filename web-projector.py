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

from package_manager import install_package, install_dependencies
from file_handler import download_dolphin_setup, extract_7z_file, move_ini_files
from workspace import create_workspace_structure, setup_game_paths, clean_directories
from venv_setup import ensure_venv
from directories import ensure_directories
from gamecube import GameCubeConfig, GameCubeEmulator
from urls import register_routes, register_error_handlers
from capture import capture_dolphin_window_dynamic  # Import the new function

app = Flask(__name__)

register_routes(app)
register_error_handlers(app)

def find_dolphin_path():
    for process in psutil.process_iter(attrs=['pid', 'name', 'exe']):
        if process.info['name'].lower() == 'dolphin.exe':
            return process.info['exe']
    return None

def generate_output():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories = create_workspace_structure()
    
    subprocess.check_call([sys.executable, "venv_setup.py"])
    ensure_venv()
    ensure_directories()

    os.environ['DOLPHIN_GAME_PATH'] = directories['game']
    
    iso_path = setup_game_paths()
    if not iso_path:
        yield "No ISO file found.<br/>\n"
        return

    requirements_path = os.path.join(base_dir, 'requirements.txt')
    install_dependencies(requirements_path)
    
    setup_dir = directories['dolphin_setup']
    dolphin_setup_url = "https://dl.dolphin-emu.org/releases/2412/dolphin-2412-x64.7z"
    dolphin_setup_path = download_dolphin_setup(dolphin_setup_url, setup_dir)
    
    extract_7z_file(dolphin_setup_path, setup_dir)
    move_ini_files(setup_dir)
    
    config = GameCubeConfig(
        dolphin_path=find_dolphin_path() or os.path.join(directories['dolphin_setup'], "Dolphin-x64", "Dolphin.exe"),
        rom_directory=directories['game'],
        memcard_directory=directories['memcards'],
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
    def gen_frames():
        if not os.path.exists(os.path.join(directories['dolphin_setup'], "Dolphin-x64", "Dolphin.exe")):
            logging.error("Dolphin executable not found!")
            return

        # Give Dolphin more time to initialize
        time.sleep(10)  # Increased delay
        
        frame_interval = 1/30
        last_frame = None
        frames_without_window = 0
        
        while True:
            try:
                frame = capture_dolphin_window_dynamic()
                if frame is None:
                    frames_without_window += 1
                    if frames_without_window > 30:  # 3 seconds without finding window
                        logging.warning("Cannot find Dolphin window for 3 seconds")
                        frames_without_window = 0
                    time.sleep(0.1)
                    continue
                
                frames_without_window = 0
                last_frame = frame
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