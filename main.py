import os
import sys
import subprocess
import logging
import shutil

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

def create_workspace_structure():
    """Create all required directories in workspace"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories = {
        'game': os.path.join(base_dir, 'game'),
        'roms': os.path.join(base_dir, 'roms'),
        'memcards': os.path.join(base_dir, 'memcards'),
        'saves': os.path.join(base_dir, 'saves'),
        'dolphin_setup': os.path.join(base_dir, 'dolphin_setup')
    }
    
    for name, path in directories.items():
        if not os.path.exists(path):
            os.makedirs(path)
            logging.info(f"Created directory: {path}")
    
    return directories

def setup_game_paths():
    """Setup and verify all game-related paths"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    game_dir = os.path.join(base_dir, 'game')
    
    # Find ISO file in game_to_include
    source_dir = os.path.join(base_dir, 'game_to_include')
    if os.path.exists(source_dir):
        for file in os.listdir(source_dir):
            if file.lower().endswith('.iso') and file.lower() != 'exemple.iso':
                source_file = os.path.join(source_dir, file)
                target_file = os.path.join(game_dir, file)
                if not os.path.exists(target_file):
                    shutil.copy(source_file, target_file)
                    logging.info(f"Copied {file} to game directory")
                return target_file
    
    # If no ISO file found in game_to_include, check game directory
    for file in os.listdir(game_dir):
        if file.lower().endswith('.iso'):
            return os.path.join(game_dir, file)
    
    logging.error("No ISO file found in game_to_include or game directory")
    return None

def move_ini_files(dolphin_setup_dir):
    """Move all .ini files to dolphin_setup\Dolphin-x64\Sys\Profiles\GCpad\ and create folder if it doesn't exist"""
    ini_source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles_to_include')
    ini_target_dir = os.path.join(dolphin_setup_dir, 'Dolphin-x64', 'Sys', 'Profiles', 'GCpad')
    
    if not os.path.exists(ini_target_dir):
        os.makedirs(ini_target_dir)
        logging.info(f"Created directory: {ini_target_dir}")
    
    for file in os.listdir(ini_source_dir):
        if file.lower().endswith('.ini'):
            source_file = os.path.join(ini_source_dir, file)
            target_file = os.path.join(ini_target_dir, file)
            if not os.path.exists(target_file):
                shutil.copy(source_file, target_file)
                logging.info(f"Copied {file} to {ini_target_dir}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Define base_dir here
    
    # Create workspace structure first
    directories = create_workspace_structure()
    
    # Run venv_setup.py to ensure virtual environment and directories are set up
    subprocess.check_call([sys.executable, "venv_setup.py"])

    # Create and activate virtual environment
    venv_dir = os.path.join(os.path.dirname(__file__), '.venv')
    
    # Ensure venv exists and dependencies are installed
    ensure_venv()
    ensure_directories()

    # Set DOLPHIN_GAME_PATH environment variable to workspace game directory
    os.environ['DOLPHIN_GAME_PATH'] = directories['game']
    
    # Setup game paths and move ISO file
    iso_path = setup_game_paths()
    if not iso_path:
        sys.exit(1)

    # Use system Python executable
    python_path = sys.executable
    
    # Install dependencies in venv
    requirements_path = os.path.join(base_dir, 'requirements.txt')
    subprocess.check_call([python_path, "-m", "pip", "install", "-r", requirements_path])
    
    # Create directory for Dolphin setup file
    setup_dir = directories['dolphin_setup']

    # Download Dolphin setup file
    dolphin_setup_url = "https://dl.dolphin-emu.org/releases/2412/dolphin-2412-x64.7z"
    dolphin_setup_path = download_dolphin_setup(dolphin_setup_url, setup_dir)
    
    # Extract setup file
    extract_7z_file(dolphin_setup_path, setup_dir)    
    # Move .ini files to the appropriate directory
    move_ini_files(setup_dir)
    
    # Configure emulator paths using workspace directories
    config = GameCubeConfig(
        dolphin_path=os.path.join(directories['dolphin_setup'], "Dolphin-x64", "Dolphin.exe"),
        rom_directory=directories['game'],
        memcard_directory=directories['memcards'],
        controller_config={
            0: {"type": "GCPad", "device": 0}
        }
    )
    
    emulator = GameCubeEmulator(config)
    
    # Launch Dolphin with the ISO file
    if os.path.exists(config.dolphin_path):
        emulator.start_game(iso_path)
    else:
        logging.error(f"Dolphin executable not found at: {config.dolphin_path}")

    # Remove redundant game path check since we're using workspace path
    if not os.path.exists(directories['game']):
        logging.error("Game directory not found in workspace")
        sys.exit(1)

if __name__ == "__main__":
    main()
