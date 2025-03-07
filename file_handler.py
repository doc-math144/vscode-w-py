import os
import logging
import shutil
import requests
import py7zr

def download_dolphin_setup(url, setup_dir):
    local_filename = os.path.join(setup_dir, url.split('/')[-1])
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info(f"Downloaded Dolphin setup file to: {local_filename}")
    except ConnectionError:
        logging.error("Network connectivity issue occurred during download.")
    except Exception as e:
        logging.error(f"An error occurred during download: {e}")
    return local_filename

def extract_7z_file(file_path, extract_to):
    try:
        with py7zr.SevenZipFile(file_path, mode='r') as archive:
            archive.extractall(path=extract_to)
        logging.info(f"Extracted {file_path} to {extract_to}")
    except Exception as e:
        logging.error(f"An error occurred during extraction: {e}")

def move_ini_files(dolphin_setup_dir):
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
