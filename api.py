import os
import sys
import jwt
import json
import queue
import requests
import multiprocessing
from multiprocessing import Queue
from flask_socketio import SocketIO
from flask import Flask, request, jsonify

from communication import formater
from communication.controller import Controller

base_url, api_port, simulation_port, step_time, first_step_time, matches, agents_amount, method, global_secret = \
    sys.argv[1:]

app = Flask(__name__)
app.config['SECRET_KEY'] = global_secret
socket = SocketIO(app=app)

controller = Controller(matches, int(agents_amount), int(first_step_time), global_secret)
connection_queue = Queue()
job_queue = Queue()
socket_clients = {}


@app.route('/start_connections', methods=['POST'])
def start_connections():
    global controller

    secret = request.get_json(force=True)

    if not controller.check_secret(secret):
        return jsonify('This endpoint can not be accessed.')

    controller.started = True
    controller.start_timer()

    if method == 'time':
        connection_arguments = (connection_queue, controller.get_agents())
        multiprocessing.Process(target=first_step_time_controller, args=connection_arguments, daemon=True).start()
    else:
        connection_arguments = ()
        multiprocessing.Process(target=first_step_button_controller, args=connection_arguments, daemon=True).start()

    return jsonify('')


def first_step_time_controller(ready_queue, current_agents):
    try:
        ready_queue.get(block=True, timeout=int(first_step_time))
    except queue.Empty:
        pass

    finally:
        if not current_agents:
            requests.post(f'http://{base_url}:{api_port}/start_connections', json=controller.secret)
        else:
            requests.get(f'http://{base_url}:{api_port}/start_step_cycle', json=controller.secret)


def first_step_button_controller():
    sys.stdin = open(0)
    print('When you are ready press Enter.')
    sys.stdin.read(1)

    requests.get(f'http://{base_url}:{api_port}/start_step_cycle', json=controller.secret)


@app.route('/start_step_cycle')
def cycle_starter():

    secret = request.get_json(force=True)

    if not controller.check_secret(secret):
        return jsonify('This endpoint can not be accessed.')

    if controller.is_first_step:
        controller.is_first_step = False
        notify_agents('simulation_started', None)

        multiprocessing.Process(target=step_controller, args=(step_time, job_queue), daemon=True).start()
        return jsonify(0)

    else:
        return jsonify(1)


@socket.on('connect_registered_agent')
def connect_registered_agent(message):
    if not controller.check_timer():
        return 0, 'Can no longer connect due to time.'

    elif not controller.check_agent_token(request.get_json(force=True)):
        return 2, 'Agent not connected or invalid Token.'

    elif not controller.check_token_registered(request.get_json(force=True)):
        return 3, 'Agent was not registered.'

    else:
        identifier = json.loads(message)['token']
        socket_clients[identifier] = request.sid
        return 1, 'Agent successfully connected.'


@socket.on('disconnect_registered_agent')
def disconnect_registered_agent(message):
    identifier = json.loads(message)['token']

    if identifier not in socket_clients:
        return 0, 'Agent was not connected.'

    else:
        del socket_clients[identifier]
        return 1, 'Agent successfully disconnected.'


@app.route('/connect_agent', methods=['POST'])
def connect_agent():
    agent_response = {'can_connect': False, 'data': '', 'message': ''}

    if not controller.started:
        agent_response['message'] = 'Simulation was not started.'

    elif controller.terminated:
        agent_response['message'] = 'Simulation already finished'

    elif not controller.check_timer():
        agent_response['message'] = 'Can no longer connect due to time.'

    elif not controller.check_population():
        agent_response['message'] = 'All possible agents already are connected.'

    elif controller.check_agent_connected(request.get_json(force=True)):
        agent_response['message'] = 'Agent already is connected.'

    else:
        agent_info = request.get_json(force=True)
        token = jwt.encode(agent_info, 'secret', algorithm='HS256').decode('utf-8')

        controller.add_agent(token, agent_info)

        agent_response['can_connect'] = True
        agent_response['data'] = token

    return jsonify(agent_response)


