import os
import pathlib
import subprocess


class Handler:
    def __init__(self, ):
        self.venv_path = None
        self.root = pathlib.Path(__file__).parents[2].absolute()

    def create_environment(self, globally, python_version):
        if globally:
            self.install_requirements('', python_version)
            self.venv_path = ''

        else:
            venv_path = self.get_venv_path()

            if not os.path.exists(venv_path):
                try:
                    subprocess.call(['virtualenv', 'venv'])
                except FileNotFoundError:
                    subprocess.call([f'pip{python_version}', 'install', 'virtualenv'])
                    subprocess.call(['virtualenv', 'venv'])

            venv_path += '/' if venv_path.find('/') else '\\'
            self.venv_path = venv_path

            self.install_requirements(venv_path, python_version)

    def get_venv_path(self):
        venv_path = self.root / 'venv'

        venv_path = venv_path / 'Scripts' if os.name == 'nt' else venv_path / 'bin'

        return str(venv_path.absolute())

    @staticmethod
    def install_requirements(venv_path, python_version):
        subprocess.call([f"{str(venv_path)}pip{python_version}", "install", "-r", "requirements.txt"])
