import requests
import json
import socketio


agent = {'name': 'agent'}
wait = True
responses = []


socket = socketio.Client()
token = None


def connect_agent():
    global token
    response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(agent)).json()
    token = response['message']
    requests.post('http://127.0.0.1:12345/register_agent', json=json.dumps({'token': token}))
    socket.emit('connect_registered_agent', data=json.dumps({'token': token}), callback=print)


@socket.on('simulation_started')
def simulation_started(msg):
    print('Simulation started:', msg)
    requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': 'pass', 'parameters': []}))


@socket.on('action_results')
def action_result(msg):
    print('Action results:', msg)
    requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': 'pass', 'parameters': []}))


@socket.on('simulation_ended')
def simulation_ended(*args):
    print('Simulation ended:', args)


if __name__ == '__main__':
    socket.connect('http://127.0.0.1:12345')
    connect_agent()
