import os
import subprocess
import pathlib


if __name__ == '__main__':
    if os.name == 'nt':
        python_path = pathlib.Path(__file__).parent / 'venv' / 'Scripts' / 'python.exe'
    else:
        python_path = pathlib.Path(__file__).parent / 'venv' / 'bin' / 'python'

    file_path = pathlib.Path(__file__).parent / 'test_linux_process_called.py'

    subprocess.call([str(python_path.absolute()), str(file_path.absolute())])
