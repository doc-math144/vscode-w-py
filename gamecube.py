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
    graphics_backend: str = "OGL"  # OpenGL backend instead of Null
    window_width: int = 800
    window_height: int = 600
    profile_name: str = "default" # ADD profile_name to config

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
        
        dolphin_dir = os.path.dirname(self.config.dolphin_path)
        user_config_path = os.path.join(dolphin_dir, "Profiles")

        command = [
            self.config.dolphin_path,
            "--exec=" + rom_path,
            "--batch",
            "--config=Dolphin.Core.GFXBackend=" + self.config.graphics_backend,
            "--config=Dolphin.Core.SerialPort1=0",
            "--config=Display.Fullscreen=True",  # Changed to windowed mode
            "--config=Display.RenderToMain=True", # Ensure rendering to main window
            "--config=Display.DisableScreenSaver=True",
            "--config=Display.Resolution=" + f"{self.config.window_width}x{self.config.window_height}",
            #f"--profile_name={self.config.profile_name}" # Use profile instead of user-config
        ]

        # Add controller configurations
        for port, controller in self.config.controller_config.items():
            command.append(f"--config=GCPad{port}.Profile={controller}")
        
        # Add memory card configurations
        command.append(f"--config=MemoryCardA.Path={os.path.join(self.config.memcard_directory, 'MemoryCardA.raw')}")
        command.append(f"--config=MemoryCardB.Path={os.path.join(self.config.memcard_directory, 'MemoryCardB.raw')}")
        
        # Set the profile name for all controller ports
        for port in range(4):  # Assuming 4 controller ports
            command.append(f"--config=GCPad{port}.Profile={self.config.profile_name}")
        
        logging.info(f"Starting game with command: {command}")
        
        try:
            # CREATE_NO_WINDOW flag hides the console window
            self.process = subprocess.Popen(
                command,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
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
