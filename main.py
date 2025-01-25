import os
import sys
import subprocess
import logging

# Ensure required packages are installed
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import requests
except ImportError:
    install_package("requests")
    import requests

try:
    import py7zr
except ImportError:
    install_package("py7zr")
    
from venv_setup import ensure_venv
from directories import ensure_directories
from gamecube import GameCubeConfig, GameCubeEmulator

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def install_dependencies(requirements_path):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
        logging.info("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install dependencies: {e}")
        sys.exit(1)

def download_dolphin_setup(url, setup_dir):
    local_filename = os.path.join(setup_dir, url.split('/')[-1])
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    logging.info(f"Downloaded Dolphin setup file to: {local_filename}")
    return local_filename

def extract_7z_file(file_path, extract_to):
    with py7zr.SevenZipFile(file_path, mode='r') as archive:
        archive.extractall(path=extract_to)
    logging.info(f"Extracted {file_path} to {extract_to}")

def create_dolphin_setup_directory():
    setup_dir = os.path.join(os.path.dirname(__file__), 'dolphin_setup')
    if not os.path.exists(setup_dir):
        os.makedirs(setup_dir)
        logging.info(f"Created directory for Dolphin setup: {setup_dir}")
    return setup_dir

def main():
    # Setup environment first
    ensure_venv()
    ensure_directories()

    # Install dependencies from requirements.txt
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    install_dependencies(requirements_path)

    # Create directory for Dolphin setup file
    setup_dir = create_dolphin_setup_directory()

    # Download Dolphin setup file
    dolphin_setup_url = "https://dl.dolphin-emu.org/releases/2412/dolphin-2412-x64.7z"  # Replace with actual URL
    dolphin_setup_path = download_dolphin_setup(dolphin_setup_url, setup_dir)

    # Extract and use the downloaded Dolphin setup file
    extract_7z_file(dolphin_setup_path, setup_dir)
    dolphin_path = os.path.join(setup_dir, "Dolphin-x64", "Dolphin.exe")

    # Configure and start the emulator
    config = GameCubeConfig(
        dolphin_path=dolphin_path,
        rom_directory=os.path.join(setup_dir, "roms"),
        memcard_directory=os.path.join(setup_dir, "memcards"),
        controller_config={
            0: {"type": "GCPad", "device": 0}
        }
    )
    emulator = GameCubeEmulator(config)
    game_path = "C:/Users/docma/Desktop/dolphin-2407-x64/jeu gamecube rom/Super Mario Sunburn (70 S.iso"
    if game_path:
        emulator.start_game(game_path)

if __name__ == "__main__":
    main()
