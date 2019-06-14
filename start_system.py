import os
import json
import pathlib
import argparse
import subprocess
import secrets
from multiprocessing import Process

root = pathlib.Path(__file__).parent.absolute()


class SimulationParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='Disaster Simulator')
        self.add_arguments()

    def add_arguments(self):
        self.parser.add_argument('-conf', required=True, type=str)
        self.parser.add_argument('-url', required=False, type=str, default='127.0.0.1')
        self.parser.add_argument('-sp', required=False, type=str, default='8910')
        self.parser.add_argument('-ap', required=False, type=str, default='12345')
        self.parser.add_argument('-pyv', required=False, type=str, default='')
        self.parser.add_argument('-g', required=False, type=bool, default=False)
        self.parser.add_argument('-step_t', required=False, type=int, default=30)
        self.parser.add_argument('-first_t', required=False, type=int, default=60)
        self.parser.add_argument('-matches', required=False, type=int, default=1)
        self.parser.add_argument('-mtd', required=False, type=str, default='time')

    def get_arguments(self):
        args = self.parser.parse_args()

        return [args.conf, args.url, args.sp, args.ap, args.pyv, args.g,
                args.step_t, args.first_t, args.matches, args.mtd]


class EnvironmentHandler:
    def __init__(self, ):
        self.venv_path = None

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

    @staticmethod
    def get_venv_path():
        venv_path = root / 'venv'

        venv_path = venv_path / 'Scripts' if os.name == 'nt' else venv_path / 'bin'

        return str(venv_path.absolute())

    @staticmethod
    def install_requirements(venv_path, python_version):
        subprocess.call([f"{str(venv_path)}pip{python_version}", "install", "-r", "requirements.txt"])


class Starter:
    def __init__(self):
        self.parser = SimulationParser()
        self.env_handler = EnvironmentHandler()

    def start(self):
        config_file, base_url, simulation_port, api_port, python_version, globally, step_time, first_step_time, \
            matches_number, method = self.parser.get_arguments()

        with open(config_file, 'r') as configuration_file:
            agents_amount = sum(json.loads(configuration_file)['agents'].values())

        self.env_handler.create_environment(globally, python_version)
        secret = secrets.token_urlsafe(15)

        simulation_arguments = [config_file, base_url, simulation_port, api_port, secret]
        simulation_process_arguments = (simulation_arguments, self.env_handler.venv_path, python_version)
        simulation_process = Process(target=self.start_simulation, args=simulation_process_arguments, daemon=True)

        api_arguments = [config_file, base_url, api_port, simulation_port, step_time, first_step_time,
                         matches_number, agents_amount, method, secret]
        api_process_arguments = (api_arguments, self.env_handler.venv_path, python_version)
        api_process = Process(target=self.start_api, args=api_process_arguments, daemon=True)

        simulation_process.start()
        api_process.start()

        simulation_process.join()
        api_process.join()

        simulation_process.close()
        api_process.close()

    @staticmethod
    def start_simulation(simulation_arguments, venv_path, python_version):
        simulation_module_path = root / 'src' / 'simulation.py'
        subprocess.call([
            f'{str(venv_path)}python{python_version}', str(simulation_module_path.absolute()), *simulation_arguments
        ])

    @staticmethod
    def start_api(api_arguments, venv_path, python_version):
        api_module_path = root / 'src' / 'api.py'
        subprocess.call([
            f"{str(venv_path)}python{python_version}", str(api_module_path.absolute()), *api_arguments
        ])


if __name__ == '__main__':
    starter = Starter()
    starter.start()
