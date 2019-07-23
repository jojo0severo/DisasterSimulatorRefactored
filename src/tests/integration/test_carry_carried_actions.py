import os
import json
import time
import signal
import pathlib
import socketio
import requests
import subprocess
from environment_handler import Handler


def get_venv_path():
    """Get the path to the generated virtual environment.

    :return str: Path to the virtual environment system independent."""

    h = Handler()
    h.create_environment()
    return h.venv_path + 'python'


agent = {'name': 'carrying_agent'}
carried_agent = {'name': 'carried_agent'}

waits = []
responses = []


socket = socketio.Client()
carried_socket = socketio.Client()
token = None
carried_token = None


def connect_agents():
    """Connect both the agents in the simulation. The one that will carry and the one that will be carried."""

    global token, carried_token

    response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(agent)).json()
    token = response['message']
    requests.post('http://127.0.0.1:12345/register_agent', json=json.dumps({'token': token}))
    socket.emit('connect_registered_agent', data=json.dumps({'token': token}))

    carried_response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(carried_agent)).json()
    carried_token = carried_response['message']
    requests.post('http://127.0.0.1:12345/register_agent', json=json.dumps({'token': carried_token}))
    carried_socket.emit('connect_registered_agent', data=json.dumps({'token': carried_token}))


@socket.on('action_results')
def action_result(msg):
    """Receive the results from the simulation for the actions sent by the agent that will carry the other.

    After carrying, the agent disconnects from the simulation and add True to the waiting variable."""

    msg = json.loads(msg)

    if msg['agent']['last_action'] == 'carry':
        responses.append(msg['agent']['last_action_result'])
        socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)

    requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': 'carry', 'parameters': [carried_token]}))


@carried_socket.on('action_results')
def carried_action_result(msg):
    """Receive the results from the simulation for the actions sent by the agent that will be carried by the other.

    After being carried, the agent disconnects from the simulation and add True to the waiting variable."""

    msg = json.loads(msg)

    if msg['agent']['last_action'] == 'getCarried':
        responses.append(msg['agent']['last_action_result'])
        carried_socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)
    else:
        requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': carried_token, 'action': 'getCarried', 'parameters': []}))


@socket.on('simulation_ended')
def simulation_ended(*args):
    """Add True to the waiting variable if the simulation ends. Just in case the agent can not finish the action."""

    waits.append(True)


@carried_socket.on('simulation_ended')
def carried_simulation_ended(*args):
    """Add True to the waiting variable if the simulation ends. Just in case the agent can not finish the action."""

    waits.append(True)


def quit_program(*args):
    """Add True to the waiting variable after the agent finish its action."""

    waits.append(True)


def do_cycle():
    """Do the cycle of connecting and waiting for the actions to be done by the agents."""

    socket.connect('http://127.0.0.1:12345')
    carried_socket.connect('http://127.0.0.1:12345')
    connect_agents()

    start_time = time.time()
    while len(waits) < 2:
        if start_time + 60 > time.time():
            responses.append(False)
            break

    socket.disconnect()
    carried_socket.disconnect()

    return all(responses)


def test_carry_carried():
    """Start the simulation and execute the test against it."""

    start_system_path = str((pathlib.Path(__file__).parents[3] / 'start_system.py').absolute())
    venv_path = get_venv_path()
    command = [venv_path, start_system_path,
               *'-conf src/tests/integration/carry_test_config.json -first_t 10 -secret batata -log false'.split(' ')]

    null = open(os.devnull, 'w')
    system_proc = subprocess.Popen(command, stdout=null, stderr=subprocess.STDOUT)

    time.sleep(10)
    assert do_cycle()

    requests.get('http://127.0.0.1:12345/terminate', json={'secret': 'batata', 'back': 0})
    requests.get('http://127.0.0.1:8910/terminate', json={'secret': 'batata', 'api': True})

    time.sleep(5)

    os.kill(system_proc.pid, signal.SIGKILL)
    del system_proc

    time.sleep(10)
