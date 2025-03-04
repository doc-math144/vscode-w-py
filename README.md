# GameCube Emulator Setup

A Python-based automation project for setting up and configuring the Dolphin GameCube emulator. This project aims to eventually enable browser-based GameCube gameplay through web streaming technology.

## Features
- Automated Dolphin emulator installation and configuration
- Controller profile management
- ROM file handling and launching
- Window management automation
- Future Features:
    - Browser-based game streaming
    - Online multiplayer support
    - Low-latency video encoding
    - Web-based controller input

## Prerequisites

- Python 3.x
- Git
- Windows OS
- Internet connection

## Setup Instructions

1. **Clone the repository**:
        ```sh
        git clone https://github.com/doc-math144/vscode-w-py.git
        cd vscode-w-py
        ```

2. **Virtual environment setup**:
        ```sh
        # The application automatically creates and activates a virtual environment
        # No manual action required for this step
        ```

3. **Install dependencies**:
        ```sh
        # The application automatically installs all required dependencies
        # No manual pip install needed
        ```
        
4. **Configure Dolphin**:
        ```sh
        # The application will attempt to download and configure Dolphin automatically
        # If you have an existing Dolphin installation, you can specify the path when prompted
        # or create a configuration file following the template in documentation
        ```

5. **Run the application**:
        ```sh
        python main.py
        ```

## Project structure  
```
vscode-w-py/
├── .vscode/                    # VSCode configuration folder
├── assets/                     # Assets directory (created automatically)
├── capture.py                  # Screen capture functionality
├── data/                       # Data storage (created automatically)
├── directories.py              # Directory management utilities
├── dolphin_setup/              # Dolphin emulator files (downloaded automatically)
├── file_handler.py             # File download and extraction utilities
├── game/                       # Game ROM storage directory
├── game_to_include/            # Default game ROMs
├── gamecube.py                 # GameCube emulator interface
├── logs/                       # Log files (created automatically)
├── main.py                     # Main application entry point
├── memcards/                   # Memory card storage
├── package_manager.py          # Package installation utilities
├── profiles_to_include/        # Controller profiles
│   └── [Profile].ini           # Default controller configuration
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── saves/                      # Game save files
├── settings.json               # Application settings
├── templates/                  # HTML templates
│   └── index.html              # Web interface template
├── urls.py                     # URL routing for web interface
├── venv_setup.py               # Virtual environment setup
└── web-projector.py            # Web streaming server
└── workspace.py                # Workspace management
```

## Configuration

Edit `settings.json` to customize:
- Dolphin emulator installation path
- ROM directory locations
- Controller profiles and settings
- Window management preferences

Additional configuration can be managed through:
- `directories.py` for custom file paths
- `profiles_to_include/` for controller configurations

## Usage

1. Ensure configuration is complete in `settings.json`
2. Place ROM files in the `game/` directory
3. Run the application:
```sh
python main.py
```
4. The application will automatically:
        - Set up the Dolphin emulator if not already installed
        - Configure controller profiles
        - Prepare the environment for gameplay

Note: If you're experiencing controller issues, check that your device is properly connected and recognized by your system. Controller support is still under development.

## Error Handling

Common issues and solutions:
- Path not found: Verify paths in `settings.json`
- Emulator launch failed: Check Dolphin installation
- ROM loading error: Ensure ROM file integrity
- Controller not detected: Verify controller is connected and properly configured

## Project Status

This project is currently in active development. The core functionality for local emulator automation is implemented, but the web streaming capabilities are still in development. The gamepad functionality is currently not working and will be implemented in future updates.

### Current
- Local emulator automation
- Basic configuration management

### Planned
- Web streaming server implementation
- Browser-based game client
- WebRTC video streaming
- Remote controller input handling
- Multi-user session management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License.
