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
from src.communication.helpers.helper import Helper
from src.communication.helpers import json_formatter

base_url, api_port, simulation_port, step_time, first_step_time, agents_amount, method, secret = sys.argv[1:]

app = Flask(__name__)
socket = SocketIO(app=app)

helper = Helper(agents_amount, first_step_time, secret)
every_agent_registered_queue = Queue()
one_agent_registered_queue = Queue()
actions_queue = Queue()


@app.route('/start_connections', methods=['POST'])
def start_connections():
    try:
        errors, message = helper.do_internal_verification(request)

        if errors:
            return jsonify(message=f'This endpoint can not be accessed. {message}')

        if message['back'] != 1:
            helper.controller.started = True

            if method == 'time':
                multiprocessing.Process(target=first_step_time_controller, args=(every_agent_registered_queue,), daemon=True).start()

            else:
                multiprocessing.Process(target=first_step_button_controller, daemon=True).start()

        else:
            multiprocessing.Process(target=first_step_time_controller, args=(one_agent_registered_queue,),
                                    daemon=True).start()

        helper.controller.start_timer()

        return jsonify('')

    except json.JSONDecodeError:
        return jsonify(message='This endpoint can not be accessed.')


def first_step_time_controller(ready_queue):
    agents_connected = False

    try:
        if int(agents_amount) > 0:
            agents_connected = ready_queue.get(block=True, timeout=int(first_step_time))

        else:
            agents_connected = True

    except queue.Empty:
        pass

    if not agents_connected:
        requests.post(f'http://{base_url}:{api_port}/start_connections', json={'secret': secret, 'back': 1})

    else:
        requests.get(f'http://{base_url}:{api_port}/start_step_cycle', json={'secret': secret})


def first_step_button_controller():
    sys.stdin = open(0)
    print('When you are ready press: "Enter"')
    sys.stdin.read(1)

    requests.get(f'http://{base_url}:{api_port}/start_step_cycle', json=secret)


@app.route('/connect_agent', methods=['POST'])
def connect_agent():
    response = {'status': 0, 'result': False, 'message': 'Error.'}

    errors, message = helper.do_connection_verifications(request)

    if not errors:
        agent_info = request.get_json(force=True)
        token = jwt.encode(agent_info, 'secret', algorithm='HS256').decode('utf-8')

        helper.controller.add_agent(token, agent_info)

        response['status'] = 1
        response['result'] = True
        response['message'] = token

    else:
        response['message'] = message

    return jsonify(response)


@app.route('/validate_agent', methods=['POST'])
def validate_agent():
    response = {'status': 0, 'result': False, 'message': 'Error.'}

    errors, message = helper.do_validation_verifications(request)

    if not errors:
        token = request.get_json(force=True)

        helper.controller.edit_agent(token, 'registered', True)

        response['status'] = 1
        response['result'] = True
        response['message'] = 'Agent registered.'

    else:
        response['message'] = message

    return jsonify(response)


@socket.on('connect_registered_agent')
def connect_registered_agent(message):
    response = {'status': 0, 'result': False, 'message': 'Error.'}

    errors, message = helper.do_socket_connection_verifications(message)

    if not errors:
        token = json.loads(message)['token']
        helper.controller.add_socket(token, request.sid)

        try:
            sim_response = requests.post(f'http://{base_url}:{simulation_port}/register_agent',
                                         json={'token': token, 'secret': secret}).json()

            if sim_response['status'] == 1:
                response['status'] = 1
                response['result'] = True
                response['message'] = 'Agent successfully connected.'

                if helper.controller.check_socket_agents():
                    if not helper.controller.check_population():
                        every_agent_registered_queue.put(True)

                    one_agent_registered_queue.put(True)

            else:
                response['message'] = sim_response['message']

        except requests.exceptions.ConnectionError:
            response['message'] = 'Simulation is not online.'

    else:
        response['message'] = message

    return json.dumps(response, sort_keys=False)


@socket.on('disconnect_registered_agent')
def disconnect_registered_agent(message):
    response = {'status': 0, 'result': False, 'message': 'Error.'}

    errors, message = helper.do_socket_disconnection_verifications(message)

    if not errors:
        try:
            token = json.loads(message)['token']
            sim_response = requests.put(f'http://{base_url}:{simulation_port}/delete_agent',
                                        json={'token': token, 'secret': secret}).json()

            if sim_response['status'] == 1:
                response['status'] = 1
                response['result'] = True
                response['message'] = 'Agent successfully disconnected.'

                helper.controller.disconnect_agent(token)

            else:
                response['message'] = sim_response['message']

        except json.decoder.JSONDecodeError:
            response['message'] = 'An internal error occurred at the simulation.'

        except requests.exceptions.ConnectionError:
            response['message'] = 'Simulation is not online.'

    return json.dumps(response, sort_keys=False)


