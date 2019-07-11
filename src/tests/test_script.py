import os
import re
import time
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
    tests_dir = pathlib.Path(__file__).parent / 'test_happy_way'

    modules = []
    for (dirpath, dirnames, filenames) in os.walk(str(tests_dir.absolute())):
        for filename in filenames:
            if filename.startswith('test_') and filename.endswith('.py'):
                modules.append(str((tests_dir / filename).absolute()))

    return modules


def execute_modules():
    start_system_path = str((pathlib.Path(__file__).parents[2] / 'start_system.py').absolute())
    venv_path = get_venv_path()
    command = [venv_path, start_system_path, *'-conf files/config.json -first_t 40 -secret batata -log false'.split(' ')]

    tests_passed = []
    modules = collect_modules()
    for module in modules:
        FNULL = open(os.devnull, 'w')
        system_proc = subprocess.Popen(command, stderr=subprocess.STDOUT)
        time.sleep(10)

        test_proc = subprocess.Popen([venv_path, module], stdout=subprocess.PIPE)
        out, err = test_proc.communicate()
        print('output:', out.decode('utf-8'), end='')

        passed = True if re.findall('True', out.decode('utf-8')) else False
        if not passed:
            print(f'Module {module} failed')

        tests_passed.append(passed)
        print('added')
        test_proc.kill()
        print('test_proc killed')

        requests.get('http://127.0.0.1:12345/terminate', json={'secret': 'batata', 'back': 0})
        print('api terminated')

        requests.get('http://127.0.0.1:8910/terminate', json={'secret': 'batata', 'api': True})
        print('simulation terminated.')

        try:
            time.sleep(10)
        except PermissionError:
            pass
        system_proc.kill()
        print('system_proc killed')

    return tests_passed


def test_system():
    assert all(execute_modules())


if __name__ == '__main__':
    execute_modules()