@app.route('/validate_agent', methods=['POST'])
def validate_agent():
    agent_response = {'agent_connected': False, 'message': ''}

    if not controller.started:
        agent_response['message'] = 'Simulation has not started.'

    elif controller.terminated:
        agent_response['message'] = 'Simulation already finished.'

    elif not controller.check_timer():
        agent_response['message'] = 'Can no longer connect due to time.'

    elif not controller.check_agent_token(request.get_json(force=True)):
        agent_response['message'] = 'Agent not connected or invalid Token.'

    elif controller.check_token_registered(request.get_json(force=True)):
        agent_response['message'] = 'Agent already registered.'

    else:
        try:
            token = request.get_json(force=True)
            agent = controller.get_agent(token).format()
            simulation_response = requests.post(f'http://{base_url}:{simulation_port}/register_agent',
                                                json=[agent, controller.secret]).json()

            controller.edit_agent(token, 'registered', True)
            controller.edit_agent(token, 'simulation_info', simulation_response['agent'])

            agent_response['agent_connected'] = True

            if not controller.check_population() and len(socket_clients) == len(controller.get_agents()):
                connection_queue.put(True)
                notify_agents('simulation_started', None)

        except requests.exceptions.ConnectionError:
            agent_response['message'] = 'Simulation is not online.'

        except json.decoder.JSONDecodeError:
            agent_response['message'] = 'An internal error occurred at the simulation.'

    return jsonify(agent_response)


@app.route('/send_job', methods=['POST'])
def send_job():
    agent_response = {'job_delivered': False, 'message': ''}

    if not controller.started:
        agent_response['message'] = 'Simulation was not started.'

    elif controller.terminated:
        agent_response['message'] = 'Simulation already finished.'

    elif controller.check_timer():
        agent_response['message'] = 'Simulation still receiving connections.'

    else:
        try:
            message = request.get_json(force=True)
            token = message['token']

            if token not in socket_clients:
                agent_response['message'] = 'Agent Socket was not connect.'

            elif not controller.check_agent_token(token):
                agent_response['message'] = 'Agent not connected.'

            elif not controller.check_token_registered(token):
                agent_response['message'] = 'Agent not registered.'

            elif controller.check_agent_action(token):
                agent_response['message'] = 'The agent has already sent a job'

            else:
                controller.edit_agent(token, 'action_name', message['action'])
                controller.edit_agent(token, 'action_params', [*message['parameters']])
                controller.edit_agent(token, 'worker', True)

                agent_response['job_delivered'] = True

                if controller.check_working_agents():
                    job_queue.put(True)

        except TypeError as t:
            agent_response['message'] = 'TypeError: ' + str(t)

        except KeyError as k:
            agent_response['message'] = 'KeyError: ' + str(k)

    return jsonify(agent_response)


@app.route('/finish_step', methods=['GET'])
def finish_step():
    secret = request.get_json(force=True)

    if not controller.check_secret(secret):
        return jsonify('This endpoint can not be accessed.')

    try:
        jobs = controller.get_jobs()
        simulation_response = requests.post(f'http://{base_url}:{simulation_port}/do_actions',
                                            json=[jobs, controller.secret]).json()

        if simulation_response['done']:
            if controller.check_remaining_matches():
                max_matches = controller.max_matches
                controller.burn(max_matches, int(agents_amount), int(first_step_time))
                return jsonify(3)
            else:
                requests.get(f'http://{base_url}:{simulation_port}/terminate', json=controller.secret)
                return jsonify(4)

        else:
            controller.update_agents(simulation_response)
            notify_agents('job_result', simulation_response)
            controller.clear_workers()

        multiprocessing.Process(target=step_controller, args=(step_time, job_queue), daemon=True).start()
        return jsonify(1)

    except requests.exceptions.ConnectionError:
        return jsonify(2)


def step_controller(sec, ready_queue):
    try:
        ready_queue.get(block=True, timeout=int(sec))
    finally:
        code = requests.get(f'http://{base_url}:{api_port}/finish_step', json=controller.secret).json()

        if code == 2:
            print('Simulation is not online. Terminating...')
            requests.get(f'http://{base_url}:{api_port}/terminate', json=controller.secret)

        elif code == 3:
            print('Ended match.')
            requests.get(f'http://{base_url}:{simulation_port}/restart', json=controller.secret)

        elif code == 4:
            print('Simulation ended all matches. Terminating...')
            requests.get(f'http://{base_url}:{api_port}/terminate', json=controller.secret)


def notify_agents(event, simulation_state):
    for token in socket_clients:
        agent = controller.get_agent(token).simulation_info
        info = formater.format_for_event(event, agent, simulation_state)
        room = socket_clients[token]
        socket.emit(event, json.dumps(info), room=room)


@app.route('/terminate', methods=['GET'])
def terminate():
    secret = request.get_json(force=True)

    if controller.secret != secret:
        return jsonify('This endpoint can not be accessed.')

    os._exit(0)


if __name__ == '__main__':
    print(f'API Serving on http://{base_url}:{api_port}')
    socket.run(app=app, host=base_url, port=api_port)
