from gamecube import GameCubeConfig, GameCubeEmulator

config = GameCubeConfig(
    dolphin_path="C:/Program Files/Dolphin/Dolphin.exe",
    rom_directory="C:/Games/GameCube",
    memcard_directory="C:/Users/Username/Documents/Dolphin/GC",
    controller_config={
        0: {"type": "GCPad", "device": 0}
    }
)

emulator = GameCubeEmulator(config)
emulator.start_game("game.iso")
