import os
import sys
import venv
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def ensure_venv():
    venv_path = os.path.join(os.path.dirname(__file__), '.venv')
    
    # Check if running in venv
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logging.info("Not running in venv, setting up environment...")
        
        # Create venv if it doesn't exist
        if not os.path.exists(venv_path):
            venv.create(venv_path, with_pip=True)
            logging.info(f"Created virtual environment at {venv_path}")
            
            # Get path to venv Python interpreter
            if os.name == 'nt':  # Windows
                python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
            else:  # Unix
                python_path = os.path.join(venv_path, 'bin', 'python')
            
            # Install required packages from requirements.txt
            requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
            if os.path.exists(requirements_path):
                subprocess.check_call([python_path, '-m', 'pip', 'install', '-r', requirements_path])
                logging.info("Installed dependencies from requirements.txt")
            
            # Relaunch script in venv
            os.execv(python_path, [python_path] + sys.argv)
    else:
        logging.info("Running in venv, ensuring required packages are installed...")
        try:
            import requests
        except ImportError:
            install_package("requests")
            import requests

        try:
            import py7zr
        except ImportError:
            install_package("py7zr")

if __name__ == "__main__":
    ensure_venv()