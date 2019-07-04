import requests
import json
import socketio


agent = {'name': 'water_action_test'}
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
def simulation_started(msg):
    water_loc = get_water_loc(msg)
    requests.post('http://127.0.0.1:12345/send_action', json={'token': token, 'action': 'move', 'parameters': water_loc}).json()


def get_water_loc(msg):
    msg = json.loads(msg)
    my_location = msg['agent']['location']
    min_distance = 999999999
    water_loc = None
    for water_sample in msg['event']['water_samples']:
        actual_distance = calculate_distance(my_location, water_sample['location'])
        if actual_distance < min_distance:
            min_distance = actual_distance
            water_loc = water_sample['location']

    return water_loc


def calculate_distance(x, y):
    return ((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) ** 0.5


@socket.on('action_results')
def action_result(msg):
    msg = json.loads(msg)

    responses.append(msg['agent']['last_action_result'])

    if not msg['agent']['route']:
        if msg['agent']['last_action'] == 'collect_water':
            socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)

        else:
            requests.post('http://127.0.0.1:12345/send_action', json={'token': token, 'action': 'collect_water', 'parameters': []}).json()

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
