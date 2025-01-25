import os
import sys
from venv_setup import ensure_venv
from directories import ensure_directories

# Setup environment first
ensure_venv()
ensure_directories()

# Install dependencies from requirements.txt
requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
os.system(f"{sys.executable} -m pip install -r {requirements_path}")

# Import game dependencies after environment setup
import pygame
from game import Game

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
