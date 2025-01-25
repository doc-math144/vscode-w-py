import os

def ensure_directories():
    required_dirs = ['assets', 'logs', 'data']
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
