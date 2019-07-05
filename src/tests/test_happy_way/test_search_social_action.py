import requests
import json
import socketio


agent = {'name': 'search_action_test'}
wait = True
responses = []


socket = socketio.Client()
token = None
counter = 0
max_iter = 2


def connect_agent():
    global token
    response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(agent)).json()
    token = response['message']
    requests.post('http://127.0.0.1:12345/validate_agent', json=json.dumps({'token': token}))
    socket.emit('connect_registered_agent', data=json.dumps({'token': token}))


@socket.on('simulation_started')
def simulation_started(msg):
    requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': 'search_social_asset', 'parameters': ['doctor']}))


@socket.on('action_results')
def action_result(msg):
    global counter
    print(msg)
    if counter == max_iter:
        socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)
    else:
        requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': 'search_social_asset', 'parameters': ['doctor']}))
        counter += 1


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


if __name__ == '__main__':
    socket.connect('http://127.0.0.1:12345')
    connect_agent()
    while wait:
        pass

    assert all(responses)

    socket.disconnect()