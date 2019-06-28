import os
import sys
import time
import requests
import multiprocessing
from flask import request, jsonify
from flask import Flask
from flask_cors import CORS
from src.simulation_engine.json_formatter import JsonFormatter
from waitress import serve

config_path, base_url, simulation_port, api_port, secret = sys.argv[1:]


app = Flask(__name__)
formatter = JsonFormatter(config_path)


@app.route('/start', methods=['POST'])
def start():
    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    return jsonify(formatter.start())


@app.route('/register_agent', methods=['POST'])
def register_agent():
    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    return jsonify(formatter.connect_agent(message['token']))


@app.route('/delete_agent', methods=['PUT'])
def delete_agent():
    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    return jsonify(formatter.disconnect_agent(message['token']))


@app.route('/do_actions', methods=['POST'])
def do_actions():
    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    return jsonify(formatter.do_step(message['actions']))


@app.route('/restart', methods=['PUT'])
def restart():
    global formatter

    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    response = formatter.log()

    if response['status'] == 1:
        formatter.regenerate()

    return jsonify(response)


@app.route('/terminate', methods=['GET'])
def finish():
    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    if 'api' in message and message['api']:
        formatter.save_logs()
        multiprocessing.Process(target=auto_destruction, daemon=True).start()

    elif 'api' in message and not message['api']:
        os._exit(0)

    return jsonify('')


def auto_destruction():
    time.sleep(1)
    try:
        requests.get(f'http://{base_url}:{simulation_port}/terminate', json={'secret': secret, 'api': False})
    except requests.exceptions.ConnectionError:
        pass


if __name__ == '__main__':
    app.debug = False
    app.config['SECRET_KEY'] = secret
    app.config['JSON_SORT_KEYS'] = False

    CORS(app)

    print('Simulation', end=': ')

    try:
        if requests.post(f'http://{base_url}:{api_port}/start_connections', json={'secret': secret, 'back': 0}):
            serve(app, host=base_url, port=simulation_port)
        else:
            print('Errors occurred during startup.')
    except requests.exceptions.ConnectionError:
        print('API is not online.')



