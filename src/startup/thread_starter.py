import json
import secrets
import pathlib
import subprocess
from multiprocessing import Process
from src.startup.environment_handler import Handler
from src.startup.arguments_parser import Parser
from src.startup.configuration_checker import Checker


class Starter:
    def __init__(self):
        self.parser = Parser()
        self.env_handler = Handler()
        self.checker = Checker(self.parser.get_argument('conf'))
        self.root = pathlib.Path(__file__).parents[1].absolute()

    def start(self):
        self.check_configuration_file()
        self.create_environment()
        arguments = self.get_arguments()
        self.start_processes(*arguments)

    def check_configuration_file(self):
        test = self.checker.test_json_load()
        if test[0]:
            test = self.checker.test_main_keys()
            if test[0]:
                test = self.checker.test_map_key()
                if test[0]:
                    test = self.checker.test_agents_key()
                    if test[0]:
                        test = self.checker.test_roles_key()
                        if test[0]:
                            test = self.checker.test_generate_key()
                            if test[0]:
                                return
        exit(test[1])

    def create_environment(self):
        globally = self.parser.get_argument('g')
        python_version = self.parser.get_argument('pyv')

        self.env_handler.create_environment(globally, python_version)

    def get_arguments(self):
        self.parser.check_arguments()

        config_file = self.parser.get_argument('conf')

        with open(config_file, 'r') as configuration_file:
            agents_amount = sum(json.load(configuration_file)['agents'].values())

        secret = secrets.token_urlsafe(15)

        simulation_arguments = self.parser.get_simulation_arguments()
        simulation_arguments.append(secret)

        api_arguments = self.parser.get_api_arguments()
        api_arguments.extend([agents_amount, secret])

        return api_arguments, simulation_arguments, self.parser.get_argument('pyv')

    def start_processes(self, api_arguments, simulation_arguments, python_version):
        simulation_path = str((self.root / 'execution' / 'simulation.py').absolute())
        simulation_process_arguments = (simulation_path, simulation_arguments, self.env_handler.venv_path, python_version)
        simulation_process = Process(target=self.start_simulation, args=simulation_process_arguments, daemon=True)

        api_path = str((self.root / 'execution' / 'api.py').absolute())
        api_process_arguments = (api_path, api_arguments, self.env_handler.venv_path, python_version)
        api_process = Process(target=self.start_api, args=api_process_arguments, daemon=True)

        api_process.start()
        simulation_process.start()

        api_process.join()
        simulation_process.join()

    @staticmethod
    def start_simulation(module_path, simulation_arguments, venv_path, python_version):
        subprocess.call([f'{str(venv_path)}python{python_version}', module_path, *map(str, simulation_arguments)])

    @staticmethod
    def start_api(module_path, api_arguments, venv_path, python_version):
        subprocess.call([f"{str(venv_path)}python{python_version}", module_path, *map(str, api_arguments)])
