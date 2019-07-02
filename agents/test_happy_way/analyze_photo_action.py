import os
import requests
import json
import socketio


agent = {'name': 'batata'}
action = 'analyze_photo'


socket = socketio.Client()
token = None


@socket.on('simulation_started')
def simulation_started(msg):
    print()
    print('Simulation started: ', end='')
    print(msg)
    move_to_photo(msg)


@socket.on('simulation_ended')
def simulation_ended(msg):
    print('Simulation ended: ', end='')
    print(msg)
    os._exit(0)


def connect_agent():
    global token
    print('Connection:')
    response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(agent)).json()
    print(response)
    token = response['message']
    print(requests.post('http://127.0.0.1:12345/validate_agent', json=token).json())
    socket.emit('connect_registered_agent', data=json.dumps({'token': token}), callback=print)


def move_to_photo(msg):
    msg = json.loads(msg)
    my_location = msg['agent']['location']
    min_distance = 999999999
    photo_loc = None
    for photo in msg['event']['photos']:
        actual_distance = calculate_distance(my_location, photo['location'])
        if actual_distance < min_distance:
            min_distance = actual_distance
            photo_loc = photo['location']

    requests.post('http://127.0.0.1:12345/send_action', json={'token': token, 'action': 'move', 'parameters': photo_loc}).json()


@socket.on('action_results')
def action_result(msg):
    msg = json.loads(msg)

    printable = {
        'last_action': msg['agent']['last_action'],
        'last_action_result': msg['agent']['last_action_result'],
        'message': msg['message']
    }
    print(printable)

    if not msg['agent']['route']:
        if msg['agent']['last_action'] == 'take_photo':
            requests.post('http://127.0.0.1:12345/send_action', json={'token': token, 'action': action, 'parameters': []}).json()

        elif msg['agent']['last_action'] == action:
            socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)

        else:
            requests.post('http://127.0.0.1:12345/send_action', json={'token': token, 'action': 'take_photo', 'parameters': []}).json()

    else:
        requests.post('http://127.0.0.1:12345/send_action', json={'token': token, 'action': 'move', 'parameters': []}).json()


def calculate_distance(x, y):
    return ((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) ** 0.5


def quit_program(args):
    print(json.loads(args))
    os._exit(0)


if __name__ == '__main__':
    socket.connect('http://127.0.0.1:12345')
    connect_agent()
