import os
import sys
import subprocess
import logging
import threading
import time
import psutil
import argparse
import urls

from package_manager import install_package, install_dependencies
from file_handler import download_dolphin_setup, extract_7z_file, move_ini_files
from workspace import create_workspace_structure, setup_game_paths, clean_directories
from venv_setup import ensure_venv
from directories import ensure_directories
from gamecube import GameCubeConfig, GameCubeEmulator

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(asctime)s - %(message)s')

# Ensure required packages
try:
    import requests
except ImportError:
    install_package("requests")
    import requests

try:
    import py7zr
except ImportError:
    install_package("py7zr")

try:
    import psutil
except ImportError:
    install_package("psutil")

def is_dolphin_running():
    for process in psutil.process_iter(['name']):
        if process.info['name'].lower() == 'dolphin.exe':
            logging.info("Found existing Dolphin instance")
            return True
    return False

def start_web_server():
    try:
        # Wait a bit to ensure Dolphin window is ready
        time.sleep(3)
        if is_dolphin_running():
            subprocess.Popen([sys.executable, "web-projector.py"])
            logging.info("Web streaming server started for existing Dolphin instance")
            return True
        logging.warning("No running Dolphin instance found")
        return False
    except Exception as e:
        logging.error(f"Failed to start web server: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Dolphin Merge Tool")
    parser.add_argument('--clean', action='store_true', help='Clean all created directories')
    args = parser.parse_args()

    if args.clean:
        clean_directories()
        print("All created directories have been cleaned.")
        return
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories = create_workspace_structure()
    
    # First check if Dolphin is already running
    dolphin_running = is_dolphin_running()

    # Continue with setup regardless of Dolphin status
    subprocess.check_call([sys.executable, "venv_setup.py"])
    ensure_venv()
    ensure_directories()

    os.environ['DOLPHIN_GAME_PATH'] = directories['game']
    
    iso_path = setup_game_paths()
    if not iso_path:
        sys.exit(1)

    requirements_path = os.path.join(base_dir, 'requirements.txt')
    install_dependencies(requirements_path)
    
    setup_dir = directories['dolphin_setup']
    dolphin_setup_url = "https://dl.dolphin-emu.org/releases/2412/dolphin-2412-x64.7z"
    
    # Setup Dolphin configuration even if already running
    if not os.path.exists(os.path.join(setup_dir, "Dolphin-x64", "Dolphin.exe")):
        dolphin_setup_path = download_dolphin_setup(dolphin_setup_url, setup_dir)
        extract_7z_file(dolphin_setup_path, setup_dir)
        move_ini_files(setup_dir)

    config = GameCubeConfig(
        dolphin_path=os.path.join(directories['dolphin_setup'], "Dolphin-x64", "Dolphin.exe"),
        rom_directory=directories['game'],
        memcard_directory=directories['memcards'],
        controller_config={
            0: {"type": "GCPad", "device": 0}
        }
    )
    
    emulator = GameCubeEmulator(config)
    # Make it available to the urls module
    urls.emulator_instance = emulator
    
    # Start web server in separate thread
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()

    # Only launch new Dolphin instance if one isn't already running
    if not dolphin_running and os.path.exists(config.dolphin_path):
        try:
            emulator.start_game(iso_path)
            logging.info("Dolphin emulator started successfully")
        except Exception as e:
            logging.error(f"Error starting Dolphin: {e}")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    except Exception as e:
        logging.error(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
