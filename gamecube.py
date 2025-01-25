import os
import subprocess
import logging
from dataclasses import dataclass
from typing import Optional

@dataclass
class GameCubeConfig:
    dolphin_path: str
    rom_directory: str
    memcard_directory: str
    controller_config: dict

class GameCubeEmulator:
    def __init__(self, config: GameCubeConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        
    def validate_rom(self, rom_path: str) -> bool:
        """Validate if file is a valid GameCube ROM (.iso, .gcm)"""
        if not os.path.exists(rom_path):
            return False
        return rom_path.lower().endswith(('.iso', '.gcm'))

    def start_game(self, rom_path: str) -> bool:
        if not self.validate_rom(rom_path):
            logging.error(f"Invalid ROM file: {rom_path}")
            return False
        
        command = [
            self.config.dolphin_path,
            "--exec=" + rom_path,
            "--batch",  # Skip GUI
            "--config=Dolphin.Core.GFXBackend=Null",  # Minimal graphics
            "--config=Dolphin.Core.SerialPort1=0",  # Disable Broadband Adapter
        ]
        logging.info(f"Starting game with command: {command}")
        
        try:
            self.process = subprocess.Popen(command)
            return True
        except FileNotFoundError as e:
            logging.error(f"Failed to start Dolphin emulator: {e}")
            return False

    def stop_game(self):
        if self.process:
            self.process.terminate()
            self.process = None

    def setup_memory_card(self, slot: int, path: str):
        """Configure memory card for specified slot"""
        if slot not in [0, 1]:
            raise ValueError("Invalid memory card slot")
        # Set memory card path in Dolphin config
        
    def configure_controller(self, port: int, config: dict):
        """Setup GameCube controller configuration"""
        if port not in range(4):
            raise ValueError("Invalid controller port")
        # Apply controller mapping
