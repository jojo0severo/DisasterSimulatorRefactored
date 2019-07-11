import subprocess
import pathlib


if __name__ == '__main__':
    python_path = pathlib.Path(__file__).parent / 'venv' / 'bin' / 'python'
    subprocess.call(str(python_path.absolute()))
