import os
import sys
import json
import time
import queue
import requests
import multiprocessing
from multiprocessing import Queue
from flask_socketio import SocketIO
from flask import Flask, request, jsonify
from src.system.execution.communication.helpers.controller import Controller
from src.system.execution.communication.helpers import json_formatter

base_url, api_port, simulation_port, step_time, first_step_time, method, secret, agents_amount, assets_amount = sys.argv[1:]


app = Flask(__name__)
socket = SocketIO(app=app)

controller = Controller(agents_amount, assets_amount, first_step_time, secret)
everyone_registered_queue = Queue()
one_agent_registered_queue = Queue()
actions_queue = Queue()


# ===================================================== CONNECTION LOOP =====================================================

@app.route('/start_connections', methods=['POST'])
def start_connections():
    try:
        valid, message = controller.do_internal_verification(request)

        if not valid:
            return jsonify(message=f'This endpoint can not be accessed. {message}')

        if message['back'] != 1:
            controller.set_started()

            if method == 'time':
                multiprocessing.Process(target=first_step_time_controller, args=(everyone_registered_queue,), daemon=True).start()

            else:
                multiprocessing.Process(target=first_step_button_controller, daemon=True).start()

        else:
            multiprocessing.Process(target=first_step_time_controller, args=(one_agent_registered_queue,), daemon=True).start()

        controller.start_timer()

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

# ===========================================================================================================================


# ================================================== CONNECTION ENDPOINTS ===================================================

@app.route('/connect_agent', methods=['POST'])
def connect_agent():
    response = {'status': 1, 'result': True, 'message': 'Error.'}

    status, message = controller.do_agent_connection(request)

    if status != 1:
        response['status'] = status
        response['result'] = False

    response['message'] = message

    return jsonify(response)


@app.route('/validate_agent', methods=['POST'])
def validate_agent():
    response = {'status': 1, 'result': True, 'message': 'Error.'}

    status, message = controller.do_agent_registration(request)

    if status != 1:
        response['status'] = status
        response['result'] = False

    response['message'] = message

    return jsonify(response)


@socket.on('connect_registered_agent')
def connect_registered_agent(msg):
    response = {'status': 0, 'result': False, 'message': 'Error.'}

    status, message = controller.do_agent_socket_connection(msg, request)

    if status == 1:
        try:
            sim_response = requests.post(f'http://{base_url}:{simulation_port}/register_agent',
                                         json={'token': message, 'secret': secret}).json()

            if sim_response['status'] == 1:
                response['status'] = 1
                response['result'] = True
                response['message'] = 'Agent successfully connected.'

                agents_list_size = len(controller.manager.get_all('agent'))
                assets_list_size = len(controller.manager.get_all('social_asset'))

                if len(controller.manager.get_all('socket')) == agents_list_size + assets_list_size:
                    if controller.agents_amount == agents_list_size and controller.social_assets_amount == assets_list_size:
                        everyone_registered_queue.put(True)

                    one_agent_registered_queue.put(True)

            else:
                response['status'] = sim_response['status']
                response['message'] = sim_response['message']

        except requests.exceptions.ConnectionError:
            response['status'] = 6
            response['message'] = 'Simulation is not online.'

    else:
        response['status'] = status
        response['message'] = message

    return json.dumps(response, sort_keys=False)

# ===========================================================================================================================


# ====================================================== DISCONNECTION ======================================================

@socket.on('disconnect_registered_agent')
def disconnect_registered_agent(msg):
    response = {'status': 0, 'result': False, 'message': 'Error.'}

    status, message = controller.do_agent_socket_disconnection(msg)

    if status == 1:
        try:
            sim_response = requests.put(f'http://{base_url}:{simulation_port}/delete_agent',
                                        json={'token': message, 'secret': secret}).json()

            if sim_response['status'] == 1:
                response['status'] = 1
                response['result'] = True
                response['message'] = 'Agent successfully disconnected.'

            else:
                response['message'] = sim_response['message']

        except json.decoder.JSONDecodeError:
            response['message'] = 'An internal error occurred at the simulation.'

        except requests.exceptions.ConnectionError:
            response['message'] = 'Simulation is not online.'

    return json.dumps(response, sort_keys=False)

# ===========================================================================================================================


# ======================================================== STEP LOOP ========================================================