@app.route('/start_step_cycle', methods=['GET'])
def start_step_cycle():
    try:
        errors, message = helper.do_internal_verification(request)

        if errors:
            return jsonify(message=f'This endpoint can not be accessed. {message}')

        helper.controller.finish_connection_timer()

        sim_response = requests.post(f'http://{base_url}:{simulation_port}/start', json={'secret': secret}).json()

        notify_agents('simulation_started', sim_response)

        multiprocessing.Process(target=step_controller, args=(actions_queue,), daemon=True).start()

    except json.JSONDecodeError:
        return jsonify(message='This endpoint can not be accessed.')

    return jsonify('')


@app.route('/finish_step', methods=['GET'])
def finish_step():
    errors, message = helper.do_internal_verification(request)

    if errors:
        return jsonify(message=f'This endpoint can not be accessed. {message}')

    try:
        helper.controller.processing_actions = True

        tokens_actions_list = helper.controller.get_actions()
        sim_response = requests.post(f'http://{base_url}:{simulation_port}/do_actions',
                                     json={'actions': tokens_actions_list, 'secret': secret}).json()

        helper.controller.clear_workers()

        if sim_response['status'] == 0:
            print('Error: ' + sim_response['message'])
            print('An internal error occurred. Shutting down...')
            requests.get(f'http://{base_url}:{simulation_port}/terminate', json={'secret': secret, 'api': True})
            os._exit(1)

        if sim_response['message'] == 'Simulation finished.':
            sim_response = requests.put(f'http://{base_url}:{simulation_port}/restart', json={'secret': secret}).json()

            if sim_response['status'] == 0:
                requests.get(f'http://{base_url}:{simulation_port}/terminate', json={'secret': secret, 'api': True})
                notify_agents('simulation_ended', {'status': 1, 'message': 'Simulation ended all matches.'})
                os._exit(0)

            else:
                notify_agents('simulation_started', sim_response)

                helper.controller.processing_actions = False
                multiprocessing.Process(target=step_controller, args=(actions_queue,), daemon=True).start()

        else:
            notify_agents('action_result', sim_response)

            helper.controller.processing_actions = False
            multiprocessing.Process(target=step_controller, args=(actions_queue,), daemon=True).start()

    except requests.exceptions.ConnectionError:
        pass

    return jsonify(0)


def step_controller(ready_queue):
    try:
        if int(agents_amount) > 0:
            ready_queue.get(block=True, timeout=int(step_time))

    except queue.Empty:
        pass

    try:
        requests.get(f'http://{base_url}:{api_port}/finish_step', json={'secret': secret})
    except requests.exceptions.ConnectionError:
        pass


@app.route('/send_action', methods=['POST'])
def send_action():
    response = {'status': 0, 'result': False, 'message': 'Error.'}

    errors, message = helper.do_action_verifications(request)

    if not errors:
        token = request.get_json(force=True)['token']
        helper.controller.edit_agent(token, 'action_name', message['action'])
        helper.controller.edit_agent(token, 'action_params', message['parameters'])
        helper.controller.edit_agent(token, 'worker', True)

        response['status'] = 1
        response['result'] = True
        response['message'] = 'Action successfully sent.'

        if helper.controller.check_working_agents():
            actions_queue.put(True)

    else:
        response['message'] = message

    return jsonify(response)


def notify_agents(event, response):
    for token in helper.controller.get_sockets():
        if event == 'simulation_started':
            info = json_formatter.simulation_started_format(response, token)

        elif event == 'simulation_ended':
            info = json_formatter.simulation_ended_format(response)

        elif event == 'action_results':
            info = json_formatter.action_results_format(response, token)

        else:
            info = json_formatter.event_error_format('Wrong event name. ')

        room = helper.controller.get_socket(token)
        socket.emit(event, json.dumps(info), room=room)


if __name__ == '__main__':
    app.config['SECRET_KEY'] = secret
    app.config['JSON_SORT_KEYS'] = False
    print(f'API: Serving on http://{base_url}:{api_port}')

    socket.run(app=app, host=base_url, port=api_port)
