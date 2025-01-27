import os
import sys
import subprocess
import logging

def install_package(package):
    try:
        if os.name == 'nt':
            python_path = os.path.join('.venv', 'Scripts', 'python.exe')
        else:
            python_path = os.path.join('.venv', 'bin', 'python')
            
        subprocess.check_call([python_path, "-m", "pip", "install", package])
        logging.info(f"Successfully installed {package}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install {package}: {e}")
        sys.exit(1)

def install_dependencies(requirements_path):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
        logging.info("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install dependencies: {e}")
        sys.exit(1)
