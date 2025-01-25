OKay first things first, i kmow i need to ask dolphin for that, i will, but this project need to be done xD 2025-01-25
i will ensure to ask them everything before posting so on this date january 25, this link is not open public... saddd... but yeah ill try to make it WORK peace!!

# GameCube Emulator Setup

This project sets up a GameCube emulator using the Dolphin emulator and runs a specified GameCube ROM.

## Features
- Automatic Dolphin emulator setup and configuration
- GameCube ROM management and launching
- Window control features:
  - Fullscreen toggle
  - Window positioning
  - Window size management
  - State preservation

## Prerequisites

- Python 3.x
- Git
- Internet connection for downloading dependencies and Dolphin setup file
- Windows OS (for window control features)

## Setup Instructions

1. **Clone the repository**:
    ```sh
    git clone https://github.com/your-repo/vscode-w-py.git
    cd vscode-w-py
    ```

2. **Create and activate a virtual environment**:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Run the setup script**:
    ```sh
    python main.py
    ```

## Configuration

- **Dolphin Setup URL**: Update the `dolphin_setup_url` variable in `main.py` with the actual URL to download the Dolphin setup file.
- **Dolphin Executable Path**: Ensure the `dolphin_path` variable in `main.py` points to the correct Dolphin executable.
- **ROM Path**: Update the `game_path` variable in `main.py` with the path to your GameCube ROM file.
- **Window Settings**: Configure default window position/size in `main.py`

## Window Controls
- Press F11 to toggle fullscreen
- Window position is automatically centered on startup
- Window state is preserved between sessions
- Custom window sizes can be configured

## Project Structure

```
vscode-w-py/
├── .venv/                  # Virtual environment directory
├── assets/                 # Assets directory
├── data/                   # Data directory
├── dolphin_setup/          # Directory for storing Dolphin setup file
├── logs/                   # Logs directory
├── notebooks/              # Notebooks directory
├── config.py               # Configuration file
├── controls.py             # Controls handling file
├── directories.py          # Directory setup file
├── game.py                 # Main game loop file
├── gamecube.py             # GameCube emulator configuration and control file
├── graphics.py             # Graphics rendering file
├── main.py                 # Main setup and execution script
├── requirements.txt        # Python dependencies file
├── venv_setup.py           # Virtual environment setup file
└── .gitignore              # Git ignore file
```

## Running the Game

After completing the setup instructions, the game should automatically start using the Dolphin emulator with the specified ROM file.

## Troubleshooting

- Ensure all paths in `main.py` are correctly set.
- Verify that the Dolphin setup URL is correct and accessible.
- Check the logs for any error messages and resolve them accordingly.
- If window controls don't work, ensure pywin32 is properly installed
- For window detection issues, try restarting the emulator
- Check Windows permissions if window manipulation fails

## License

This project is licensed under the MIT License.
