import os
import requests
import json
import socketio
import random


agent = {'name': 'batata'}
actions = ['move']


socket = socketio.Client()
token = None


@socket.on('simulation_started')
def simulation_started(msg):
    print()
    print('Simulation started: ', end='')
    print(msg)
    action = random.choice(actions)
    print(f'Send action {action}: ', end='')
    requests.post('http://127.0.0.1:12345/send_action', json={'token': token, 'action': action, 'parameters': []}).json()
    print()


@socket.on('simulation_ended')
def simulation_ended(msg):
    print('Simulation ended: ', end='')
    print(msg)
    os._exit(0)


@socket.on('action_results')
def action_result(msg):
    print('Action results: ', end='')
    print(msg)
    action = random.choice(actions)
    print(f'Send action {action}: ', end='')
    requests.post('http://127.0.0.1:12345/send_action', json={'token': token, 'action': action, 'parameters': []}).json()
    print()


def connect_agent():
    global token
    print('Connection:')
    response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(agent)).json()
    print(response)
    token = response['message']
    print(requests.post('http://127.0.0.1:12345/validate_agent', json=token).json())
    socket.emit('connect_registered_agent', data=json.dumps({'token': token}), callback=print)


if __name__ == '__main__':
    socket.connect('http://127.0.0.1:12345')
    connect_agent()
