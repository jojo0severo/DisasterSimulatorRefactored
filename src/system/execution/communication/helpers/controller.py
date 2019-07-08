import jwt
import json
import time
from src.system.execution.communication.controllers.manager import Manager


class Controller:
    def __init__(self, agents_amount, social_assets_amount, time_limit, internal_secret):
        self.manager = Manager()
        self.start_time = None
        self.time_limit = int(time_limit)
        self.started = False
        self.terminated = False
        self.agents_amount = int(agents_amount)
        self.social_assets_amount = int(social_assets_amount)
        self.secret = internal_secret
        self.processing_actions = False

    def set_started(self):
        if self.started:
            self.started = False
        else:
            self.started = True

    def set_processing_actions(self):
        if self.processing_actions:
            self.processing_actions = False
        else:
            self.processing_actions = True

    def start_timer(self):
        self.start_time = time.time()

    def finish_connection_timer(self):
        self.start_time -= self.time_limit

    def do_internal_verification(self, request):
        try:
            message = request.get_json(force=True)

            if 'secret' in message:
                if self.check_secret(self.secret, message['secret']):
                    return 1, 'Ok.'

                return 3, 'Different secret provided.'

            return 4, 'Message does not contain secret.'

        except json.JSONDecodeError:
            return 2, 'JSON format error.'

    def do_agent_connection(self, request):
        try:
            obj = json.loads(request.get_json(force=True))

            if not self.started:
                return 5, 'Simulation has not started.'

            if self.terminated:
                return 5, 'Simulation already terminated.'

            if self.start_time + self.time_limit >= time.time():
                return 5, 'Connection time ended.'

            if len(self.manager.get_all('agent')) == self.agents_amount:
                return 5, 'All possible agents already connected.'

            if not isinstance(obj, dict):
                return 4, 'Object is not a dictionary.'

            token = jwt.encode(obj, 'secret', algorithm='HS256').decode('utf-8')

            if self.manager.get(token, 'agent') is not None:
                return 5, 'Agent already connected.'

            if not self.manager.add(token, obj, 'agent'):
                return 0, 'Error while adding token.'

            return 1, token

        except json.JSONDecodeError:
            return 2, 'Object format is not JSON.'

        except Exception as e:
            return 0, f'Unknown error: {str(e)}'

    def do_social_asset_connection(self, request):
        try:
            obj = json.loads(request.get_json(force=True))

            if not self.started:
                return 5, 'Simulation has not started.'

            if self.terminated:
                return 5, 'Simulation already terminated.'

            if len(self.manager.get_all('social_asset')) == self.social_assets_amount:
                return 5, 'All possible social assets already connected.'

            if not isinstance(obj, dict):
                return 4, 'Object is not a dictionary.'

            token = jwt.encode(obj, 'secret', algorithm='HS256').decode('utf-8')

            if self.manager.get(token, 'social_asset') is not None:
                return 5, 'Social asset already connected.'

            if not self.manager.add(token, obj, 'social_asset'):
                return 0, 'Error while adding token.'

            return 1, token

        except json.JSONDecodeError:
            return 2, 'Object format is not JSON.'

        except Exception as e:
            return 0, f'Unknown error: {str(e)}'

    def do_agent_registration(self, request):
        try:
            obj = json.loads(request.get_json(force=True))

            if not self.started:
                return 5, 'Simulation has not started.'

            if self.terminated:
                return 5, 'Simulation already terminated.'

            if self.start_time + self.time_limit >= time.time():
                return 5, 'Connection time ended.'

            if not isinstance(obj, dict):
                return 4, 'Object is not a dictionary.'

            if 'token' not in obj:
                return 3, 'Object does not contain "token" as key.'

            agent = self.manager.get(obj['token'], 'agent')
            if agent is None:
                return 5, 'Agent was not connected.'

            if agent.registered:
                return 5, 'Agent already registered.'

            if not self.manager.edit(obj['token'], 'registered', True, 'agent'):
                return 0, 'Error while editing token.'

            return 1, 'Agent registered.'

        except json.JSONDecodeError:
            return 2, 'Object format is not JSON.'

        except Exception as e:
            return 0, f'Unknown error: {str(e)}'

    def do_social_asset_registration(self, request):
        try:
            obj = json.loads(request.get_json(force=True))

            if not self.started:
                return 5, 'Simulation has not started.'

            if self.terminated:
                return 5, 'Simulation already terminated.'

            if not isinstance(obj, dict):
                return 4, 'Object is not a dictionary.'

            if 'token' not in obj:
                return 3, 'Object does not contain "token" as key.'

            social_asset = self.manager.get(obj['token'], 'social_asset')
            if social_asset is None:
                return 5, 'Social asset was not connected.'

            if social_asset.registered:
                return 5, 'Social asset already registered.'

            if not self.manager.edit(obj['token'], 'registered', True, 'social_asset'):
                return 0, 'Error while editing token.'

            return 1, 'Social asset registered.'

        except json.JSONDecodeError:
            return 2, 'Object format is not JSON.'

        except Exception as e:
            return 0, f'Unknown error: {str(e)}'

    def do_agent_socket_connection(self, request, msg):
        try:
            obj = json.loads(msg)

            if not self.started:
                return 5, 'Simulation has not started.'

            if self.terminated:
                return 5, 'Simulation already terminated.'

            if self.start_time + self.time_limit >= time.time():
                return 5, 'Connection time ended.'

            if not isinstance(obj, dict):
                return 4, 'Object is not a dictionary.'

            if 'token' not in obj:
                return 3, 'Object does not contain "token" as key.'

            agent = self.manager.get(obj['token'], 'agent')
            if agent is None:
                return 5, 'Agent was not connected.'

            if not agent.registered:
                return 5, 'Agent was not registered.'

            if self.manager.get(obj['token'], 'socket') is not None:
                return 5, 'Socket already registered.'

            if not self.manager.add(obj['token'], request.sid, 'socket'):
                return 0, 'Error while adding token.'

            return 1, obj['token']

        except json.JSONDecodeError:
            return 2, 'Object format is not JSON.'

        except Exception as e:
            return 0, f'Unknown error: {str(e)}'

    def do_social_asset_socket_connection(self, request, msg):
        try:
            obj = json.loads(msg)

            if not self.started:
                return 5, 'Simulation has not started.'

            if self.terminated:
                return 5, 'Simulation already terminated.'

            if not isinstance(obj, dict):
                return 4, 'Object is not a dictionary.'

            if 'token' not in obj:
                return 3, 'Object does not contain "token" as key.'

            social_asset = self.manager.get(obj['token'], 'agent')
            if social_asset is None:
                return 5, 'Social asset was not connected.'

            if not social_asset.registered:
                return 5, 'Social asset was not registered.'

            if self.manager.get(obj['token'], 'socket') is not None:
                return 5, 'Socket already registered.'

            if not self.manager.add(obj['token'], request.sid, 'socket'):
                return 0, 'Error while adding token.'

            return 1, obj['token']

        except json.JSONDecodeError:
            return 2, 'Object format is not JSON.'

        except Exception as e:
            return 0, f'Unknown error: {str(e)}'

    def do_agent_socket_disconnection(self, msg):
        try:
            obj = json.loads(msg)

            if not self.started:
                return 5, 'Simulation has not started.'

            if self.terminated:
                return 5, 'Simulation already terminated.'

            if not isinstance(obj, dict):
                return 4, 'Object is not a dictionary.'

            if 'token' not in obj:
                return 3, 'Object does not contain "token" as key.'

            if self.manager.get(obj['token'], 'socket') is None:
                return 5, 'Socket was not connected.'

            if not self.manager.remove(obj['token'], 'agent'):
                return 0, 'Error while removing token.'

            return 1, obj['token']

        except json.JSONDecodeError:
            return 2, 'Object format is not JSON.'

        except Exception as e:
            return 0, f'Unknown error: {str(e)}'

    def do_social_asset_socket_disconnection(self, msg):
        try:
            obj = json.loads(msg)

            if not self.started:
                return 5, 'Simulation has not started.'

            if self.terminated:
                return 5, 'Simulation already terminated.'

            if not isinstance(obj, dict):
                return 4, 'Object is not a dictionary.'

            if 'token' not in obj:
                return 3, 'Object does not contain "token" as key.'

            if self.manager.get(obj['token'], 'socket') is None:
                return 5, 'Socket was not connected.'

            if not self.manager.remove(obj['token'], 'social_asset'):
                return 0, 'Error while removing token.'

            return 1, obj['token']

        except json.JSONDecodeError:
            return 2, 'Object format is not JSON.'

        except Exception as e:
            return 0, f'Unknown error: {str(e)}'

    def do_action(self, request):
        try:
            obj = json.loads(request.get_json(force=True))

            if not self.started:
                return 5, 'Simulation has not started.'

            if self.terminated:
                return 5, 'Simulation already terminated.'

            if self.processing_actions:
                return 5, 'Simulation is processing previous actions.'

            if self.start_time + self.time_limit < time.time():
                return 5, 'Simulation still receiving agent connections.'

            if not isinstance(obj, dict):
                return 4, 'Object is not a dictionary.'

            if 'agent' not in obj:
                return 3, 'Object does not contain "agent" as key.'

            if 'token' not in obj:
                return 3, 'Object does not contain "token" as key.'

            if 'action' not in obj:
                return 3, 'Object does not contain "action" as key.'

            if 'parameters' not in obj:
                return 3, 'Object does not contain "parameters" as key.'

            kind = 'social_asset' if not obj['agent'] else 'agent'
            object_found = self.manager.get(obj['token'], kind)
            if object_found is None:
                return 5, 'Object was not connected.'

            if not object_found.registered:
                return 5, 'Object was not registered.'

            if object_found.worker:
                return 5, 'Object already sent an action.'

            if self.manager.get(obj['token'], 'socket') is None:
                return 5, 'Socket was not connect.'

            if not self.manager.edit(obj['token'], 'action_name', obj['action'], kind):
                return 0, 'Error while editing action.'

            if not self.manager.edit(obj['token'], 'action_params', obj['parameters'], kind):
                return 0, 'Error while editing parameters.'

            if not self.manager.edit(obj['token'], 'worker', True, kind):
                return 0, 'Error while editing working state.'

            return 1, 'Action successfully sent.'

        except json.JSONDecodeError:
            return 2, 'Objector format is not JSON.'

    @staticmethod
    def check_secret(secret, other_secret):
        if len(other_secret) != len(secret):
            return False

        for saved_letter, other_letter in zip(list(secret), list(other_secret)):
            if saved_letter != other_letter:
                return False

        return True
