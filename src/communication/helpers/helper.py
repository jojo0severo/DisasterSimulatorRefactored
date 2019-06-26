import json
from src.communication.controllers.controller import Controller


class Helper:
    def __init__(self, matches, agents_amount, first_step_time, secret):
        self.controller = Controller(matches, int(agents_amount), int(first_step_time), secret)

    def burn(self, matches, agents_amount, first_step_time):
        self.controller.burn(matches, int(agents_amount), int(first_step_time))

    def do_internal_verification(self, request):
        try:
            message = request.get_json(force=True)

            if 'secret' in message:
                if message['secret'] == self.controller.secret:
                    return False, message

                return True, 'Different secret provided.'

            return True, 'Message does not contain secret.'

        except json.JSONDecodeError:
            return True, 'JSON format error.'

    def do_connection_verifications(self, request_object):
        error = True

        try:
            if not self.controller.started:
                message = 'Simulation was not started.'

            elif self.controller.terminated:
                message = 'Simulation already finished'

            elif not self.controller.check_timer():
                message = 'Connection time ended.'

            elif not self.controller.check_population():
                message = 'All possible agents already are connected.'

            elif self.controller.check_agent_connected(request_object.get_json(force=True)):
                message = 'Agent already is connected.'

            else:
                message = 'Ok.'
                error = False

        except json.JSONDecodeError:
            message = 'Wrong JSON format or information.'

        return error, message

    def do_validation_verifications(self, request_object):
        error = True
        try:
            if not self.controller.started:
                message = 'Simulation has not started.'

            elif self.controller.terminated:
                message = 'Simulation already finished.'

            elif not self.controller.check_timer():
                message = 'Connection time ended.'

            elif not self.controller.check_agent_token(request_object.get_json(force=True)):
                message = 'Agent not connected or invalid Token.'

            elif self.controller.check_token_registered(request_object.get_json(force=True)):
                message = 'Agent already registered.'

            else:
                message = 'Ok.'
                error = False

        except json.JSONDecodeError:
            message = 'Wrong JSON format or information.'

        return error, message

    def do_socket_connection_verifications(self, socket_message):
        error = True
        try:
            token = json.loads(socket_message)['token']
            if not self.controller.check_timer():
                message = 'Can no longer connect due to time.'

            elif not self.controller.check_agent_token(json.loads(token)):
                message = 'Agent not connected or invalid Token.'

            elif not self.controller.check_token_registered(token):
                message = 'Agent was not registered.'

            else:
                if self.controller.check_socket_connected(token):
                    message = 'Socket already connected.'

                else:
                    message = 'Ok.'
                    error = False

        except json.decoder.JSONDecodeError:
            message = 'Wrong JSON format or information.'

        return error, message

    def do_socket_disconnection_verifications(self, socket_message):
        error = True

        try:
            token = json.loads(socket_message)['token']
            if not self.controller.check_socket_connected(token):
                message = 'Agent was not connected.'

            else:
                message = 'Ok.'
                error = False

        except KeyError:
            message = 'Token was not sent.'

        except json.decoder.JSONDecodeError:
            message = 'Wrong JSON format or information.'

        return error, message

    def do_action_verifications(self, request_object):
        error = True

        if self.controller.processing_actions:
            message = 'Simulation is processing step actions.'

        elif not self.controller.started:
            message = 'Simulation was not started.'

        elif self.controller.terminated:
            message = 'Simulation already finished.'

        elif self.controller.check_timer():
            message = 'Simulation still receiving connections.'

        else:
            try:
                message = request_object.get_json(force=True)
                token = message['token']
                _ = message['action']
                _ = message['parameters']

                if not self.controller.check_socket_connected(token):
                    message = 'Agent Socket was not connect.'

                elif not self.controller.check_agent_token(token):
                    message = 'Agent not connected.'

                elif not self.controller.check_token_registered(token):
                    message = 'Agent not registered.'

                elif self.controller.check_agent_action(token):
                    message = 'The agent has already sent a job'

                else:
                    message = 'Ok.'
                    error = False

            except TypeError as t:
                message = 'TypeError: ' + str(t)

            except KeyError as k:
                message = 'KeyError: ' + str(k)

        return error, message
