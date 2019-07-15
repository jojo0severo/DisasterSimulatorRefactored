import os
import re
import time
import signal
import pathlib
import requests
import subprocess
from environment_handler import Handler


def get_venv_path():
    h = Handler()
    h.root = pathlib.Path(__file__).parents[2].absolute()
    h.create_environment(False, '')
    return h.venv_path + 'python'


def collect_modules():
    tests_dir = pathlib.Path(__file__).parent / 'test_social_assets'

    modules = []
    for (dirpath, dirnames, filenames) in os.walk(str(tests_dir.absolute())):
        for filename in filenames:
            if filename.startswith('test_') and filename.endswith('.py'):
                modules.append(str((tests_dir / filename).absolute()))

    return modules


def execute_modules():
    start_system_path = str((pathlib.Path(__file__).parents[2] / 'start_system.py').absolute())
    venv_path = get_venv_path()
    command = [venv_path, start_system_path,
               *'-conf src/tests/test_social_assets/assets_test_config.json -first_t 10 -secret batata -log false'.split(' ')]

    tests_passed = []
    modules = collect_modules()
    for module in modules:
        print('\nCurrent test:', module)
        null = open(os.devnull, 'w')
        system_proc = subprocess.Popen(command, stdout=null, stderr=subprocess.STDOUT)
        time.sleep(10)
        print('System up')

        test_proc = subprocess.Popen([venv_path, module], stdout=subprocess.PIPE)
        out, err = test_proc.communicate()
        print('Output:', out.decode('utf-8')[-1])

        passed = True if re.findall('True', out.decode('utf-8')) else False
        if not passed:
            print(f'Module {module} failed')

        tests_passed.append(passed)
        test_proc.kill()
        print('Test process killed')

        requests.get('http://127.0.0.1:12345/terminate', json={'secret': 'batata', 'back': 0})
        print('API terminated.')

        requests.get('http://127.0.0.1:8910/terminate', json={'secret': 'batata', 'api': True})
        print('Simulation terminated')

        time.sleep(5)

        os.kill(system_proc.pid, signal.SIGKILL)
        del system_proc
        print('System process killed')
        time.sleep(10)

    return tests_passed


def test_system():
    assert all(execute_modules())


if __name__ == '__main__':
    print(execute_modules())
