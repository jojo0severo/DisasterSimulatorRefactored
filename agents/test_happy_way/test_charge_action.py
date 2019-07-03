import requests
import json
import socketio


agent = {'name': 'charge_action_test'}
wait = True
responses = []

socket = socketio.Client()
token = None


def connect_agent():
    global token
    response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(agent)).json()
    token = response['message']
    requests.post('http://127.0.0.1:12345/validate_agent', json=token).json()
    socket.emit('connect_registered_agent', data=json.dumps({'token': token}))


@socket.on('simulation_started')
def simulation_started(*msg):
    requests.post('http://127.0.0.1:12345/send_action', json={'token': token, 'action': 'move', 'parameters': ['cdm']}).json()


@socket.on('action_results')
def action_result(msg):
    msg = json.loads(msg)

    responses.append(msg['agent']['last_action_result'])

    if not msg['agent']['route']:
        if msg['agent']['last_action'] == 'charge':
            socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)

        else:
            requests.post('http://127.0.0.1:12345/send_action', json={'token': token, 'action': 'charge', 'parameters': []}).json()

    else:
        requests.post('http://127.0.0.1:12345/send_action', json={'token': token, 'action': 'move', 'parameters': []}).json()


@socket.on('simulation_ended')
def simulation_ended(*args):
    global wait
    wait = False


def quit_program(*args):
    global wait
    wait = False


def test_cycle():
    socket.connect('http://127.0.0.1:12345')
    connect_agent()
    while wait:
        pass

    assert all(responses)

    socket.disconnect()