@app.route('/start_step_cycle', methods=['GET'])
def start_step_cycle():
    try:
        valid, message = controller.do_internal_verification(request)

        if not valid:
            return jsonify(message=f'This endpoint can not be accessed. {message}')

        controller.finish_connection_timer()

        sim_response = requests.post(f'http://{base_url}:{simulation_port}/start', json={'secret': secret}).json()

        notify_agents('simulation_started', sim_response)

        multiprocessing.Process(target=step_controller, args=(actions_queue,), daemon=True).start()

    except json.JSONDecodeError:
        return jsonify(message='This endpoint can not be accessed.')

    return jsonify('')


@app.route('/finish_step', methods=['GET'])
def finish_step():
    valid, message = controller.do_internal_verification(request)

    if not valid:
        return jsonify(message=f'This endpoint can not be accessed. {message}')

    try:
        controller.set_processing_actions()
        tokens_actions_list = [*controller.manager.get_actions('agent'), *controller.manager.get_actions('social_asset')]
        sim_response = requests.post(f'http://{base_url}:{simulation_port}/do_actions',
                                     json={'actions': tokens_actions_list, 'secret': secret}).json()

        controller.manager.clear_workers()

        if sim_response['status'] == 0:
            print(sim_response['message'])
            print('An internal error occurred. Shutting down...')
            requests.get(f'http://{base_url}:{simulation_port}/terminate', json={'secret': secret, 'api': True})
            os._exit(1)

        if sim_response['message'] == 'Simulation finished.':
            sim_response = requests.put(f'http://{base_url}:{simulation_port}/restart', json={'secret': secret}).json()

            if sim_response['status'] == 0:
                requests.get(f'http://{base_url}:{simulation_port}/terminate', json={'secret': secret, 'api': True})
                notify_agents('simulation_ended', {'status': 1, 'message': 'Simulation ended all matches.'})
                multiprocessing.Process(target=auto_destruction, daemon=True).start()

            else:
                notify_agents('simulation_started', sim_response)

                controller.set_processing_actions()
                multiprocessing.Process(target=step_controller, args=(actions_queue,), daemon=True).start()

        else:
            notify_agents('action_results', sim_response)

            controller.set_processing_actions()
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

# ===========================================================================================================================


# ==================================================== ACTIONS ENDPOINTS ====================================================

@app.route('/send_action', methods=['POST'])
def send_action():
    response = {'status': 1, 'result': True, 'message': 'Error.'}

    status, message = controller.do_action(request)

    if status != 1:
        response['status'] = status
        response['result'] = False

    else:
        tokens_connected_size = len(controller.manager.get_all('socket'))
        agent_workers_size = len(controller.manager.get_workers('agent'))
        social_asset_workers_size = len(controller.manager.get_workers('social_asset'))

        if tokens_connected_size == agent_workers_size + social_asset_workers_size:
            actions_queue.put(True)

    response['message'] = message

    return jsonify(response)

# ===========================================================================================================================


# ==================================================== AUXILIARY METHODS ====================================================

def notify_agents(event, response):
    for token in controller.manager.get_all('socket'):
        if event == 'simulation_started':
            info = json_formatter.simulation_started_format(response, token)

        elif event == 'simulation_ended':
            info = json_formatter.simulation_ended_format(response)

        elif event == 'action_results':
            info = json_formatter.action_results_format(response, token)

        else:
            exit('Wrong event name. Possible internal errors.')

        room = controller.manager.get(token, 'socket')
        socket.emit(event, json.dumps(info), room=room)


@app.route('/terminate', methods=['GET'])
def terminate():
    valid, message = controller.do_internal_verification(request)

    if not valid:
        return jsonify(message='This endpoint can not be accessed.')

    socket.stop()
    os._exit(0)

    return jsonify('')


def auto_destruction():
    time.sleep(1)
    try:
        requests.get(f'http://{base_url}:{api_port}/terminate', json={'secret': secret})
    except requests.exceptions.ConnectionError:
        pass

# ===========================================================================================================================


if __name__ == '__main__':
    app.config['SECRET_KEY'] = secret
    app.config['JSON_SORT_KEYS'] = False
    print(f'API: Serving on http://{base_url}:{api_port}')

    socket.run(app=app, host=base_url, port=api_port)
