import os
import logging
import shutil
import psutil

def create_workspace_structure():
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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    game_dir = os.path.join(base_dir, 'game')
    
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
    
    for file in os.listdir(game_dir):
        if file.lower().endswith('.iso'):
            return os.path.join(game_dir, file)
    
    logging.error("No ISO file found in game_to_include or game directory")
    return None

def is_dolphin_running():
    for proc in psutil.process_iter(['pid', 'name']):
        if 'dolphin' in proc.info['name'].lower():
            return True
    return False

def clean_directories():
    if is_dolphin_running():
        print("Dolphin is running. Please close Dolphin before cleaning directories.")
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories = [
        'game', 'roms', 'memcards', 'saves', 'dolphin_setup', '.venv',
        'logs', 'temp', 'cache', 'build', 'dist', 'data', 'assets', '__pycache__'
    ]
    
    for dir_name in directories:
        dir_path = os.path.join(base_dir, dir_name)
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"Deleted directory: {dir_path}")
            except (PermissionError, Exception) as e:
                print(f"Error: {e} - Could not delete {dir_path}")
